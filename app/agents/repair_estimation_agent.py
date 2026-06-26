"""
Repair Estimation Agent
────────────────────────
Looks up the repair catalog (ChromaDB) and uses Gemini to produce
itemised parts + labour cost estimates.
"""

import json
import logging
from pathlib import Path
from typing import Any

from app.agents.base import BaseAgent
from app.core.config import settings
from app.models.schemas import (
    GraphState,
    PartEstimate,
    RepairAction,
    RepairEstimationOutput,
)

logger = logging.getLogger(__name__)

REPAIR_PROMPT = """
You are an expert automobile repair cost estimator for the Indian market.
Use the repair catalog data below plus your expertise to estimate repair costs.

Vehicle: {vehicle_model}
Parts to estimate:
{parts_list}

Repair Catalog Reference Data:
{catalog_data}

Return ONLY a valid JSON object:
{{
  "vehicle_model": "{vehicle_model}",
  "estimates": [
    {{
      "part_name": "<part name>",
      "action": "<REPAIR|REPLACE|MONITOR>",
      "parts_cost": <float INR>,
      "labour_cost": <float INR>,
      "total_cost": <float INR>,
      "vendor_note": "<e.g. OEM part recommended>"
    }}
  ],
  "subtotal_parts": <float>,
  "subtotal_labour": <float>,
  "grand_total": <float>,
  "currency": "INR",
  "estimation_confidence": <0.0 to 1.0>,
  "notes": "<any estimation notes>"
}}

Pricing guidelines (INR):
- Minor cosmetic repair: ₹2,000 - ₹8,000
- Bumper replacement: ₹12,000 - ₹25,000
- Headlight replacement: ₹6,000 - ₹18,000
- Door panel replacement: ₹15,000 - ₹35,000
- Bonnet replacement: ₹18,000 - ₹45,000
- Windshield replacement: ₹8,000 - ₹25,000
- Labour rate: ₹500 - ₹1,500 per hour
- Always add 18% GST to parts cost in vendor_note if applicable
"""


class RepairEstimationAgent(BaseAgent):
    """Estimates repair costs using a catalog and Gemini."""

    def __init__(self) -> None:
        super().__init__()
        self._catalog_data: dict[str, Any] | None = None

    def _load_catalog(self) -> dict[str, Any]:
        """Load the repair cost catalog from JSON file."""
        if self._catalog_data is None:
            catalog_path = Path("data/repair_costs.json")
            if catalog_path.exists():
                with open(catalog_path, "r", encoding="utf-8") as f:
                    self._catalog_data = json.load(f)
            else:
                self._catalog_data = {}
        return self._catalog_data

    def run(self, state: GraphState) -> GraphState:
        self.logger.info("RepairEstimationAgent starting for claim %s", state.claim_id)
        try:
            catalog = self._load_catalog()
            parts_list = self._get_parts_list(state)
            catalog_data = self._lookup_catalog(catalog, state.vehicle_model, parts_list)

            prompt = REPAIR_PROMPT.format(
                vehicle_model=state.vehicle_model,
                parts_list="\n".join(
                    f"  - {p['part_name']}: {p['action']}" for p in parts_list
                ),
                catalog_data=json.dumps(catalog_data, indent=2),
            )

            raw_response = self._call_gemini(prompt)
            data = self._extract_json(raw_response)
            state.repair_estimation_output = self._parse_output(data)

            self.logger.info(
                "RepairEstimationAgent complete — total=₹%.0f",
                state.repair_estimation_output.grand_total,
            )
        except Exception as exc:
            self.logger.error("RepairEstimationAgent failed: %s", exc, exc_info=True)
            state.errors.append(f"RepairEstimationAgent error: {str(exc)}")
            state.repair_estimation_output = self._fallback_output(state)

        return state

    # ──────────────────────────────────────────
    #  Helpers
    # ──────────────────────────────────────────

    def _get_parts_list(self, state: GraphState) -> list[dict[str, str]]:
        if state.damage_assessment_output:
            return [
                {"part_name": a.part_name, "action": a.recommended_action.value}
                for a in state.damage_assessment_output.assessments
            ]
        if state.vision_output:
            return [
                {"part_name": p.part_name, "action": "REPAIR"}
                for p in state.vision_output.damaged_parts
            ]
        return [{"part_name": "General damage", "action": "REPAIR"}]

    def _lookup_catalog(
        self, catalog: dict[str, Any], vehicle_model: str, parts: list[dict[str, str]]
    ) -> dict[str, Any]:
        """Find closest matching vehicle and parts in catalog."""
        result: dict[str, Any] = {}

        # Fuzzy vehicle match
        model_key = None
        vehicle_lower = vehicle_model.lower()
        for key in catalog.get("vehicles", {}).keys():
            if any(word in key.lower() for word in vehicle_lower.split()):
                model_key = key
                break

        if model_key:
            vehicle_data = catalog["vehicles"][model_key]
            for p in parts:
                part_lower = p["part_name"].lower()
                for part_key, cost_data in vehicle_data.items():
                    if any(word in part_key.lower() for word in part_lower.split()):
                        result[p["part_name"]] = cost_data

        return result

    def _parse_output(self, data: dict[str, Any]) -> RepairEstimationOutput:
        estimates = [
            PartEstimate(
                part_name=e["part_name"],
                action=RepairAction(e["action"]),
                parts_cost=float(e["parts_cost"]),
                labour_cost=float(e["labour_cost"]),
                total_cost=float(e["total_cost"]),
                vendor_note=e.get("vendor_note", ""),
            )
            for e in data.get("estimates", [])
        ]
        return RepairEstimationOutput(
            vehicle_model=data.get("vehicle_model", "Unknown"),
            estimates=estimates,
            subtotal_parts=float(data.get("subtotal_parts", 0)),
            subtotal_labour=float(data.get("subtotal_labour", 0)),
            grand_total=float(data.get("grand_total", 0)),
            currency=data.get("currency", "INR"),
            estimation_confidence=float(data.get("estimation_confidence", 0.8)),
            notes=data.get("notes", ""),
        )

    def _fallback_output(self, state: GraphState) -> RepairEstimationOutput:
        parts = self._get_parts_list(state)
        estimates = []
        for p in parts:
            estimates.append(
                PartEstimate(
                    part_name=p["part_name"],
                    action=RepairAction(p["action"]),
                    parts_cost=15000.0,
                    labour_cost=3000.0,
                    total_cost=18000.0,
                    vendor_note="Fallback estimate — actual quote required",
                )
            )
        total = sum(e.total_cost for e in estimates)
        return RepairEstimationOutput(
            vehicle_model=state.vehicle_model,
            estimates=estimates,
            subtotal_parts=sum(e.parts_cost for e in estimates),
            subtotal_labour=sum(e.labour_cost for e in estimates),
            grand_total=total,
            currency="INR",
            estimation_confidence=0.3,
            notes="Fallback estimates — physical inspection required for accurate quotes",
        )
