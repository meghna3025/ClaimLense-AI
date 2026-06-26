"""
FastAPI routes for ClaimSense AI.
"""

import base64
import uuid
import logging
from typing import Annotated

from fastapi import APIRouter, File, Form, HTTPException, UploadFile, status

from app.core.video_utils import extract_frames_from_video
from app.graph.orchestrator import run_claim_pipeline
from app.models.schemas import ClaimProcessingResult, GraphState

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/v1/claims", tags=["Claims"])

ALLOWED_IMAGE_TYPES = {"image/jpeg", "image/png", "image/webp"}
ALLOWED_VIDEO_TYPES = {"video/mp4", "video/quicktime", "video/x-msvideo", "video/webm", "video/mpeg"}


@router.post(
    "/process",
    response_model=ClaimProcessingResult,
    summary="Process an insurance claim",
    description=(
        "Upload an accident image OR video clip and provide claim details. "
        "Returns a full AI analysis with a final APPROVE / REJECT / HUMAN_REVIEW decision."
    ),
)
async def process_claim(
    description: Annotated[str, Form(description="Accident description by the claimant")],
    policy_number: Annotated[str, Form(description="Insurance policy number")],
    vehicle_model: Annotated[str, Form(description="Vehicle make and model e.g. Toyota Corolla")],
    image: Annotated[UploadFile | None, File(description="Accident photograph (JPEG / PNG / WebP)")] = None,
    video: Annotated[UploadFile | None, File(description="Accident video clip (MP4 / MOV / AVI / WebM, max 100MB)")] = None,
) -> ClaimProcessingResult:
    """
    Main endpoint — runs the full 6-agent LangGraph pipeline.
    Accepts either an image or a video. If video, frames are auto-extracted.
    """
    if image is None and video is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Provide either an image or a video file.",
        )

    claim_id = f"CLM-{uuid.uuid4().hex[:10].upper()}"
    logger.info(
        "Received claim %s — policy=%s vehicle=%s media=%s",
        claim_id, policy_number, vehicle_model,
        "video" if video else "image",
    )

    extra_image_parts: list[dict] = []
    media_source = "image"

    if video is not None:
        # ── Video path ────────────────────────────────────────────
        if video.content_type not in ALLOWED_VIDEO_TYPES:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Unsupported video type '{video.content_type}'. Use MP4, MOV, AVI, or WebM.",
            )
        video_bytes = await video.read()
        if len(video_bytes) > 100 * 1024 * 1024:  # 100 MB limit
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Video size must not exceed 100 MB.",
            )
        logger.info("Extracting frames from video (%.1f MB)...", len(video_bytes) / 1024 / 1024)
        try:
            frames = extract_frames_from_video(video_bytes)
        except Exception as exc:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Video frame extraction failed: {str(exc)}",
            )
        if not frames:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="No usable frames could be extracted from the video.",
            )
        # Use first frame as primary image, rest as extras
        first_frame = frames[0]
        image_b64 = base64.b64encode(first_frame["data"]).decode("utf-8")
        image_mime = "image/jpeg"
        extra_image_parts = frames[1:]
        media_source = "video"
        logger.info("Extracted %d frames from video for analysis", len(frames))

    else:
        # ── Image path ────────────────────────────────────────────
        if image.content_type not in ALLOWED_IMAGE_TYPES:
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
        image_mime = image.content_type or "image/jpeg"

    # Build initial state
    initial_state = GraphState(
        claim_id=claim_id,
        policy_number=policy_number.strip(),
        vehicle_model=vehicle_model.strip(),
        accident_description=description.strip(),
        image_base64=image_b64,
        image_mime_type=image_mime,
        extra_image_parts=extra_image_parts,
        media_source=media_source,
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
