"""
Integration tests for the FastAPI endpoints.
Uses httpx TestClient with mocked pipeline.

Run: pytest tests/test_api.py -v
"""

import base64
from io import BytesIO
from unittest.mock import MagicMock, patch

import pytest
from fastapi.testclient import TestClient
from PIL import Image

from app.main import app
from app.models.schemas import (
    ClaimDecision,
    ClaimProcessingResult,
    DecisionAgentOutput,
    FraudRisk,
    FraudRiskOutput,
    GraphState,
)

client = TestClient(app)


def _make_test_image() -> bytes:
    """Generate a minimal valid JPEG for testing."""
    img = Image.new("RGB", (100, 100), color=(200, 100, 50))
    buf = BytesIO()
    img.save(buf, format="JPEG")
    return buf.getvalue()


def _mock_final_state(claim_id: str) -> GraphState:
    """Return a realistic mock final state."""
    from app.models.schemas import (
        DamagedPart,
        DamageAssessmentOutput,
        FraudIndicator,
        PartAssessment,
        PartEstimate,
        PolicyAgentOutput,
        PolicyClause,
        RepairEstimationOutput,
        RepairAction,
        SeverityLevel,
        VisionAgentOutput,
    )

    state = GraphState(
        claim_id=claim_id,
        policy_number="POL-STANDARD-1234",
        vehicle_model="Toyota Corolla",
        accident_description="Front collision at intersection",
        image_base64="test",
    )
    state.vision_output = VisionAgentOutput(
        damaged_parts=[
            DamagedPart(
                part_name="Front Bumper",
                damage_description="Cracked",
                severity=SeverityLevel.MODERATE,
                confidence=0.9,
            )
        ],
        overall_severity=SeverityLevel.MODERATE,
        accident_type="front collision",
        image_quality="Clear",
        raw_observations="Front bumper damaged",
    )
    state.damage_assessment_output = DamageAssessmentOutput(
        assessments=[
            PartAssessment(
                part_name="Front Bumper",
                insurance_terminology="Direct Collision Damage — Front Fascia",
                recommended_action=RepairAction.REPLACE,
                severity=SeverityLevel.MODERATE,
                justification="Structural crack requires full replacement",
            )
        ],
        overall_damage_category="Moderate Collision Damage",
        total_parts_damaged=1,
        requires_towing=False,
        vehicle_drivable=True,
        notes="",
    )
    state.policy_output = PolicyAgentOutput(
        policy_number="POL-STANDARD-1234",
        policy_type="Standard",
        damage_covered=True,
        coverage_percentage=80.0,
        deductible_amount=5000.0,
        max_payout=150000.0,
        supporting_clauses=[
            PolicyClause(
                clause_id="Section 1.1",
                clause_text="Accidental damage to own vehicle covered",
                relevance_score=0.95,
            )
        ],
        exclusions_triggered=[],
        coverage_notes="Covered under Standard plan Section 1.1",
    )
    state.repair_estimation_output = RepairEstimationOutput(
        vehicle_model="Toyota Corolla",
        estimates=[
            PartEstimate(
                part_name="Front Bumper",
                action=RepairAction.REPLACE,
                parts_cost=18000,
                labour_cost=4000,
                total_cost=22000,
            )
        ],
        subtotal_parts=18000,
        subtotal_labour=4000,
        grand_total=22000,
        currency="INR",
        estimation_confidence=0.88,
        notes="",
    )
    state.fraud_risk_output = FraudRiskOutput(
        fraud_score=0.1,
        fraud_risk_level=FraudRisk.LOW,
        indicators=[],
        inconsistencies_found=[],
        reasoning="No fraud indicators detected",
        recommendation="Proceed with claim",
    )
    state.decision_output = DecisionAgentOutput(
        decision=ClaimDecision.APPROVE,
        confidence=0.92,
        approved_amount=12600.0,
        reasons=["Covered under Standard policy", "Low fraud risk"],
        conditions=[],
        next_steps=["Transfer ₹12,600 to claimant's account"],
        summary="Claim approved. ₹12,600 payable after deductible.",
    )
    return state


class TestHealthEndpoint:
    def test_health_check(self):
        response = client.get("/api/v1/claims/health")
        assert response.status_code == 200
        assert response.json()["status"] == "healthy"

    def test_root_endpoint(self):
        response = client.get("/")
        assert response.status_code == 200
        assert "ClaimSense AI" in response.json()["service"]


class TestClaimsProcessEndpoint:
    def test_process_claim_success(self):
        """Test happy path with mocked pipeline."""
        image_bytes = _make_test_image()

        with patch("app.api.routes.run_claim_pipeline") as mock_pipeline:
            mock_pipeline.side_effect = lambda state: _mock_final_state(state.claim_id)

            response = client.post(
                "/api/v1/claims/process",
                files={"image": ("test.jpg", image_bytes, "image/jpeg")},
                data={
                    "description": "Front collision at intersection",
                    "policy_number": "POL-STANDARD-1234",
                    "vehicle_model": "Toyota Corolla",
                },
            )

        assert response.status_code == 200
        result = response.json()
        assert result["status"] in ("PROCESSED", "PROCESSED_WITH_ERRORS")
        assert result["claim_id"].startswith("CLM-")
        assert result["decision"]["decision"] == "APPROVE"
        assert result["decision"]["approved_amount"] == 12600.0

    def test_invalid_image_type(self):
        """Non-image file should return 400."""
        response = client.post(
            "/api/v1/claims/process",
            files={"image": ("test.pdf", b"fake pdf content", "application/pdf")},
            data={
                "description": "Test",
                "policy_number": "POL-BASIC-0001",
                "vehicle_model": "Honda City",
            },
        )
        assert response.status_code == 400

    def test_missing_fields(self):
        """Missing required fields should return 422."""
        response = client.post(
            "/api/v1/claims/process",
            files={"image": ("test.jpg", _make_test_image(), "image/jpeg")},
            data={
                "description": "Front collision",
                # Missing policy_number and vehicle_model
            },
        )
        assert response.status_code == 422
