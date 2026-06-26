"""
Base agent class — wraps Gemini API calls with retry logic and structured JSON parsing.
"""

import json
import logging
import re
from abc import ABC, abstractmethod
from typing import Any, TypeVar

import google.generativeai as genai
from tenacity import retry, stop_after_attempt, wait_exponential

from app.core.config import settings

logger = logging.getLogger(__name__)

T = TypeVar("T")


def _configure_gemini() -> None:
    """Configure the Gemini SDK (idempotent)."""
    if settings.gemini_api_key:
        genai.configure(api_key=settings.gemini_api_key)


class BaseAgent(ABC):
    """All ClaimSense agents inherit from this class."""

    def __init__(self, model_name: str | None = None) -> None:
        _configure_gemini()
        self.model_name = model_name or settings.gemini_model
        self.model = genai.GenerativeModel(self.model_name)
        self.logger = logging.getLogger(self.__class__.__name__)

    # ──────────────────────────────────────────
    #  Gemini call helpers
    # ──────────────────────────────────────────

    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=2, max=10),
        reraise=True,
    )
    def _call_gemini(self, prompt: str, **kwargs: Any) -> str:
        """Send a text prompt to Gemini and return the response text."""
        response = self.model.generate_content(prompt, **kwargs)
        return response.text

    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=2, max=10),
        reraise=True,
    )
    def _call_gemini_vision(self, prompt: str, image_parts: list[Any]) -> str:
        """Send a multimodal (text + image) prompt to Gemini Vision."""
        vision_model = genai.GenerativeModel(settings.gemini_vision_model)
        parts = image_parts + [prompt]
        response = vision_model.generate_content(parts)
        return response.text

    # ──────────────────────────────────────────
    #  JSON extraction
    # ──────────────────────────────────────────

    def _extract_json(self, text: str) -> dict[str, Any]:
        """
        Robustly extract a JSON object from a Gemini response.
        Handles markdown code fences (```json ... ```) and bare JSON.
        """
        # Strip markdown code fences if present
        json_match = re.search(r"```(?:json)?\s*(\{.*?\})\s*```", text, re.DOTALL)
        if json_match:
            return json.loads(json_match.group(1))

        # Try to find a raw JSON object
        obj_match = re.search(r"\{.*\}", text, re.DOTALL)
        if obj_match:
            return json.loads(obj_match.group())

        raise ValueError(f"No valid JSON found in Gemini response:\n{text[:500]}")

    # ──────────────────────────────────────────
    #  Abstract interface
    # ──────────────────────────────────────────

    @abstractmethod
    def run(self, state: Any) -> Any:
        """Execute the agent and return an updated state."""
        ...
