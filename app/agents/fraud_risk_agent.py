"""
Fraud Risk Agent
─────────────────
Detects claim inconsistencies and produces a LOW / MEDIUM / HIGH fraud
risk score backed by explicit reasoning.
"""

import json
import logging
from pathlib import Path
from typing import Any

from app.agents.base import BaseAgent
from app.models.schemas import (
    FraudIndicator,
    FraudRisk,
    FraudRiskOutput,
    GraphState,
)

logger = logging.getLogger(__name__)

FRAUD_PROMPT = """
You are a senior insurance fraud investigator with 15+ years of experience.
Analyse this claim for potential fraud indicators.

CLAIM DETAILS:
Policy Number: {policy_number}
Vehicle: {vehicle_model}
Accident Description: {accident_description}

VISION FINDINGS:
{vision_summary}

DAMAGE ASSESSMENT:
{damage_summary}

REPAIR ESTIMATE:
Total estimated cost: ₹{repair_total:,.0f}

POLICY COVERAGE:
Policy type: {policy_type}
Coverage: {coverage_pct}%
Max payout: ₹{max_payout:,.0f}

FRAUD RULES & PATTERNS:
{fraud_rules}

Analyse for these fraud patterns:
1. Damage inconsistencies (description vs image mismatch)
2. Pre-existing damage claimed as new
3. Inflated repair estimates (cost vs damage severity mismatch)
4. Policy timing (recently purchased policy with major claim)
5. Accident description vagueness or implausibility
6. Parts claimed that don't match accident type
7. Estimate significantly exceeds market rates

Return ONLY a valid JSON object:
{{
  "fraud_score": <0.0 to 1.0>,
  "fraud_risk_level": "<LOW|MEDIUM|HIGH>",
  "indicators": [
    {{
      "indicator": "<indicator name>",
      "description": "<what was found>",
      "weight": <0.0 to 1.0>
    }}
  ],
  "inconsistencies_found": ["<list of specific inconsistencies>"],
  "reasoning": "<detailed explanation of fraud assessment>",
  "recommendation": "<what the investigator recommends>"
}}

Scoring guide:
- 0.0 - 0.35: LOW — claim appears legitimate
- 0.35 - 0.65: MEDIUM — some concerns, needs review
- 0.65 - 1.0: HIGH — strong fraud indicators present
"""


class FraudRiskAgent(BaseAgent):
    """Detects fraud risk indicators in insurance claims."""

    def __init__(self) -> None:
        super().__init__()
        self._fraud_rules: list[dict[str, Any]] | None = None

    def _load_fraud_rules(self) -> list[dict[str, Any]]:
        if self._fraud_rules is None:
            rules_path = Path("rag/fraud_rules/fraud_rules.json")
            if rules_path.exists():
                with open(rules_path, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    self._fraud_rules = data.get("rules", [])
            else:
                self._fraud_rules = []
        return self._fraud_rules

    def run(self, state: GraphState) -> GraphState:
        self.logger.info("FraudRiskAgent starting for claim %s", state.claim_id)
        try:
            rules = self._load_fraud_rules()
            rules_text = self._format_rules(rules)

            prompt = FRAUD_PROMPT.format(
                policy_number=state.policy_number,
                vehicle_model=state.vehicle_model,
                accident_description=state.accident_description,
                vision_summary=self._vision_summary(state),
                damage_summary=self._damage_summary(state),
                repair_total=self._repair_total(state),
                policy_type=state.policy_output.policy_type if state.policy_output else "Unknown",
                coverage_pct=state.policy_output.coverage_percentage if state.policy_output else 0,
                max_payout=state.policy_output.max_payout if state.policy_output else 0,
                fraud_rules=rules_text,
            )

            raw_response = self._call_gemini(prompt)
            data = self._extract_json(raw_response)
            state.fraud_risk_output = self._parse_output(data)

            self.logger.info(
                "FraudRiskAgent complete — risk=%s, score=%.2f",
                state.fraud_risk_output.fraud_risk_level,
                state.fraud_risk_output.fraud_score,
            )
        except Exception as exc:
            self.logger.error("FraudRiskAgent failed: %s", exc, exc_info=True)
            state.errors.append(f"FraudRiskAgent error: {str(exc)}")
            state.fraud_risk_output = self._fallback_output()

        return state

    # ──────────────────────────────────────────
    #  Helpers
    # ──────────────────────────────────────────

    def _vision_summary(self, state: GraphState) -> str:
        if not state.vision_output:
            return "Not available"
        parts = [f"{p.part_name} ({p.severity})" for p in state.vision_output.damaged_parts]
        return (
            f"Accident type: {state.vision_output.accident_type}\n"
            f"Overall severity: {state.vision_output.overall_severity}\n"
            f"Damaged parts: {', '.join(parts)}"
        )

    def _damage_summary(self, state: GraphState) -> str:
        if not state.damage_assessment_output:
            return "Not available"
        da = state.damage_assessment_output
        return (
            f"Category: {da.overall_damage_category}\n"
            f"Parts damaged: {da.total_parts_damaged}\n"
            f"Towing required: {da.requires_towing}\n"
            f"Drivable: {da.vehicle_drivable}"
        )

    def _repair_total(self, state: GraphState) -> float:
        if state.repair_estimation_output:
            return state.repair_estimation_output.grand_total
        return 0.0

    def _format_rules(self, rules: list[dict[str, Any]]) -> str:
        if not rules:
            return "Apply general fraud detection principles."
        return "\n".join(
            f"- [{r.get('id', 'R?')}] {r.get('name', '')}: {r.get('description', '')}"
            for r in rules[:20]
        )

    def _parse_output(self, data: dict[str, Any]) -> FraudRiskOutput:
        indicators = [
            FraudIndicator(
                indicator=i["indicator"],
                description=i["description"],
                weight=float(i.get("weight", 0.5)),
            )
            for i in data.get("indicators", [])
        ]
        return FraudRiskOutput(
            fraud_score=float(data.get("fraud_score", 0.2)),
            fraud_risk_level=FraudRisk(data.get("fraud_risk_level", "LOW")),
            indicators=indicators,
            inconsistencies_found=data.get("inconsistencies_found", []),
            reasoning=data.get("reasoning", ""),
            recommendation=data.get("recommendation", ""),
        )

    def _fallback_output(self) -> FraudRiskOutput:
        return FraudRiskOutput(
            fraud_score=0.3,
            fraud_risk_level=FraudRisk.LOW,
            indicators=[],
            inconsistencies_found=[],
            reasoning="Fraud analysis could not be completed — defaulting to LOW risk",
            recommendation="Manual review recommended",
        )
