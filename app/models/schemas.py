"""
Pydantic schemas for all agent inputs, outputs, and the API contract.
"""

from __future__ import annotations
from enum import Enum
from typing import Any
from pydantic import BaseModel, Field


# ─────────────────────────────────────────
#  Enums
# ─────────────────────────────────────────

class SeverityLevel(str, Enum):
    MINOR = "MINOR"
    MODERATE = "MODERATE"
    SEVERE = "SEVERE"
    TOTAL_LOSS = "TOTAL_LOSS"


class RepairAction(str, Enum):
    REPAIR = "REPAIR"
    REPLACE = "REPLACE"
    MONITOR = "MONITOR"


class FraudRisk(str, Enum):
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"


class ClaimDecision(str, Enum):
    APPROVE = "APPROVE"
    REJECT = "REJECT"
    HUMAN_REVIEW = "HUMAN_REVIEW"


# ─────────────────────────────────────────
#  Vision Agent
# ─────────────────────────────────────────

class DamagedPart(BaseModel):
    part_name: str = Field(..., description="Name of the damaged automobile part")
    damage_description: str = Field(..., description="Detailed visual description of the damage")
    severity: SeverityLevel
    confidence: float = Field(..., ge=0.0, le=1.0, description="Detection confidence 0-1")


class VisionAgentOutput(BaseModel):
    damaged_parts: list[DamagedPart]
    overall_severity: SeverityLevel
    accident_type: str = Field(..., description="E.g. front collision, rear-end, side impact")
    image_quality: str = Field(..., description="Clear / Blurry / Partial")
    raw_observations: str = Field(..., description="Free-text observations from Gemini Vision")


# ─────────────────────────────────────────
#  Damage Assessment Agent
# ─────────────────────────────────────────

class PartAssessment(BaseModel):
    part_name: str
    insurance_terminology: str = Field(..., description="Official insurance term for the damage")
    recommended_action: RepairAction
    severity: SeverityLevel
    justification: str


class DamageAssessmentOutput(BaseModel):
    assessments: list[PartAssessment]
    overall_damage_category: str = Field(
        ..., description="E.g. Minor Collision Damage, Major Structural Damage"
    )
    total_parts_damaged: int
    requires_towing: bool
    vehicle_drivable: bool
    notes: str


# ─────────────────────────────────────────
#  Policy Agent
# ─────────────────────────────────────────

class PolicyClause(BaseModel):
    clause_id: str
    clause_text: str
    relevance_score: float = Field(..., ge=0.0, le=1.0)


class PolicyAgentOutput(BaseModel):
    policy_number: str
    policy_type: str = Field(..., description="Basic / Standard / Premium / Comprehensive")
    damage_covered: bool
    coverage_percentage: float = Field(..., ge=0.0, le=100.0)
    deductible_amount: float
    max_payout: float
    supporting_clauses: list[PolicyClause]
    exclusions_triggered: list[str]
    coverage_notes: str


# ─────────────────────────────────────────
#  Repair Estimation Agent
# ─────────────────────────────────────────

class PartEstimate(BaseModel):
    part_name: str
    action: RepairAction
    parts_cost: float
    labour_cost: float
    total_cost: float
    vendor_note: str = ""


class RepairEstimationOutput(BaseModel):
    vehicle_model: str
    estimates: list[PartEstimate]
    subtotal_parts: float
    subtotal_labour: float
    grand_total: float
    currency: str = "INR"
    estimation_confidence: float = Field(..., ge=0.0, le=1.0)
    notes: str


# ─────────────────────────────────────────
#  Fraud Risk Agent
# ─────────────────────────────────────────

class FraudIndicator(BaseModel):
    indicator: str
    description: str
    weight: float = Field(..., ge=0.0, le=1.0, description="How much this contributes to fraud score")


class FraudRiskOutput(BaseModel):
    fraud_score: float = Field(..., ge=0.0, le=1.0)
    fraud_risk_level: FraudRisk
    indicators: list[FraudIndicator]
    inconsistencies_found: list[str]
    reasoning: str
    recommendation: str


# ─────────────────────────────────────────
#  Decision Agent
# ─────────────────────────────────────────

class DecisionAgentOutput(BaseModel):
    decision: ClaimDecision
    confidence: float = Field(..., ge=0.0, le=1.0)
    approved_amount: float
    reasons: list[str]
    conditions: list[str] = Field(default_factory=list)
    next_steps: list[str]
    summary: str


# ─────────────────────────────────────────
#  Full Pipeline State
# ─────────────────────────────────────────

class ClaimInput(BaseModel):
    """Input from the user / API layer"""
    policy_number: str
    vehicle_model: str
    accident_description: str
    image_base64: str = Field(..., description="Base64-encoded accident image")


class ClaimProcessingResult(BaseModel):
    """Final response returned by the API"""
    claim_id: str
    status: str = "PROCESSED"
    vision: VisionAgentOutput | None = None
    damage_assessment: DamageAssessmentOutput | None = None
    policy: PolicyAgentOutput | None = None
    repair_estimation: RepairEstimationOutput | None = None
    fraud_risk: FraudRiskOutput | None = None
    decision: DecisionAgentOutput | None = None
    processing_errors: list[str] = Field(default_factory=list)


# ─────────────────────────────────────────
#  LangGraph State
# ─────────────────────────────────────────

class GraphState(BaseModel):
    """Shared mutable state passed between LangGraph nodes"""
    model_config = {"arbitrary_types_allowed": True}

    # Inputs
    claim_id: str = ""
    policy_number: str = ""
    vehicle_model: str = ""
    accident_description: str = ""
    image_base64: str = ""

    # Agent outputs
    vision_output: VisionAgentOutput | None = None
    damage_assessment_output: DamageAssessmentOutput | None = None
    policy_output: PolicyAgentOutput | None = None
    repair_estimation_output: RepairEstimationOutput | None = None
    fraud_risk_output: FraudRiskOutput | None = None
    decision_output: DecisionAgentOutput | None = None

    # Errors
    errors: list[str] = Field(default_factory=list)
