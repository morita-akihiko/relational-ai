"""Small, direct wrapper around the OpenAI Responses API."""

from __future__ import annotations

import os
from typing import Any

from openai import OpenAI


DEFAULT_MODEL = "gpt-5.6-sol"


class OpenAIConfigurationError(RuntimeError):
    """Raised when live generation has not been configured."""


def api_key_from_environment() -> str | None:
    return os.getenv("OPENAI_API_KEY")


def generate_response(
    instructions: str,
    messages: list[dict[str, str]],
    *,
    api_key: str | None = None,
    model: str | None = None,
) -> str:
    """Generate one text response while keeping the SDK boundary visible."""

    resolved_key = api_key or api_key_from_environment()
    if not resolved_key:
        raise OpenAIConfigurationError("OPENAI_API_KEY is not configured.")

    client = OpenAI(api_key=resolved_key)
    response: Any = client.responses.create(
        model=model or os.getenv("OPENAI_MODEL", DEFAULT_MODEL),
        instructions=instructions,
        input=messages,
    )
    text = response.output_text.strip()
    if not text:
        raise RuntimeError("The OpenAI response did not contain displayable text.")
    return text
