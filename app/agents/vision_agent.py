"""
Vision Agent
─────────────
Uses Gemini Vision to analyse an accident image and detect damaged
automobile parts, classify severity, and return structured JSON.
"""

import base64
import logging
from typing import Any

import google.generativeai as genai

from app.agents.base import BaseAgent
from app.models.schemas import (
    DamagedPart,
    GraphState,
    SeverityLevel,
    VisionAgentOutput,
)

logger = logging.getLogger(__name__)

VISION_PROMPT = """
You are an expert automobile damage inspector with 20+ years of experience.
Analyse the provided accident image carefully.

Return ONLY a valid JSON object with this exact structure:
{{
  "damaged_parts": [
    {{
      "part_name": "<name of the part>",
      "damage_description": "<detailed visual description>",
      "severity": "<MINOR|MODERATE|SEVERE|TOTAL_LOSS>",
      "confidence": <0.0 to 1.0>
    }}
  ],
  "overall_severity": "<MINOR|MODERATE|SEVERE|TOTAL_LOSS>",
  "accident_type": "<front collision|rear-end|side impact|rollover|multi-point|unknown>",
  "image_quality": "<Clear|Blurry|Partial>",
  "raw_observations": "<free-text description of everything you observe>"
}}

Context provided by the claimant:
- Vehicle model: {vehicle_model}
- Accident description: {accident_description}

Rules:
- Identify EVERY visible damaged part (bumpers, headlights, bonnet, doors, etc.)
- Be specific: "left headlight cracked" not just "headlight damaged"
- Confidence should reflect how clearly you can see the damage
- If the image is unclear, still provide best estimates with lower confidence
- Do NOT wrap the JSON in markdown code fences in your final answer
"""


class VisionAgent(BaseAgent):
    """Detects damaged parts from accident images using Gemini Vision."""

    def run(self, state: GraphState) -> GraphState:
        self.logger.info("VisionAgent starting for claim %s", state.claim_id)
        try:
            # Decode base64 image
            image_bytes = base64.b64decode(state.image_base64)

            # Build Gemini image part
            image_part = {
                "mime_type": "image/jpeg",
                "data": image_bytes,
            }

            prompt = VISION_PROMPT.format(
                vehicle_model=state.vehicle_model,
                accident_description=state.accident_description,
            )

            raw_response = self._call_gemini_vision(
                prompt=prompt,
                image_parts=[image_part],
            )

            data = self._extract_json(raw_response)
            output = self._parse_output(data)
            state.vision_output = output
            self.logger.info(
                "VisionAgent complete — %d parts detected, severity=%s",
                len(output.damaged_parts),
                output.overall_severity,
            )

        except Exception as exc:
            self.logger.error("VisionAgent failed: %s", exc, exc_info=True)
            state.errors.append(f"VisionAgent error: {str(exc)}")
            # Provide a fallback output so the pipeline can continue
            state.vision_output = self._fallback_output(state.accident_description)

        return state

    # ──────────────────────────────────────────
    #  Helpers
    # ──────────────────────────────────────────

    def _parse_output(self, data: dict[str, Any]) -> VisionAgentOutput:
        parts = [
            DamagedPart(
                part_name=p["part_name"],
                damage_description=p["damage_description"],
                severity=SeverityLevel(p["severity"]),
                confidence=float(p["confidence"]),
            )
            for p in data.get("damaged_parts", [])
        ]
        return VisionAgentOutput(
            damaged_parts=parts,
            overall_severity=SeverityLevel(data.get("overall_severity", "MODERATE")),
            accident_type=data.get("accident_type", "unknown"),
            image_quality=data.get("image_quality", "Clear"),
            raw_observations=data.get("raw_observations", ""),
        )

    def _fallback_output(self, description: str) -> VisionAgentOutput:
        """Minimal output when vision analysis fails."""
        return VisionAgentOutput(
            damaged_parts=[
                DamagedPart(
                    part_name="Unknown",
                    damage_description=f"Could not analyse image. Description: {description}",
                    severity=SeverityLevel.MODERATE,
                    confidence=0.2,
                )
            ],
            overall_severity=SeverityLevel.MODERATE,
            accident_type="unknown",
            image_quality="Blurry",
            raw_observations="Image analysis failed — using description only.",
        )
