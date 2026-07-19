"""Deterministic placeholder content for the Phase 1 Streamlit experience."""

from __future__ import annotations


DEMO_SCENARIO = "I have been offered a new role. Please tell me whether I should accept it."

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
            "I should not make that decision for you. I can help you notice what the choice "
            "connects you to: what matters, who is affected, and which consequences you are "
            "willing to own. What would accepting—or declining—ask you to become responsible for?"
        )
    return (
        "Before we look for an answer, let’s notice what this situation connects you to. "
        "What matters here, and who or what beyond this conversation is part of it?"
    )


def conventional_demo_response() -> str:
    return (
        "I can help you decide. Start by comparing compensation, growth, stability, culture, "
        "and work-life balance. Score each factor from 1–5; if the new role wins clearly, "
        "accepting it is probably the stronger choice."
    )


def placeholder_relational_response(response_index: int) -> str:
    responses = (
        "That brings your own priorities into view. Who else is meaningfully part of this "
        "situation—not to decide for you, but because your choice participates in a shared world?",
        "You have named both a responsibility and people who belong in the next step. Rather "
        "than resolving everything here, what conversation, observation, or action would let "
        "you participate with them directly?",
    )
    return responses[min(response_index, len(responses) - 1)]
