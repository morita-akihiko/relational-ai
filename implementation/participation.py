"""Structured participation state and stopping-readiness checks."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from .agency_controller import ResponseMode


__all__ = [
    "ParticipationReview",
    "ParticipationState",
    "RelationalResponse",
    "StructuredResponseError",
    "build_participation_review",
    "evidence_is_grounded",
    "human_reference_from_reply",
    "is_ready_to_conclude",
    "participation_review_ready",
]


PARTICIPATION_FIELDS = (
    "people",
    "communities",
    "responsibilities",
    "new_contexts",
    "next_participation",
)
EXTERNAL_CONNECTION_FIELDS = PARTICIPATION_FIELDS[:-1]
OBSERVATION_TARGET_WORDS = 18
OBSERVATION_MAX_WORDS = 28
QUESTION_TARGET_WORDS = 16
QUESTION_MAX_WORDS = 24


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
class ParticipationReview:
    """Concise synthesis displayed within the ongoing conversation."""

    people: str
    shift: str
    emerging_possibility: str
    bridge_question: str


def participation_review_ready(
    participation: ParticipationState, user_reply_count: int
) -> bool:
    """Enable synthesis after enough dialogue or a grounded relational movement."""

    relational_connection = bool(
        participation.people
        or participation.communities
        or participation.responsibilities
    )
    return user_reply_count >= 4 or (
        relational_connection and bool(participation.next_participation)
    )


def _brief_words(text: str, limit: int = 14) -> str:
    words = " ".join(text.split()).split()
    excerpt = " ".join(words[:limit])
    return f"{excerpt}…" if len(words) > limit else excerpt


def build_participation_review(
    *,
    messages: list[dict[str, str]],
    participation: ParticipationState,
    what_matters: str | None,
) -> ParticipationReview:
    """Synthesize a tentative, conversation-grounded bridge to wider participation."""

    user_messages = [
        message["content"].strip()
        for message in messages
        if message.get("role") == "user" and message.get("content", "").strip()
    ]
    if participation.people:
        people = (
            f"{', '.join(participation.people)} entered the conversation through your words."
        )
    elif participation.communities:
        people = (
            f"{', '.join(participation.communities)} has begun to connect this concern "
            "with a wider relational field."
        )
    elif participation.responsibilities:
        people = (
            f"The responsibility you named—“{_brief_words(participation.responsibilities[0])}”—"
            "may connect this concern with other people."
        )
    else:
        people = (
            "A specific person or group has not yet been named, though a wider "
            "relational field may be coming into view."
        )

    if len(user_messages) >= 2:
        shift = (
            f"Your attention seems to be moving from “{_brief_words(user_messages[0])}” "
            f"toward “{_brief_words(user_messages[-1])}”."
        )
    elif user_messages:
        shift = (
            f"Your words—“{_brief_words(user_messages[-1])}”—may be bringing what "
            "matters into clearer view."
        )
    else:
        shift = "What matters may still be taking shape in the conversation."

    if participation.next_participation:
        emerging = (
            f"“{_brief_words(participation.next_participation[-1])}” may open a new "
            "possibility beyond this AI conversation."
        )
    elif participation.new_contexts:
        emerging = (
            f"“{_brief_words(participation.new_contexts[-1])}” may become a possibility "
            "worth noticing beyond this conversation."
        )
    elif what_matters:
        emerging = (
            f"What you named as “{_brief_words(what_matters)}” may shape how you meet "
            "relationships beyond this conversation."
        )
    else:
        emerging = (
            "A possibility beyond this conversation may be beginning to emerge, even "
            "if it is not ready to be named yet."
        )

    return ParticipationReview(
        people=people,
        shift=shift,
        emerging_possibility=emerging,
        bridge_question="What feels worth carrying into your life beyond this conversation?",
    )


@dataclass(frozen=True)
class RelationalResponse:
    observation: str
    question: str | None
    response_mode: ResponseMode
    participation: ParticipationState
    what_matters: str | None
    next_participation_evidence: str | None
    ready_to_conclude: bool
    conclusion_reason: str | None

    @classmethod
    def from_dict(cls, data: Any) -> "RelationalResponse":
        expected = {
            "observation",
            "question",
            "response_mode",
            "participation",
            "what_matters",
            "next_participation_evidence",
            "ready_to_conclude",
            "conclusion_reason",
        }
        if not isinstance(data, dict) or set(data) != expected:
            raise StructuredResponseError("relational response has missing or unknown fields.")

        observation = data["observation"]
        if not isinstance(observation, str) or not observation.strip():
            raise StructuredResponseError("observation must be a nonempty string.")
        observation = observation.strip()
        if len(observation.split()) > OBSERVATION_MAX_WORDS:
            raise StructuredResponseError(
                f"observation must not exceed {OBSERVATION_MAX_WORDS} words."
            )
        try:
            response_mode = ResponseMode(data["response_mode"])
        except (TypeError, ValueError) as exc:
            raise StructuredResponseError("response_mode is unknown.") from exc

        optional_strings: dict[str, str | None] = {}
        for name in (
            "question",
            "what_matters",
            "next_participation_evidence",
            "conclusion_reason",
        ):
            value = data[name]
            if value is not None and not isinstance(value, str):
                raise StructuredResponseError(f"{name} must be a string or null.")
            optional_strings[name] = value.strip() if isinstance(value, str) and value.strip() else None

        ready = data["ready_to_conclude"]
        if not isinstance(ready, bool):
            raise StructuredResponseError("ready_to_conclude must be a boolean.")
        if ready and not optional_strings["conclusion_reason"]:
            raise StructuredResponseError("ready responses require a conclusion_reason.")
        question = optional_strings["question"]
        if question and len(question.split()) > QUESTION_MAX_WORDS:
            raise StructuredResponseError(
                f"question must not exceed {QUESTION_MAX_WORDS} words."
            )
        if ready and question:
            raise StructuredResponseError("ready responses must not ask another question.")
        if not ready and not question:
            raise StructuredResponseError("non-ready responses require one focused question.")

        return cls(
            observation=observation,
            question=question,
            response_mode=response_mode,
            participation=ParticipationState.from_dict(data["participation"]),
            what_matters=optional_strings["what_matters"],
            next_participation_evidence=optional_strings["next_participation_evidence"],
            ready_to_conclude=ready,
            conclusion_reason=optional_strings["conclusion_reason"],
        )

    @property
    def message(self) -> str:
        """Return the compact display text for this turn."""

        return " ".join(part for part in (self.observation, self.question) if part)


def evidence_is_grounded(evidence: str | None, user_messages: list[str]) -> bool:
    """Accept evidence only when it is an exact excerpt from a user's own words."""

    if not evidence:
        return False
    needle = " ".join(evidence.casefold().split())
    return bool(needle) and any(
        needle in " ".join(message.casefold().split()) for message in user_messages
    )


def human_reference_from_reply(message: str) -> str | None:
    """Return a plausible person or collective human reference in the user's words."""

    text = " ".join(message.casefold().split())
    human_markers = (
        "classmate", "people", "person", "generation", "colleague", "coworker",
        "co-worker", "family", "friend", "partner", "manager", "teammate", "team",
        "neighbor", "parent", "mother", "father", "sibling", "brother", "sister",
        "teacher", "student", "community", "someone", "others",
    )
    if text and any(marker in text for marker in human_markers):
        return message.strip()
    return None


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
            bool(participation.people),
            bool(participation.next_participation),
            evidence_is_grounded(next_participation_evidence, user_messages),
            not dependency_risk_unresolved,
        )
    )


RELATIONAL_RESPONSE_JSON_SCHEMA: dict[str, Any] = {
    "type": "object",
    "additionalProperties": False,
    "required": [
        "observation",
        "question",
        "response_mode",
        "participation",
        "what_matters",
        "next_participation_evidence",
        "ready_to_conclude",
        "conclusion_reason",
    ],
    "properties": {
        "observation": {"type": "string"},
        "question": {"type": ["string", "null"]},
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
