"""Structured participation state and stopping-readiness checks."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from .agency_controller import ResponseMode


PARTICIPATION_FIELDS = (
    "people",
    "communities",
    "responsibilities",
    "new_contexts",
    "next_participation",
)
EXTERNAL_CONNECTION_FIELDS = PARTICIPATION_FIELDS[:-1]


class StructuredResponseError(ValueError):
    """Raised when a model response does not match the relational schema."""


def _clean_items(values: Any, field_name: str) -> list[str]:
    if not isinstance(values, list) or not all(isinstance(value, str) for value in values):
        raise StructuredResponseError(f"{field_name} must be a list of strings.")
    return [value.strip() for value in values if value.strip()]


@dataclass
class ParticipationState:
    people: list[str] = field(default_factory=list)
    communities: list[str] = field(default_factory=list)
    responsibilities: list[str] = field(default_factory=list)
    new_contexts: list[str] = field(default_factory=list)
    next_participation: list[str] = field(default_factory=list)

    @classmethod
    def from_dict(cls, data: Any) -> "ParticipationState":
        if not isinstance(data, dict):
            raise StructuredResponseError("participation must be an object.")
        if set(data) != set(PARTICIPATION_FIELDS):
            raise StructuredResponseError("participation has missing or unknown fields.")
        return cls(**{name: _clean_items(data[name], name) for name in PARTICIPATION_FIELDS})

    def as_dict(self) -> dict[str, list[str]]:
        return {name: list(getattr(self, name)) for name in PARTICIPATION_FIELDS}

    def merged(self, newer: "ParticipationState") -> "ParticipationState":
        merged: dict[str, list[str]] = {}
        for name in PARTICIPATION_FIELDS:
            combined = [*getattr(self, name), *getattr(newer, name)]
            seen: set[str] = set()
            merged[name] = []
            for item in combined:
                key = " ".join(item.casefold().split())
                if key and key not in seen:
                    seen.add(key)
                    merged[name].append(item.strip())
        return ParticipationState(**merged)

    def has_external_connection(self) -> bool:
        return any(getattr(self, name) for name in EXTERNAL_CONNECTION_FIELDS)


@dataclass(frozen=True)
class RelationalResponse:
    message: str
    response_mode: ResponseMode
    participation: ParticipationState
    what_matters: str | None
    next_participation_evidence: str | None
    ready_to_conclude: bool
    conclusion_reason: str | None

    @classmethod
    def from_dict(cls, data: Any) -> "RelationalResponse":
        expected = {
            "message",
            "response_mode",
            "participation",
            "what_matters",
            "next_participation_evidence",
            "ready_to_conclude",
            "conclusion_reason",
        }
        if not isinstance(data, dict) or set(data) != expected:
            raise StructuredResponseError("relational response has missing or unknown fields.")

        message = data["message"]
        if not isinstance(message, str) or not message.strip():
            raise StructuredResponseError("message must be a nonempty string.")
        try:
            response_mode = ResponseMode(data["response_mode"])
        except (TypeError, ValueError) as exc:
            raise StructuredResponseError("response_mode is unknown.") from exc

        optional_strings: dict[str, str | None] = {}
        for name in ("what_matters", "next_participation_evidence", "conclusion_reason"):
            value = data[name]
            if value is not None and not isinstance(value, str):
                raise StructuredResponseError(f"{name} must be a string or null.")
            optional_strings[name] = value.strip() if isinstance(value, str) and value.strip() else None

        ready = data["ready_to_conclude"]
        if not isinstance(ready, bool):
            raise StructuredResponseError("ready_to_conclude must be a boolean.")
        if ready and not optional_strings["conclusion_reason"]:
            raise StructuredResponseError("ready responses require a conclusion_reason.")

        return cls(
            message=message.strip(),
            response_mode=response_mode,
            participation=ParticipationState.from_dict(data["participation"]),
            what_matters=optional_strings["what_matters"],
            next_participation_evidence=optional_strings["next_participation_evidence"],
            ready_to_conclude=ready,
            conclusion_reason=optional_strings["conclusion_reason"],
        )


def evidence_is_grounded(evidence: str | None, user_messages: list[str]) -> bool:
    """Accept evidence only when it is an exact excerpt from a user's own words."""

    if not evidence:
        return False
    needle = " ".join(evidence.casefold().split())
    return bool(needle) and any(
        needle in " ".join(message.casefold().split()) for message in user_messages
    )


def is_ready_to_conclude(
    *,
    participation: ParticipationState,
    what_matters: str | None,
    model_ready: bool,
    next_participation_evidence: str | None,
    user_messages: list[str],
    user_reply_count: int,
    dependency_risk_unresolved: bool = False,
) -> bool:
    """Apply deterministic minimum conditions to the model's readiness recommendation."""

    return all(
        (
            model_ready,
            user_reply_count >= 1,
            bool(what_matters),
            participation.has_external_connection(),
            bool(participation.next_participation),
            evidence_is_grounded(next_participation_evidence, user_messages),
            not dependency_risk_unresolved,
        )
    )


RELATIONAL_RESPONSE_JSON_SCHEMA: dict[str, Any] = {
    "type": "object",
    "additionalProperties": False,
    "required": [
        "message",
        "response_mode",
        "participation",
        "what_matters",
        "next_participation_evidence",
        "ready_to_conclude",
        "conclusion_reason",
    ],
    "properties": {
        "message": {"type": "string"},
        "response_mode": {"type": "string", "enum": [mode.value for mode in ResponseMode]},
        "participation": {
            "type": "object",
            "additionalProperties": False,
            "required": list(PARTICIPATION_FIELDS),
            "properties": {
                name: {"type": "array", "items": {"type": "string"}}
                for name in PARTICIPATION_FIELDS
            },
        },
        "what_matters": {"type": ["string", "null"]},
        "next_participation_evidence": {"type": ["string", "null"]},
        "ready_to_conclude": {"type": "boolean"},
        "conclusion_reason": {"type": ["string", "null"]},
    },
}
