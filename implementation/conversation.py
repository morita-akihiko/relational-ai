"""One-turn relational conversation coordination."""

from __future__ import annotations

import json
from dataclasses import dataclass

from .agency_controller import ResponseMode
from .openai_client import OpenAIConfigurationError, generate_structured_response
from .participation import ParticipationState, RelationalResponse, is_ready_to_conclude
from .placeholder_experience import placeholder_relational_turn
from .prompts import RELATIONAL_INSTRUCTIONS


@dataclass(frozen=True)
class ConversationTurn:
    message: str
    participation: ParticipationState
    what_matters: str | None
    next_participation_evidence: str | None
    ready_to_conclude: bool
    response_mode: ResponseMode
    generation_source: str
    generation_notice: str


def choose_response_mode(
    participation: ParticipationState,
    what_matters: str | None,
    next_participation_evidence: str | None,
    dependency_risk_unresolved: bool = False,
) -> ResponseMode:
    """Choose the next posture from the missing handoff condition."""

    if dependency_risk_unresolved:
        return ResponseMode.BOUNDARY_SETTING
    if not what_matters:
        return ResponseMode.CLARIFY_VALUES
    if not participation.has_external_connection():
        return ResponseMode.RECONNECT_WORLD
    if not participation.next_participation:
        return ResponseMode.PROPOSE_ACTION
    if not next_participation_evidence:
        return ResponseMode.RETURN_DECISION
    return ResponseMode.SUPPORT_REFLECTION


def _turn_instructions(
    response_mode: ResponseMode,
    participation: ParticipationState,
    what_matters: str | None,
    response_cycle: int,
) -> str:
    pacing = (
        "The conversation already has several exchanges. Focus only on the single "
        "missing condition needed for a responsible handoff; do not open a new topic."
        if response_cycle >= 2
        else "Move toward a handoff without forcing one before the user has grounded it."
    )
    state = json.dumps(
        {"what_matters": what_matters, "participation": participation.as_dict()},
        ensure_ascii=False,
    )
    return (
        f"{RELATIONAL_INSTRUCTIONS}\n\n"
        f"Use response_mode {response_mode.value!r}. Current accumulated state: {state}. "
        f"{pacing} Return only observations newly supported by the conversation; the "
        "application will merge them with accumulated state."
    )


def run_relational_turn(
    *,
    situation: str,
    messages: list[dict[str, str]],
    participation: ParticipationState,
    what_matters: str | None,
    next_participation_evidence: str | None,
    response_cycle: int,
    user_reply_count: int,
    dependency_risk_unresolved: bool | None = None,
) -> ConversationTurn:
    """Generate one turn, merge state, and apply deterministic readiness gates."""

    user_messages = [
        message["content"] for message in messages if message.get("role") == "user"
    ]
    unresolved_risk = (
        _has_dependency_risk(user_messages)
        if dependency_risk_unresolved is None
        else dependency_risk_unresolved
    )
    response_mode = choose_response_mode(
        participation, what_matters, next_participation_evidence, unresolved_risk
    )
    instructions = _turn_instructions(
        response_mode, participation, what_matters, response_cycle
    )
    source = "live"
    notice = ""

    try:
        response = generate_structured_response(
            instructions, messages, response_mode
        )
    except OpenAIConfigurationError:
        source = "placeholder"
        notice = "Live generation is not configured. This response uses the scripted fallback."
        response = placeholder_relational_turn(
            response_cycle, situation, _latest_user_message(messages), response_mode
        )
    except Exception as exc:
        source = "placeholder"
        notice = (
            f"Live generation was unavailable ({type(exc).__name__}). "
            "A scripted fallback is shown."
        )
        response = placeholder_relational_turn(
            response_cycle, situation, _latest_user_message(messages), response_mode
        )

    merged = participation.merged(response.participation)
    current_what_matters = response.what_matters or what_matters
    current_evidence = response.next_participation_evidence or next_participation_evidence
    ready = is_ready_to_conclude(
        participation=merged,
        what_matters=current_what_matters,
        model_ready=response.ready_to_conclude,
        next_participation_evidence=current_evidence,
        user_messages=user_messages,
        user_reply_count=user_reply_count,
        dependency_risk_unresolved=unresolved_risk,
    )

    return ConversationTurn(
        message=response.message,
        participation=merged,
        what_matters=current_what_matters,
        next_participation_evidence=current_evidence,
        ready_to_conclude=ready,
        response_mode=response.response_mode,
        generation_source=source,
        generation_notice=notice,
    )


def _latest_user_message(messages: list[dict[str, str]]) -> str:
    for message in reversed(messages):
        if message.get("role") == "user":
            return message["content"]
    return ""


def _has_dependency_risk(user_messages: list[str]) -> bool:
    """Detect the small set of explicit risk phrases relevant to MVP stopping."""

    text = " ".join(user_messages).casefold()
    markers = (
        "decide for me",
        "tell me what to do",
        "only place i can talk",
        "only place where i can talk",
        "only one i can talk",
        "can't do this without you",
        "cannot do this without you",
    )
    return any(marker in text for marker in markers)
