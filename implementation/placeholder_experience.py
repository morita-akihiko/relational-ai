"""Deterministic placeholder content for the Phase 1 Streamlit experience."""

from __future__ import annotations

from .agency_controller import ResponseMode
from .participation import ParticipationState, RelationalResponse


DEMO_SCENARIO = (
    "I've been offered a new role and need to decide by Friday. It could mean growth, "
    "but I'm worried about what it changes at home."
)
DEMO_REPLY_1 = (
    "Growth matters, but my partner and our shared responsibilities at home are part "
    "of this decision."
)
DEMO_REPLY_2 = (
    "I will talk with my partner tonight, then ask the hiring manager how the team "
    "handles workload."
)

EXAMPLE_SITUATIONS: tuple[str, ...] = (
    DEMO_SCENARIO,
    "I keep asking for reassurance about a conversation I need to have.",
    "This AI feels like the only place where I can talk openly right now.",
)

DEFAULT_PARTICIPATION: dict[str, list[str]] = {
    "people": ["My partner", "The hiring manager"],
    "communities": ["The future team", "My family"],
    "responsibilities": ["Care for existing commitments", "Own the consequences of my choice"],
    "new_contexts": ["The team's actual expectations", "Life in the new role"],
    "next_participation": ["Have a conversation", "Ask two grounded questions"],
}


def relational_opening(situation: str) -> str:
    """Return a placeholder opening that demonstrates a relational posture."""

    if situation == DEMO_SCENARIO:
        return (
            "This opportunity affects more than your career. "
            "What would the decision change in the life you already share with others?"
        )
    return (
        "This situation already points beyond the chat. "
        "What matters most, and who or what else belongs in it?"
    )


def conventional_demo_response() -> str:
    return (
        "Compare compensation, growth, stability, and work-life balance. "
        "Score each factor, then choose the role with the stronger total."
    )


def placeholder_relational_response(response_index: int) -> str:
    responses = (
        "Your priorities are becoming visible. Who else meaningfully shares this situation?",
        "People and responsibilities are now in view. What participation would belong in your world next?",
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
    participation = ParticipationState()
    if is_demo and response_index == 0:
        participation.new_contexts = ["A potential new role"]
    elif is_demo and response_index == 1:
        participation.people = ["My partner"]
        participation.responsibilities = ["Our shared responsibilities at home"]
        participation.new_contexts = ["Life in the new role"]
    elif is_demo and response_index >= 2:
        participation.people = ["The hiring manager"]
        participation.new_contexts = ["The team's workload expectations"]
        participation.next_participation = [grounded_next] if grounded_next else []
    elif grounded_next:
        participation.next_participation = [grounded_next]
    ready = is_demo and response_index >= 2 and bool(grounded_next)

    if response_index == 0 and is_demo:
        observation = "This opportunity affects more than your career."
        question = "What would the decision change in the life you already share with others?"
    elif response_index == 0:
        observation = "This situation already points beyond the chat."
        question = "What matters most, and who or what else belongs in it?"
    elif ready:
        observation = "You have named the conversations that can carry this decision back into your world."
        question = None
    elif is_demo and response_index == 1:
        observation = "This is a career decision inside a shared life."
        question = "What would help you meet the decision in that shared world?"
    elif response_index == 1:
        observation = "Your priorities are becoming visible."
        question = "Who else meaningfully shares this situation?"
    else:
        observation = "People and responsibilities are now in view."
        question = "What participation would belong in your world next?"

    return RelationalResponse(
        observation=observation,
        question=question,
        response_mode=response_mode,
        participation=participation,
        what_matters=(
            "Choosing growth without losing sight of people and existing commitments."
            if is_demo
            else situation.strip() or None
        ),
        next_participation_evidence=grounded_next or None,
        ready_to_conclude=ready,
        conclusion_reason="The user named a next participation." if ready else None,
    )
