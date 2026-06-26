"""
Damage Assessment Agent
────────────────────────
Converts raw visual observations into insurance-standard terminology,
recommends repair vs replacement, and produces structured assessments.
"""

import logging
from typing import Any

from app.agents.base import BaseAgent
from app.models.schemas import (
    DamageAssessmentOutput,
    GraphState,
    PartAssessment,
    RepairAction,
    SeverityLevel,
)

logger = logging.getLogger(__name__)

ASSESSMENT_PROMPT = """
You are a certified automobile insurance damage assessor.
Convert the following visual inspection data into formal insurance assessment terminology.

Visual Inspection Data:
{visual_data}

Vehicle: {vehicle_model}
Accident Description: {accident_description}

Return ONLY a valid JSON object with this structure:
{{
  "assessments": [
    {{
      "part_name": "<part name>",
      "insurance_terminology": "<official insurance term e.g. 'Direct Collision Damage — Front Fascia'>",
      "recommended_action": "<REPAIR|REPLACE|MONITOR>",
      "severity": "<MINOR|MODERATE|SEVERE|TOTAL_LOSS>",
      "justification": "<why repair/replace/monitor>"
    }}
  ],
  "overall_damage_category": "<e.g. Minor Collision Damage | Major Structural Damage | Total Loss>",
  "total_parts_damaged": <integer>,
  "requires_towing": <true|false>,
  "vehicle_drivable": <true|false>,
  "notes": "<any additional assessor notes>"
}}

Guidelines:
- Use industry-standard insurance terminology
- REPLACE if structural damage or safety systems are compromised
- REPAIR for cosmetic / surface-level damage
- MONITOR for suspected damage that needs specialist inspection
- requires_towing: true if any structural, suspension, or powertrain damage
- vehicle_drivable: false if airbags deployed, structural damage, or wheel/suspension damage
"""


class DamageAssessmentAgent(BaseAgent):
    """Converts visual observations to formal insurance damage assessments."""

    def run(self, state: GraphState) -> GraphState:
        self.logger.info("DamageAssessmentAgent starting for claim %s", state.claim_id)
        try:
            if state.vision_output is None:
                raise ValueError("VisionAgent output is required but missing")

            visual_data = self._format_visual_data(state.vision_output)
            prompt = ASSESSMENT_PROMPT.format(
                visual_data=visual_data,
                vehicle_model=state.vehicle_model,
                accident_description=state.accident_description,
            )

            raw_response = self._call_gemini(prompt)
            data = self._extract_json(raw_response)
            state.damage_assessment_output = self._parse_output(data)

            self.logger.info(
                "DamageAssessmentAgent complete — %d assessments, category=%s",
                len(state.damage_assessment_output.assessments),
                state.damage_assessment_output.overall_damage_category,
            )
        except Exception as exc:
            self.logger.error("DamageAssessmentAgent failed: %s", exc, exc_info=True)
            state.errors.append(f"DamageAssessmentAgent error: {str(exc)}")
            state.damage_assessment_output = self._fallback_output(state)

        return state

    # ──────────────────────────────────────────
    #  Helpers
    # ──────────────────────────────────────────

    def _format_visual_data(self, vision_output: Any) -> str:
        lines = [f"Overall Severity: {vision_output.overall_severity}",
                 f"Accident Type: {vision_output.accident_type}",
                 f"Image Quality: {vision_output.image_quality}",
                 "", "Damaged Parts:"]
        for p in vision_output.damaged_parts:
            lines.append(
                f"  - {p.part_name}: {p.damage_description} "
                f"(Severity: {p.severity}, Confidence: {p.confidence:.0%})"
            )
        lines.append(f"\nRaw Observations: {vision_output.raw_observations}")
        return "\n".join(lines)

    def _parse_output(self, data: dict[str, Any]) -> DamageAssessmentOutput:
        assessments = [
            PartAssessment(
                part_name=a["part_name"],
                insurance_terminology=a["insurance_terminology"],
                recommended_action=RepairAction(a["recommended_action"]),
                severity=SeverityLevel(a["severity"]),
                justification=a["justification"],
            )
            for a in data.get("assessments", [])
        ]
        return DamageAssessmentOutput(
            assessments=assessments,
            overall_damage_category=data.get("overall_damage_category", "Moderate Collision Damage"),
            total_parts_damaged=int(data.get("total_parts_damaged", len(assessments))),
            requires_towing=bool(data.get("requires_towing", False)),
            vehicle_drivable=bool(data.get("vehicle_drivable", True)),
            notes=data.get("notes", ""),
        )

    def _fallback_output(self, state: GraphState) -> DamageAssessmentOutput:
        parts = []
        if state.vision_output:
            for p in state.vision_output.damaged_parts:
                parts.append(
                    PartAssessment(
                        part_name=p.part_name,
                        insurance_terminology=f"Collision Damage — {p.part_name}",
                        recommended_action=RepairAction.REPAIR,
                        severity=p.severity,
                        justification="Assessment generated from visual data (fallback mode)",
                    )
                )
        return DamageAssessmentOutput(
            assessments=parts,
            overall_damage_category="Moderate Collision Damage",
            total_parts_damaged=len(parts),
            requires_towing=False,
            vehicle_drivable=True,
            notes="Generated in fallback mode — manual review recommended",
        )
