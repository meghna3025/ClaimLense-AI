"""
FastAPI routes for ClaimSense AI.
"""

import base64
import uuid
import logging
from typing import Annotated

from fastapi import APIRouter, File, Form, HTTPException, UploadFile, status

from app.graph.orchestrator import run_claim_pipeline
from app.models.schemas import ClaimProcessingResult, GraphState

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/v1/claims", tags=["Claims"])


@router.post(
    "/process",
    response_model=ClaimProcessingResult,
    summary="Process an insurance claim",
    description=(
        "Upload an accident image and provide claim details. "
        "Returns a full AI analysis with a final APPROVE / REJECT / HUMAN_REVIEW decision."
    ),
)
async def process_claim(
    image: Annotated[UploadFile, File(description="Accident photograph (JPEG / PNG)")],
    description: Annotated[str, Form(description="Accident description by the claimant")],
    policy_number: Annotated[str, Form(description="Insurance policy number")],
    vehicle_model: Annotated[str, Form(description="Vehicle make and model e.g. Toyota Corolla")],
) -> ClaimProcessingResult:
    """
    Main endpoint — runs the full 6-agent LangGraph pipeline and returns
    structured results for every stage.
    """
    claim_id = f"CLM-{uuid.uuid4().hex[:10].upper()}"
    logger.info(
        "Received claim %s — policy=%s vehicle=%s", claim_id, policy_number, vehicle_model
    )

    # Read and encode image
    if image.content_type not in ("image/jpeg", "image/png", "image/webp"):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Only JPEG, PNG, or WebP images are supported.",
        )

    image_bytes = await image.read()
    if len(image_bytes) > 20 * 1024 * 1024:  # 20 MB limit
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Image size must not exceed 20 MB.",
        )
    image_b64 = base64.b64encode(image_bytes).decode("utf-8")

    # Build initial state
    initial_state = GraphState(
        claim_id=claim_id,
        policy_number=policy_number.strip(),
        vehicle_model=vehicle_model.strip(),
        accident_description=description.strip(),
        image_base64=image_b64,
    )

    try:
        final_state = run_claim_pipeline(initial_state)
    except Exception as exc:
        logger.error("Pipeline failed for claim %s: %s", claim_id, exc, exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Claim processing failed: {str(exc)}",
        )

    return ClaimProcessingResult(
        claim_id=claim_id,
        status="PROCESSED" if not final_state.errors else "PROCESSED_WITH_ERRORS",
        vision=final_state.vision_output,
        damage_assessment=final_state.damage_assessment_output,
        policy=final_state.policy_output,
        repair_estimation=final_state.repair_estimation_output,
        fraud_risk=final_state.fraud_risk_output,
        decision=final_state.decision_output,
        processing_errors=final_state.errors,
    )


@router.get("/health", summary="Health check")
async def health_check() -> dict[str, str]:
    return {"status": "healthy", "service": "ClaimSense AI"}
