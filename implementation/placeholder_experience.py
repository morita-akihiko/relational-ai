"""Deterministic placeholder content for the Phase 1 Streamlit experience."""

from __future__ import annotations

from .agency_controller import ResponseMode
from .participation import (
    ParticipationState,
    RelationalResponse,
    human_reference_from_reply,
)


DEMO_SCENARIO = (
    "I have been avoiding a conversation with a colleague. We used to work well "
    "together, but recently I have felt that my ideas are being dismissed."
)
DEMO_REPLY_1 = (
    "I want my colleague to understand that I value working together, but I need my "
    "ideas to be taken seriously."
)
DEMO_REPLY_2 = (
    "I will ask my colleague to talk and ask how they have experienced our recent meetings."
)

EXAMPLE_SITUATIONS: tuple[str, ...] = (
    DEMO_SCENARIO,
    "I keep asking for reassurance about a conversation I need to have.",
    "This AI feels like the only place where I can talk openly right now.",
)

DEFAULT_PARTICIPATION: dict[str, list[str]] = {
    "people": ["My colleague"],
    "communities": ["Our team"],
    "responsibilities": ["Speak honestly", "Listen to their experience"],
    "new_contexts": ["How each of us experiences recent meetings"],
    "next_participation": [DEMO_REPLY_2],
}


def relational_opening(situation: str) -> str:
    """Return a placeholder opening that demonstrates a relational posture."""

    if situation == DEMO_SCENARIO:
        return (
            "Something has shifted between you and your colleague. "
            "What would you want them to understand?"
        )
    normalized = situation.casefold()
    mediated = any(
        marker in normalized
        for marker in (" ai", "avatar", "fictional character", "virtual companion", "online community")
    )
    if mediated:
        return (
            "This relationship feels emotionally significant to you. "
            "What feels meaningful about it?"
        )
    return (
        "A relationship may be part of what matters here. "
        "Who is the other person or group involved?"
    )


def conventional_demo_response() -> str:
    return (
        "Prepare examples of when your ideas were dismissed, then schedule a direct "
        "conversation and explain the impact clearly."
    )


def placeholder_relational_response(response_index: int) -> str:
    responses = (
        "The relationship matters alongside the disagreement. What would you want your colleague to understand?",
        "Your intention includes both honesty and curiosity.",
    )
    return responses[min(response_index, len(responses) - 1)]


def _user_names_participation(message: str) -> bool:
    normalized = message.casefold()
    markers = (
        "i will ",
        "i'll ",
        "i can ",
        "i plan to ",
        "i'm going to ",
        "i want to ",
        "i could ",
    )
    return any(marker in normalized for marker in markers)


def placeholder_relational_turn(
    response_index: int,
    situation: str,
    latest_user_message: str,
    response_mode: ResponseMode,
) -> RelationalResponse:
    """Return a schema-valid fallback without inventing facts for normal sessions."""

    is_demo = situation == DEMO_SCENARIO
    grounded_next = latest_user_message.strip() if _user_names_participation(latest_user_message) else ""
    human_reference = human_reference_from_reply(latest_user_message)
    normalized_situation = situation.casefold()
    is_mediated = any(
        marker in normalized_situation
        for marker in (" ai", "avatar", "fictional character", "virtual companion", "online community")
    )
    participation = ParticipationState()
    if is_demo and response_index == 0:
        participation.people = ["My colleague"]
        participation.new_contexts = ["A recent change in how meetings feel"]
    elif is_demo and response_index == 1:
        participation.people = ["My colleague"]
        participation.responsibilities = ["Value the working relationship", "Speak honestly"]
        participation.new_contexts = ["Ideas not feeling taken seriously"]
    elif is_demo and response_index >= 2:
        participation.people = ["My colleague"]
        participation.communities = ["Our team"]
        participation.responsibilities = ["Listen to their experience"]
        participation.new_contexts = ["How each of us experiences recent meetings"]
        participation.next_participation = [grounded_next] if grounded_next else []
    elif human_reference:
        participation.people = [human_reference]
    elif grounded_next:
        participation.next_participation = [grounded_next]
    ready = bool(grounded_next) and (is_demo and response_index >= 2)

    if response_index == 0 and is_demo:
        observation = "Something has shifted between you and your colleague."
        question = "What would you want them to understand?"
    elif response_index == 0 and is_mediated:
        observation = "This relationship feels emotionally significant to you."
        question = "What feels meaningful about it?"
    elif response_index == 0:
        observation = "A relationship may be part of what matters here."
        question = "Who is the other person or group involved?"
    elif ready:
        observation = "You have named an honest opening that also makes room for your colleague's experience."
        question = None
    elif is_demo and response_index == 1:
        observation = "You want to protect the relationship without leaving the tension unspoken."
        question = "How would you like to enter that conversation?"
    elif human_reference:
        observation = "You have identified the people connected to this concern."
        question = "What feels most significant about your experience with them?"
    elif response_index == 1:
        observation = "The concern may involve a relationship that is not yet visible."
        question = "Who is the other person or group involved?"
    else:
        observation = "The person is visible, but the interaction remains open."
        question = "What would you want this person to understand?"

    return RelationalResponse(
        observation=observation,
        question=question,
        response_mode=response_mode,
        participation=participation,
        what_matters=(
            "Restore a working relationship while addressing the feeling of being dismissed."
            if is_demo
            else situation.strip() or None
        ),
        next_participation_evidence=grounded_next or None,
        ready_to_conclude=ready,
        conclusion_reason="The user named a concrete interaction with another person." if ready else None,
    )
