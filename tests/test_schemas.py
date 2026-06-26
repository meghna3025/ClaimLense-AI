"""
Unit tests for Pydantic schemas and agent output parsing.
Run: pytest tests/ -v
"""

import pytest
from app.models.schemas import (
    ClaimDecision,
    DamagedPart,
    FraudRisk,
    GraphState,
    SeverityLevel,
    VisionAgentOutput,
    DamageAssessmentOutput,
    PartAssessment,
    RepairAction,
    RepairEstimationOutput,
    PartEstimate,
    FraudRiskOutput,
    FraudIndicator,
    DecisionAgentOutput,
    PolicyAgentOutput,
)


class TestVisionAgentOutput:
    def test_valid_output(self):
        part = DamagedPart(
            part_name="Front Bumper",
            damage_description="Cracked and bent",
            severity=SeverityLevel.MODERATE,
            confidence=0.92,
        )
        output = VisionAgentOutput(
            damaged_parts=[part],
            overall_severity=SeverityLevel.MODERATE,
            accident_type="front collision",
            image_quality="Clear",
            raw_observations="Front bumper shows significant crack.",
        )
        assert len(output.damaged_parts) == 1
        assert output.overall_severity == SeverityLevel.MODERATE

    def test_confidence_bounds(self):
        with pytest.raises(Exception):
            DamagedPart(
                part_name="Headlight",
                damage_description="Broken",
                severity=SeverityLevel.MINOR,
                confidence=1.5,  # Invalid — must be ≤ 1.0
            )


class TestGraphState:
    def test_default_state(self):
        state = GraphState(
            claim_id="CLM-TEST-001",
            policy_number="POL-STANDARD-1234",
            vehicle_model="Toyota Corolla",
            accident_description="Front collision at intersection",
            image_base64="dGVzdA==",
        )
        assert state.errors == []
        assert state.vision_output is None
        assert state.decision_output is None

    def test_errors_accumulate(self):
        state = GraphState(
            claim_id="CLM-TEST-002",
            policy_number="POL-BASIC-0001",
            vehicle_model="Honda City",
            accident_description="Side impact",
            image_base64="dGVzdA==",
        )
        state.errors.append("VisionAgent error: timeout")
        state.errors.append("PolicyAgent error: no data")
        assert len(state.errors) == 2


class TestDecisionAgent:
    def test_decision_values(self):
        for d in ["APPROVE", "REJECT", "HUMAN_REVIEW"]:
            assert ClaimDecision(d) is not None

    def test_fraud_risk_values(self):
        for r in ["LOW", "MEDIUM", "HIGH"]:
            assert FraudRisk(r) is not None

    def test_severity_values(self):
        for s in ["MINOR", "MODERATE", "SEVERE", "TOTAL_LOSS"]:
            assert SeverityLevel(s) is not None

    def test_repair_action_values(self):
        for a in ["REPAIR", "REPLACE", "MONITOR"]:
            assert RepairAction(a) is not None


class TestRepairEstimation:
    def test_total_calculation(self):
        estimates = [
            PartEstimate(
                part_name="Front Bumper",
                action=RepairAction.REPLACE,
                parts_cost=18000,
                labour_cost=4000,
                total_cost=22000,
            ),
            PartEstimate(
                part_name="Headlight",
                action=RepairAction.REPLACE,
                parts_cost=9500,
                labour_cost=1500,
                total_cost=11000,
            ),
        ]
        output = RepairEstimationOutput(
            vehicle_model="Toyota Corolla",
            estimates=estimates,
            subtotal_parts=27500,
            subtotal_labour=5500,
            grand_total=33000,
            currency="INR",
            estimation_confidence=0.9,
            notes="",
        )
        assert output.grand_total == 33000
        assert output.currency == "INR"
