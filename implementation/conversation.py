"""One-turn relational conversation coordination."""

from __future__ import annotations

import json
from dataclasses import dataclass
from enum import Enum

from .agency_controller import ResponseMode
from .openai_client import OpenAIConfigurationError, generate_structured_response
from .participation import (
    ParticipationState,
    RelationalResponse,
    human_reference_from_reply,
    is_ready_to_conclude,
)
from .placeholder_experience import placeholder_relational_turn
from .prompts import RELATIONAL_INSTRUCTIONS


IMPACT_SIGNAL_MARKERS = (
    "stopped going to school", "stopped attending school", "stopped going to work",
    "rarely leave my room", "rarely leave the house", "cannot function", "can't function",
    "not eating", "not sleeping", "neglecting myself", "afraid of", "scared of",
    "coerced", "threatened", "friends are worried", "family is worried",
    "people are worried", "concerned about me", "hurting myself", "harm myself",
)


@dataclass(frozen=True)
class ConversationTurn:
    observation: str
    question: str | None
    participation: ParticipationState
    what_matters: str | None
    next_participation_evidence: str | None
    ready_to_conclude: bool
    response_mode: ResponseMode
    generation_source: str
    generation_notice: str

    @property
    def message(self) -> str:
        return " ".join(part for part in (self.observation, self.question) if part)


class MediatedRelationshipStage(str, Enum):
    """Meaning-first progression for emotionally significant mediated relationships."""

    MEANING = "meaning"
    QUALITIES = "qualities"
    FUTURE_POSSIBILITY = "future_possibility"
    HUMAN_BRIDGE = "human_bridge"
    NEXT_CONVERSATION = "next_conversation"
    IMPACT = "impact"


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


def _states_human_interaction(message: str, people: list[str]) -> bool:
    """Conservatively recognize a user-owned interaction with another person."""

    text = " ".join(message.casefold().split())
    intention = (
        "i will ", "i'll ", "i want to ", "i plan to ", "i'm going to ",
        "i can ", "i could ", "i intend to ",
    )
    interaction = (
        "speak with ", "talk with ", "talk to ", "contact ", "ask ", "invite ",
        "listen to ", "clarify ", "acknowledge ", "request ", "offer ", "tell ",
        "meet with ", "reach out ",
    )
    human_reference = (
        " colleague", " friend", " partner", " manager", " coworker", " co-worker",
        " teammate", " neighbor", " parent", " sibling", " family", " team", " them",
        " him", " her", " person", " people", " someone",
    )
    known_person = any(person.casefold() in text for person in people)
    return (
        any(marker in text for marker in intention)
        and any(marker in text for marker in interaction)
        and (known_person or any(marker in text for marker in human_reference))
    )


def _asks_who_is_involved(question: str | None) -> bool:
    """Recognize questions seeking a person or human group."""

    text = " ".join((question or "").casefold().split())
    return bool(text) and (
        ("who" in text and any(term in text for term in ("involved", "belongs", "shares")))
        or "other person or group" in text
    )


def _previous_assistant_question(messages: list[dict[str, str]]) -> str | None:
    for message in reversed(messages[:-1]):
        if message.get("role") == "assistant":
            return message.get("question") or message.get("content")
    return None


def _has_mediated_relationship(user_messages: list[str]) -> bool:
    text = " ".join(user_messages).casefold()
    entities = (
        " ai", "chatbot", "avatar", "fictional character", "virtual companion",
        "virtual partner", "online community", "digital companion", "character",
    )
    relationship = (
        "attached", "attachment", "relationship", "companion", "companionship",
        "meaningful", "important to me", "care about", "love", "understands me",
    )
    return any(marker in f" {text}" for marker in entities) and any(
        marker in text for marker in relationship
    )


def _has_explicit_impact_or_concern(user_messages: list[str]) -> bool:
    """Detect user-stated harm, impairment, fear, isolation, or outside concern."""

    text = " ".join(user_messages).casefold()
    return any(marker in text for marker in IMPACT_SIGNAL_MARKERS)


def _supported_impact_excerpt(user_messages: list[str], limit: int = 14) -> str:
    """Return a brief user-authored excerpt containing an explicit impact signal."""

    message = next(
        (
            candidate.strip()
            for candidate in reversed(user_messages)
            if any(marker in candidate.casefold() for marker in IMPACT_SIGNAL_MARKERS)
        ),
        user_messages[-1].strip() if user_messages else "",
    )
    words = message.split()
    excerpt = " ".join(words[:limit])
    return f"{excerpt}…" if len(words) > limit else excerpt


def _valued_quality(message: str) -> str | None:
    text = message.casefold()
    qualities = {
        "never judges": "non-judgment",
        "doesn't judge": "non-judgment",
        "does not judge": "non-judgment",
        "understands me": "feeling understood",
        "accepts me": "acceptance",
        "always there": "reliability",
        "feels safe": "safety",
    }
    return next((label for marker, label in qualities.items() if marker in text), None)


def _accepts_mediated_relationship(message: str) -> bool:
    text = message.casefold()
    return (
        any(marker in text for marker in ("i am happy", "i'm happy", "feels right to me"))
        and any(marker in text for marker in ("do not want to change", "don't want to change", "not want to change"))
    )


def _mediated_relationship_stage(
    messages: list[dict[str, str]],
    participation: ParticipationState,
) -> MediatedRelationshipStage | None:
    user_messages = [m["content"] for m in messages if m.get("role") == "user"]
    if not _has_mediated_relationship(user_messages):
        return None
    if _has_explicit_impact_or_concern(user_messages):
        return MediatedRelationshipStage.IMPACT

    assistant_questions = " ".join(
        (m.get("question") or m.get("content") or "").casefold()
        for m in messages
        if m.get("role") == "assistant"
    )
    latest = user_messages[-1] if user_messages else ""
    if _states_human_interaction(latest, participation.people):
        return MediatedRelationshipStage.NEXT_CONVERSATION
    if participation.people:
        return MediatedRelationshipStage.HUMAN_BRIDGE
    if _valued_quality(latest):
        return MediatedRelationshipStage.FUTURE_POSSIBILITY
    if any(term in assistant_questions for term in ("meaningful", "give you", "feels important")):
        return MediatedRelationshipStage.QUALITIES
    return MediatedRelationshipStage.MEANING


def _guard_mediated_response(
    *,
    stage: MediatedRelationshipStage | None,
    user_messages: list[str],
    latest_user_message: str,
    observation: str,
    question: str | None,
) -> tuple[str, str | None]:
    """Apply deterministic, non-diagnostic stage progression to generated responses."""

    if stage is None:
        return observation, question
    if stage == MediatedRelationshipStage.IMPACT:
        excerpt = _supported_impact_excerpt(user_messages)
        return (
            f"You described “{excerpt}”; this may be having an impact that is important to understand.",
            "What effect, if any, is this having on your daily life or ability to care for yourself?",
        )
    if _accepts_mediated_relationship(latest_user_message):
        return (
            "You are clear that this relationship matters to you and that you do not want to replace it.",
            "Is there anyone you would like to understand this part of you better, or does none feel right?",
        )
    if stage == MediatedRelationshipStage.MEANING:
        return (
            "Your relationship with this mediated companion feels emotionally significant to you.",
            "What feels meaningful about this relationship?",
        )
    quality = _valued_quality(latest_user_message)
    if stage == MediatedRelationshipStage.FUTURE_POSSIBILITY and quality:
        return (
            f"Being met with {quality} is an important quality of this relationship.",
            "What kind of relationship might become possible if more of that quality were present?",
        )
    return observation, question


def _turn_instructions(
    response_mode: ResponseMode,
    participation: ParticipationState,
    what_matters: str | None,
    response_cycle: int,
    messages: list[dict[str, str]],
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
    previous_turns = [
        {
            "observation": message.get("observation"),
            "question": message.get("question"),
        }
        for message in messages
        if message.get("role") == "assistant"
    ][-4:]
    return (
        f"{RELATIONAL_INSTRUCTIONS}\n\n"
        f"Use response_mode {response_mode.value!r}. Current accumulated state: {state}. "
        f"Recent assistant turns: {json.dumps(previous_turns, ensure_ascii=False)}. "
        "Do not repeat or closely paraphrase an earlier observation or question. The "
        "question must respond directly to the latest user message and advance one step. "
        f"{pacing} Return only observations newly supported by the conversation; the "
        "application will merge them with accumulated state."
    )


def _normalized(text: str | None) -> str:
    return " ".join((text or "").casefold().split()).rstrip("?.!")


def _avoid_repetition(
    *,
    messages: list[dict[str, str]],
    latest_user_message: str,
    participation: ParticipationState,
    observation: str,
    question: str | None,
) -> tuple[str, str | None]:
    """Replace exact repeats with grounded, tentative language that advances the exchange."""

    previous_observations = {
        _normalized(message.get("observation") or message.get("content"))
        for message in messages
        if message.get("role") == "assistant"
    }
    previous_questions = {
        _normalized(message.get("question"))
        for message in messages
        if message.get("role") == "assistant" and message.get("question")
    }
    if _normalized(observation) in previous_observations:
        excerpt = " ".join(latest_user_message.split()[:10])
        suffix = "…" if len(latest_user_message.split()) > 10 else ""
        observation = (
            f"Your words—“{excerpt}{suffix}”—may be bringing a relational possibility "
            "into clearer view."
        )
    if question and _normalized(question) in previous_questions:
        if participation.next_participation:
            question = "What feels worth carrying into your life beyond this conversation?"
        elif participation.people or participation.communities:
            question = "What feels newly possible in how you might meet this relationship?"
        else:
            question = "Who else might be touched by what is beginning to matter here?"
    return observation, question


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
        response_mode, participation, what_matters, response_cycle, messages
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
    latest_user_message = _latest_user_message(messages).strip()
    human_reference = human_reference_from_reply(latest_user_message)
    answered_who_question = (
        _asks_who_is_involved(_previous_assistant_question(messages))
        and bool(human_reference)
    )
    if human_reference:
        merged = merged.merged(ParticipationState(people=[human_reference]))
    user_named_interaction = _states_human_interaction(latest_user_message, merged.people)
    if user_named_interaction:
        merged = merged.merged(
            ParticipationState(next_participation=[latest_user_message])
        )
        current_evidence = latest_user_message
    ready = is_ready_to_conclude(
        participation=merged,
        what_matters=current_what_matters,
        model_ready=response.ready_to_conclude or user_named_interaction,
        next_participation_evidence=current_evidence,
        user_messages=user_messages,
        user_reply_count=user_reply_count,
        dependency_risk_unresolved=unresolved_risk,
    )
    guarded_question = (
        None
        if ready
        else "What feels most significant about your experience with these people?"
        if answered_who_question and _asks_who_is_involved(response.question)
        else response.question
    )
    stage = _mediated_relationship_stage(messages, merged)
    guarded_observation, guarded_question = _guard_mediated_response(
        stage=stage,
        user_messages=user_messages,
        latest_user_message=latest_user_message,
        observation=response.observation,
        question=guarded_question,
    )
    guarded_observation, guarded_question = _avoid_repetition(
        messages=messages,
        latest_user_message=latest_user_message,
        participation=merged,
        observation=guarded_observation,
        question=None if ready else guarded_question,
    )

    return ConversationTurn(
        observation=guarded_observation,
        question=None if ready else guarded_question,
        participation=merged,
        what_matters=current_what_matters,
        next_participation_evidence=current_evidence,
        ready_to_conclude=ready,
        response_mode=response_mode,
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
    return any(marker in text for marker in markers) or _has_explicit_impact_or_concern(user_messages)
