"""
Policy Agent
─────────────
Uses RAG (FAISS + Gemini embeddings) over insurance policy documents
to determine coverage, deductibles, and supporting clauses.
"""

import json
import logging
import pickle
from pathlib import Path
from typing import Any

import numpy as np

from app.agents.base import BaseAgent
from app.core.config import settings
from app.models.schemas import (
    GraphState,
    PolicyAgentOutput,
    PolicyClause,
)

logger = logging.getLogger(__name__)

POLICY_PROMPT = """
You are an expert insurance policy analyst.
Using the retrieved policy clauses below, determine coverage for this claim.

Policy Number: {policy_number}
Vehicle: {vehicle_model}
Accident Description: {accident_description}
Damage Summary: {damage_summary}

Retrieved Policy Clauses:
{retrieved_clauses}

Return ONLY a valid JSON object:
{{
  "policy_number": "{policy_number}",
  "policy_type": "<Basic|Standard|Premium|Comprehensive>",
  "damage_covered": <true|false>,
  "coverage_percentage": <0 to 100>,
  "deductible_amount": <float in INR>,
  "max_payout": <float in INR>,
  "supporting_clauses": [
    {{
      "clause_id": "<e.g. Section 4.2>",
      "clause_text": "<relevant clause text>",
      "relevance_score": <0.0 to 1.0>
    }}
  ],
  "exclusions_triggered": ["<list any policy exclusions that apply>"],
  "coverage_notes": "<explanation of coverage decision>"
}}

Be precise about deductible and max payout amounts found in the clauses.
If not covered, explain why in coverage_notes.
"""


class FAISSIndex:
    """Lightweight FAISS wrapper that stores docs + metadata alongside the index."""

    def __init__(self, index_path: str):
        self.index_path = Path(index_path)
        self.index = None
        self.documents: list[str] = []
        self.metadatas: list[dict] = []

    def load(self) -> bool:
        """Load index from disk. Returns True if successful."""
        idx_file = self.index_path / "index.faiss"
        docs_file = self.index_path / "docs.pkl"
        if not idx_file.exists() or not docs_file.exists():
            return False
        try:
            import faiss
            self.index = faiss.read_index(str(idx_file))
            with open(docs_file, "rb") as f:
                data = pickle.load(f)
                self.documents = data["documents"]
                self.metadatas = data["metadatas"]
            return True
        except Exception as e:
            logger.warning("Failed to load FAISS index: %s", e)
            return False

    def search(self, query_embedding: list[float], k: int = 5) -> list[tuple[str, dict, float]]:
        """Return top-k (document, metadata, score) tuples."""
        if self.index is None or len(self.documents) == 0:
            return []
        vec = np.array([query_embedding], dtype=np.float32)
        distances, indices = self.index.search(vec, min(k, len(self.documents)))
        results = []
        for dist, idx in zip(distances[0], indices[0]):
            if idx >= 0:
                results.append((self.documents[idx], self.metadatas[idx], float(dist)))
        return results


class PolicyAgent(BaseAgent):
    """RAG-based policy coverage analysis agent using FAISS."""

    def __init__(self) -> None:
        super().__init__()
        self._index: FAISSIndex | None = None

    def _get_index(self) -> FAISSIndex:
        if self._index is None:
            self._index = FAISSIndex(
                index_path=str(Path(settings.chroma_persist_dir) / "policies")
            )
            loaded = self._index.load()
            if not loaded:
                logger.warning("Policy FAISS index not found — RAG will be text-only")
        return self._index

    def _embed(self, text: str) -> list[float]:
        """Get Gemini text embedding for a query string."""
        import google.generativeai as genai
        result = genai.embed_content(
            model="models/text-embedding-004",
            content=text,
            task_type="retrieval_query",
        )
        return result["embedding"]

    def run(self, state: GraphState) -> GraphState:
        self.logger.info("PolicyAgent starting for claim %s", state.claim_id)
        try:
            retrieved_clauses = self._retrieve(state)

            prompt = POLICY_PROMPT.format(
                policy_number=state.policy_number,
                vehicle_model=state.vehicle_model,
                accident_description=state.accident_description,
                damage_summary=self._damage_summary(state),
                retrieved_clauses=retrieved_clauses,
            )

            raw_response = self._call_gemini(prompt)
            data = self._extract_json(raw_response)
            state.policy_output = self._parse_output(data)

            self.logger.info(
                "PolicyAgent complete — covered=%s, type=%s",
                state.policy_output.damage_covered,
                state.policy_output.policy_type,
            )
        except Exception as exc:
            self.logger.error("PolicyAgent failed: %s", exc, exc_info=True)
            state.errors.append(f"PolicyAgent error: {str(exc)}")
            state.policy_output = self._fallback_output(state.policy_number)

        return state

    # ──────────────────────────────────────────
    #  Helpers
    # ──────────────────────────────────────────

    def _retrieve(self, state: GraphState) -> str:
        """Try FAISS retrieval; fall back to loading raw markdown if index missing."""
        query = self._build_query(state)
        index = self._get_index()

        if index.index is not None and len(index.documents) > 0:
            try:
                embedding = self._embed(query)
                results = index.search(embedding, k=5)
                if results:
                    lines = []
                    for doc, meta, score in results:
                        clause_id = meta.get("clause_id", "Clause")
                        lines.append(f"[{clause_id}]: {doc}")
                    return "\n\n".join(lines)
            except Exception as e:
                logger.warning("FAISS retrieval failed, using fallback: %s", e)

        # Fallback: read policy markdown files directly
        return self._load_policy_text(state.policy_number)

    def _build_query(self, state: GraphState) -> str:
        damage_parts = []
        if state.damage_assessment_output:
            damage_parts = [a.part_name for a in state.damage_assessment_output.assessments]
        return (
            f"Coverage for {state.vehicle_model} collision damage. "
            f"Damaged parts: {', '.join(damage_parts) or 'unknown'}. "
            f"Accident: {state.accident_description}"
        )

    def _load_policy_text(self, policy_number: str) -> str:
        """Load policy markdown based on policy number prefix."""
        policy_dir = Path(settings.rag_policies_dir)
        prefix_map = {
            "POL-BASIC": "policy_basic.md",
            "POL-STANDARD": "policy_standard.md",
            "POL-PREMIUM": "policy_premium.md",
            "POL-COMP": "policy_comprehensive.md",
        }
        for prefix, filename in prefix_map.items():
            if policy_number.upper().startswith(prefix):
                policy_file = policy_dir / filename
                if policy_file.exists():
                    with open(policy_file, "r", encoding="utf-8") as f:
                        content = f.read()
                    # Return first 3000 chars to avoid token overflow
                    return content[:3000]

        # Return all policies if we can't match
        all_text = []
        for md_file in sorted(policy_dir.glob("policy_*.md")):
            with open(md_file, "r", encoding="utf-8") as f:
                all_text.append(f.read()[:1000])
        return "\n\n---\n\n".join(all_text) if all_text else (
            "No policy documents found. Use general insurance knowledge."
        )

    def _damage_summary(self, state: GraphState) -> str:
        if not state.damage_assessment_output:
            return state.accident_description
        da = state.damage_assessment_output
        parts = [a.part_name for a in da.assessments]
        return (
            f"{da.overall_damage_category}. "
            f"Parts affected: {', '.join(parts)}. "
            f"Towing required: {da.requires_towing}."
        )

    def _parse_output(self, data: dict[str, Any]) -> PolicyAgentOutput:
        supporting = [
            PolicyClause(
                clause_id=c.get("clause_id", "Unknown"),
                clause_text=c.get("clause_text", ""),
                relevance_score=float(c.get("relevance_score", 0.7)),
            )
            for c in data.get("supporting_clauses", [])
        ]
        return PolicyAgentOutput(
            policy_number=data.get("policy_number", "UNKNOWN"),
            policy_type=data.get("policy_type", "Standard"),
            damage_covered=bool(data.get("damage_covered", True)),
            coverage_percentage=float(data.get("coverage_percentage", 80.0)),
            deductible_amount=float(data.get("deductible_amount", 5000.0)),
            max_payout=float(data.get("max_payout", 100000.0)),
            supporting_clauses=supporting,
            exclusions_triggered=data.get("exclusions_triggered", []),
            coverage_notes=data.get("coverage_notes", ""),
        )

    def _fallback_output(self, policy_number: str) -> PolicyAgentOutput:
        return PolicyAgentOutput(
            policy_number=policy_number,
            policy_type="Standard",
            damage_covered=True,
            coverage_percentage=75.0,
            deductible_amount=5000.0,
            max_payout=150000.0,
            supporting_clauses=[],
            exclusions_triggered=[],
            coverage_notes="Policy analysis performed in fallback mode — manual review required",
        )
