"""
Decision Agent
───────────────
Synthesises all upstream agent outputs and produces a final
APPROVE / REJECT / HUMAN_REVIEW decision with reasoning.
"""

import logging
from typing import Any

from app.agents.base import BaseAgent
from app.models.schemas import (
    ClaimDecision,
    DecisionAgentOutput,
    FraudRisk,
    GraphState,
    SeverityLevel,
)

logger = logging.getLogger(__name__)

DECISION_PROMPT = """
You are the Chief Claims Officer of an automobile insurance company.
Review all agent findings and make a final claim decision.

═══════════════════════════════════════════
CLAIM SUMMARY
═══════════════════════════════════════════
Policy Number: {policy_number}
Vehicle: {vehicle_model}
Accident: {accident_description}

VISION ANALYSIS:
- Accident type: {accident_type}
- Overall severity: {overall_severity}
- Parts damaged: {damaged_parts}

DAMAGE ASSESSMENT:
- Category: {damage_category}
- Towing required: {requires_towing}
- Vehicle drivable: {vehicle_drivable}

POLICY COVERAGE:
- Policy type: {policy_type}
- Covered: {damage_covered}
- Coverage: {coverage_pct}%
- Deductible: ₹{deductible:,.0f}
- Max payout: ₹{max_payout:,.0f}
- Exclusions triggered: {exclusions}

REPAIR ESTIMATE:
- Grand total: ₹{repair_total:,.0f}
- Confidence: {repair_confidence:.0%}

FRAUD RISK:
- Risk level: {fraud_risk}
- Fraud score: {fraud_score:.2f}
- Key indicators: {fraud_indicators}

═══════════════════════════════════════════
DECISION RULES:
1. REJECT if: fraud_risk is HIGH, or damage not covered, or exclusions triggered
2. HUMAN_REVIEW if: fraud_risk is MEDIUM, repair_confidence < 0.6,
   or repair_total > max_payout * 0.9, or major inconsistencies exist
3. APPROVE if: covered, LOW fraud risk, estimate within policy limits

Approved amount = repair_total * (coverage_pct / 100) - deductible
Approved amount cannot exceed max_payout.
═══════════════════════════════════════════

Return ONLY a valid JSON object:
{{
  "decision": "<APPROVE|REJECT|HUMAN_REVIEW>",
  "confidence": <0.0 to 1.0>,
  "approved_amount": <float INR — 0 if REJECT>,
  "reasons": ["<reason 1>", "<reason 2>"],
  "conditions": ["<condition if any, e.g. submit additional photos>"],
  "next_steps": ["<step 1>", "<step 2>"],
  "summary": "<2-3 sentence executive summary of the decision>"
}}
"""


class DecisionAgent(BaseAgent):
    """Makes the final claim decision based on all agent outputs."""

    def run(self, state: GraphState) -> GraphState:
        self.logger.info("DecisionAgent starting for claim %s", state.claim_id)
        try:
            prompt = self._build_prompt(state)
            raw_response = self._call_gemini(prompt)
            data = self._extract_json(raw_response)
            state.decision_output = self._parse_output(data, state)

            self.logger.info(
                "DecisionAgent complete — decision=%s, amount=₹%.0f",
                state.decision_output.decision,
                state.decision_output.approved_amount,
            )
        except Exception as exc:
            self.logger.error("DecisionAgent failed: %s", exc, exc_info=True)
            state.errors.append(f"DecisionAgent error: {str(exc)}")
            state.decision_output = self._fallback_output(state)

        return state

    # ──────────────────────────────────────────
    #  Prompt construction
    # ──────────────────────────────────────────

    def _build_prompt(self, state: GraphState) -> str:
        # Vision
        accident_type = "Unknown"
        overall_severity = "Unknown"
        damaged_parts = "Unknown"
        if state.vision_output:
            accident_type = state.vision_output.accident_type
            overall_severity = state.vision_output.overall_severity
            damaged_parts = ", ".join(
                p.part_name for p in state.vision_output.damaged_parts
            )

        # Assessment
        damage_category = "Unknown"
        requires_towing = False
        vehicle_drivable = True
        if state.damage_assessment_output:
            damage_category = state.damage_assessment_output.overall_damage_category
            requires_towing = state.damage_assessment_output.requires_towing
            vehicle_drivable = state.damage_assessment_output.vehicle_drivable

        # Policy
        policy_type = "Unknown"
        damage_covered = False
        coverage_pct = 0.0
        deductible = 5000.0
        max_payout = 100000.0
        exclusions = "None"
        if state.policy_output:
            policy_type = state.policy_output.policy_type
            damage_covered = state.policy_output.damage_covered
            coverage_pct = state.policy_output.coverage_percentage
            deductible = state.policy_output.deductible_amount
            max_payout = state.policy_output.max_payout
            exclusions = (
                ", ".join(state.policy_output.exclusions_triggered) or "None"
            )

        # Repair
        repair_total = 0.0
        repair_confidence = 0.5
        if state.repair_estimation_output:
            repair_total = state.repair_estimation_output.grand_total
            repair_confidence = state.repair_estimation_output.estimation_confidence

        # Fraud
        fraud_risk = "LOW"
        fraud_score = 0.2
        fraud_indicators = "None"
        if state.fraud_risk_output:
            fraud_risk = state.fraud_risk_output.fraud_risk_level
            fraud_score = state.fraud_risk_output.fraud_score
            fraud_indicators = (
                "; ".join(i.indicator for i in state.fraud_risk_output.indicators[:3])
                or "None"
            )

        return DECISION_PROMPT.format(
            policy_number=state.policy_number,
            vehicle_model=state.vehicle_model,
            accident_description=state.accident_description,
            accident_type=accident_type,
            overall_severity=overall_severity,
            damaged_parts=damaged_parts,
            damage_category=damage_category,
            requires_towing=requires_towing,
            vehicle_drivable=vehicle_drivable,
            policy_type=policy_type,
            damage_covered=damage_covered,
            coverage_pct=coverage_pct,
            deductible=deductible,
            max_payout=max_payout,
            exclusions=exclusions,
            repair_total=repair_total,
            repair_confidence=repair_confidence,
            fraud_risk=fraud_risk,
            fraud_score=fraud_score,
            fraud_indicators=fraud_indicators,
        )

    def _parse_output(self, data: dict[str, Any], state: GraphState) -> DecisionAgentOutput:
        raw_decision = data.get("decision", "HUMAN_REVIEW")

        # Hard override: HIGH fraud → always REJECT
        if state.fraud_risk_output and state.fraud_risk_output.fraud_risk_level == FraudRisk.HIGH:
            raw_decision = "REJECT"

        # Hard override: not covered → REJECT
        if state.policy_output and not state.policy_output.damage_covered:
            raw_decision = "REJECT"

        return DecisionAgentOutput(
            decision=ClaimDecision(raw_decision),
            confidence=float(data.get("confidence", 0.8)),
            approved_amount=float(data.get("approved_amount", 0)),
            reasons=data.get("reasons", []),
            conditions=data.get("conditions", []),
            next_steps=data.get("next_steps", []),
            summary=data.get("summary", ""),
        )

    def _fallback_output(self, state: GraphState) -> DecisionAgentOutput:
        return DecisionAgentOutput(
            decision=ClaimDecision.HUMAN_REVIEW,
            confidence=0.5,
            approved_amount=0.0,
            reasons=["Automated processing encountered errors — routing to manual review"],
            conditions=[],
            next_steps=[
                "Assign to claims adjuster",
                "Request physical vehicle inspection",
                "Verify policy details manually",
            ],
            summary=(
                "The automated claim processing pipeline encountered errors. "
                "This claim has been routed for human review. "
                f"Processing errors: {'; '.join(state.errors)}"
            ),
        )
