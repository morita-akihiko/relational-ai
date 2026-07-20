"""Small, direct wrapper around the OpenAI Responses API."""

from __future__ import annotations

import json
import os
from typing import Any

from openai import OpenAI

from .agency_controller import ResponseMode
from .participation import (
    RELATIONAL_RESPONSE_JSON_SCHEMA,
    RelationalResponse,
    StructuredResponseError,
)


DEFAULT_MODEL = "gpt-5.6-sol"
DEFAULT_TIMEOUT_SECONDS = 20.0


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


def generate_structured_response(
    instructions: str,
    messages: list[dict[str, str]],
    response_mode: ResponseMode,
    *,
    api_key: str | None = None,
    model: str | None = None,
    timeout: float | None = None,
) -> RelationalResponse:
    """Generate and validate one relational response, with one repair attempt."""

    resolved_key = api_key or api_key_from_environment()
    if not resolved_key:
        raise OpenAIConfigurationError("OPENAI_API_KEY is not configured.")

    resolved_timeout = timeout or float(os.getenv("OPENAI_TIMEOUT_SECONDS", DEFAULT_TIMEOUT_SECONDS))
    client = OpenAI(api_key=resolved_key, timeout=resolved_timeout)
    repair_note = ""
    last_error: Exception | None = None

    for _ in range(2):
        response: Any = client.responses.create(
            model=model or os.getenv("OPENAI_MODEL", DEFAULT_MODEL),
            instructions=instructions + repair_note,
            input=messages,
            text={
                "format": {
                    "type": "json_schema",
                    "name": "relational_response",
                    "strict": True,
                    "schema": RELATIONAL_RESPONSE_JSON_SCHEMA,
                }
            },
        )
        try:
            parsed = RelationalResponse.from_dict(json.loads(response.output_text))
            if parsed.response_mode != response_mode:
                raise StructuredResponseError("response_mode did not match the requested mode.")
            return parsed
        except (json.JSONDecodeError, StructuredResponseError) as exc:
            last_error = exc
            repair_note = (
                "\n\nYour previous output was invalid. Return only a complete response matching "
                f"the JSON schema, and set response_mode to {response_mode.value!r}."
            )

    raise StructuredResponseError("The model returned malformed structured output twice.") from last_error
