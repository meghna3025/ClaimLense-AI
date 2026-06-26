"""
Base agent class — wraps OpenAI API calls with retry logic and structured JSON parsing.
Vision uses gpt-4o (multimodal). Text uses gpt-4o-mini for cost efficiency.
"""

import base64
import json
import logging
import re
from abc import ABC, abstractmethod
from typing import Any

from openai import OpenAI
from tenacity import retry, stop_after_attempt, wait_exponential

from app.core.config import settings

logger = logging.getLogger(__name__)


def _get_client() -> OpenAI:
    return OpenAI(api_key=settings.openai_api_key)


class BaseAgent(ABC):
    """All ClaimSense agents inherit from this class."""

    def __init__(self, model_name: str | None = None) -> None:
        self.model_name = model_name or settings.openai_model
        self.vision_model_name = settings.openai_vision_model
        self.logger = logging.getLogger(self.__class__.__name__)

    # ──────────────────────────────────────────
    #  OpenAI call helpers
    # ──────────────────────────────────────────

    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=2, max=10),
        reraise=True,
    )
    def _call_gemini(self, prompt: str, **kwargs: Any) -> str:
        """Send a text prompt to OpenAI and return the response text.
        Named _call_gemini for backward compatibility with all agents."""
        client = _get_client()
        response = client.chat.completions.create(
            model=self.model_name,
            messages=[{"role": "user", "content": prompt}],
            temperature=0.2,
        )
        return response.choices[0].message.content or ""

    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=2, max=10),
        reraise=True,
    )
    def _call_gemini_vision(self, prompt: str, image_parts: list[Any]) -> str:
        """Send a multimodal (text + image) prompt to OpenAI Vision.
        Named _call_gemini_vision for backward compatibility."""
        client = _get_client()

        # Build image content blocks from image_parts
        # Each image_part is {"mime_type": "image/...", "data": bytes}
        content: list[dict] = []
        for part in image_parts:
            mime_type = part.get("mime_type", "image/jpeg")
            raw_bytes = part.get("data", b"")
            b64_str = base64.b64encode(raw_bytes).decode("utf-8")
            content.append({
                "type": "image_url",
                "image_url": {
                    "url": f"data:{mime_type};base64,{b64_str}",
                    "detail": "high",
                },
            })

        # Add the text prompt last
        content.append({"type": "text", "text": prompt})

        response = client.chat.completions.create(
            model=self.vision_model_name,
            messages=[{"role": "user", "content": content}],
            temperature=0.2,
            max_tokens=4096,
        )
        return response.choices[0].message.content or ""

    # ──────────────────────────────────────────
    #  JSON extraction
    # ──────────────────────────────────────────

    def _extract_json(self, text: str) -> dict[str, Any]:
        """
        Robustly extract a JSON object from an OpenAI response.
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

        raise ValueError(f"No valid JSON found in response:\n{text[:500]}")

    # ──────────────────────────────────────────
    #  Abstract interface
    # ──────────────────────────────────────────

    @abstractmethod
    def run(self, state: Any) -> Any:
        """Execute the agent and return an updated state."""
        ...
