"""
Vision Agent
─────────────
Uses Gemini Vision to analyse an accident image, detect damaged automobile
parts, classify severity, and flag any unauthorised vehicle modifications
that may void or reduce insurance coverage.
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
    VehicleModification,
    VisionAgentOutput,
)

logger = logging.getLogger(__name__)

VISION_PROMPT = """
You are an expert automobile damage inspector and insurance assessor with 20+ years of experience.
Carefully analyse the provided vehicle image.

Return ONLY a valid JSON object with this exact structure — no markdown fences:
{{
  "damaged_parts": [
    {{
      "part_name": "<specific part name>",
      "damage_description": "<detailed visual description of the damage>",
      "severity": "<MINOR|MODERATE|SEVERE|TOTAL_LOSS>",
      "confidence": <0.0 to 1.0>
    }}
  ],
  "overall_severity": "<MINOR|MODERATE|SEVERE|TOTAL_LOSS>",
  "accident_type": "<front collision|rear-end|side impact|rollover|multi-point|unknown>",
  "image_quality": "<Clear|Blurry|Partial>",
  "raw_observations": "<free-text description of everything visually observed>",
  "modifications_detected": [
    {{
      "modification_type": "<type e.g. aftermarket exhaust, engine chip tune, body kit, lift kit, racing tyres, tinted windows beyond legal limit, nitrous system, roll cage, suspension lowering>",
      "description": "<what is visually visible in the image>",
      "claim_impact": "<how this modification affects the insurance claim>",
      "rejection_reason": "<specific policy reason e.g. Unauthorised performance modification voids Section 4.2 of standard policy>"
    }}
  ]
}}

Context provided by claimant:
- Vehicle model: {vehicle_model}
- Accident description: {accident_description}

DAMAGE INSPECTION RULES:
- Identify EVERY visible damaged part (bumpers, headlights, bonnet, doors, fenders, wheels, windscreen, etc.)
- Be specific: "left front headlight — lens shattered" not just "headlight damaged"
- Confidence reflects how clearly the damage is visible
- If image is unclear, still provide best estimates with lower confidence values

MODIFICATION DETECTION RULES (critical for claim validity):
Inspect the vehicle carefully for ANY of these unauthorised modifications that standard policies do not cover:
1. Performance/engine mods — aftermarket air intakes, chip tuning stickers, turbo/supercharger additions, exhaust modifications
2. Suspension mods — lowering kits, lift kits, non-standard shock absorbers, air suspension
3. Body modifications — aftermarket body kits, non-OEM bumpers, spoilers, wide-body kits, vinyl wraps
4. Wheel/tyre mods — oversized wheels, racing slick tyres, non-standard offsets
5. Interior mods — roll cages, racing seats without harness approval, removed airbags
6. Lighting mods — illegal tint, HID/LED retrofits without approval, underlighting
7. Towing/hauling mods — non-approved tow bars, roof racks affecting structural integrity
8. Safety system tampering — removed or bypassed airbags, ABS disabling

If NO modifications are visible, return an empty array: "modifications_detected": []
Only include modifications that are CLEARLY VISIBLE in the image.
"""


class VisionAgent(BaseAgent):
    """Detects damaged parts and unauthorised modifications using Gemini Vision."""

    def run(self, state: GraphState) -> GraphState:
        self.logger.info("VisionAgent starting for claim %s", state.claim_id)
        try:
            image_bytes = base64.b64decode(state.image_base64)

            # Use actual mime type from upload, not hardcoded jpeg
            mime_type = state.image_mime_type or "image/jpeg"

            image_part = {
                "mime_type": mime_type,
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

            mod_count = len(output.modifications_detected)
            self.logger.info(
                "VisionAgent complete — %d parts detected, severity=%s, modifications=%d",
                len(output.damaged_parts),
                output.overall_severity,
                mod_count,
            )
            if mod_count > 0:
                self.logger.warning(
                    "MODIFICATIONS DETECTED for claim %s: %s",
                    state.claim_id,
                    [m.modification_type for m in output.modifications_detected],
                )

        except Exception as exc:
            self.logger.error("VisionAgent failed: %s", exc, exc_info=True)
            state.errors.append(f"VisionAgent error: {str(exc)}")
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

        modifications = [
            VehicleModification(
                modification_type=m["modification_type"],
                description=m["description"],
                claim_impact=m["claim_impact"],
                rejection_reason=m["rejection_reason"],
            )
            for m in data.get("modifications_detected", [])
        ]

        return VisionAgentOutput(
            damaged_parts=parts,
            overall_severity=SeverityLevel(data.get("overall_severity", "MODERATE")),
            accident_type=data.get("accident_type", "unknown"),
            image_quality=data.get("image_quality", "Clear"),
            raw_observations=data.get("raw_observations", ""),
            modifications_detected=modifications,
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
            modifications_detected=[],
        )
