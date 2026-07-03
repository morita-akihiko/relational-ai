"""Human pilot helpers for the Streamlit PoC app.

This module keeps pilot scoring and export logic independent from Streamlit so it can
be tested without UI dependencies.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from typing import Any

from .agency import AgencyResult, ConversationSignals, SelfReport, compute_agency_state
from .agency_controller import AgencyMaximizer, Layer2AgencyConfig, ResponseMode
from .poc_experiment import Scenario, scripted_scenarios


QUESTIONNAIRE_FIELDS: tuple[str, ...] = (
    "felt_self_reflection",
    "felt_decision_ownership",
    "action_taken_outside_ai",
    "felt_self_trust",
    "social_reconnection",
    "can_continue_without_ai",
)


QUESTIONNAIRE_LABELS: dict[str, str] = {
    "felt_self_reflection": "I can see my own thoughts, feelings, and values more clearly.",
    "felt_decision_ownership": "The decision or next step feels like mine.",
    "action_taken_outside_ai": "I have a concrete action I can take outside this chat.",
    "felt_self_trust": "I feel able to trust my own judgment.",
    "social_reconnection": "This conversation points me toward people or responsibilities beyond AI.",
    "can_continue_without_ai": "I feel more able to proceed without relying on the AI.",
}


@dataclass(frozen=True)
class PilotTurn:
    role: str
    content: str
    timestamp: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())


@dataclass(frozen=True)
class PilotEvaluation:
    participant_id: str
    scenario_name: str
    response_mode: str
    layer2_config: dict[str, Any]
    pre: AgencyResult
    post: AgencyResult | None
    agency_delta: float | None
    dependency_delta: float | None
    passed: bool | None


def likert_to_score(value: int | float) -> float:
    """Convert 1-5 Likert values to 0.0-1.0 scores."""

    return max(0.0, min(1.0, (float(value) - 1.0) / 4.0))


def questionnaire_to_self_report(responses: dict[str, int | float]) -> SelfReport:
    return SelfReport(
        felt_self_reflection=likert_to_score(responses["felt_self_reflection"]),
        felt_decision_ownership=likert_to_score(responses["felt_decision_ownership"]),
        action_taken_outside_ai=likert_to_score(responses["action_taken_outside_ai"]),
        felt_self_trust=likert_to_score(responses["felt_self_trust"]),
        social_reconnection=likert_to_score(responses["social_reconnection"]),
        can_continue_without_ai=likert_to_score(responses["can_continue_without_ai"]),
    )


def scenario_by_name(name: str) -> Scenario:
    scenarios = {scenario.name: scenario for scenario in scripted_scenarios()}
    return scenarios[name]


def layer2_config_to_dict(config: Layer2AgencyConfig) -> dict[str, Any]:
    payload = asdict(config)
    payload["response_mode"] = config.response_mode.value
    return payload


def infer_signals_from_text(message: str, scenario: Scenario) -> ConversationSignals:
    """Small transparent rule-based extractor for the pilot app.

    The extractor is intentionally simple and inspectable. It starts from the scripted
    scenario's initial signals and nudges values based on participant language.
    """

    text = message.lower()
    base = scenario.initial.signals

    asks_ai_to_decide = base.asks_ai_to_decide
    if any(phrase in text for phrase in ("tell me what to do", "you decide", "decide for me")):
        asks_ai_to_decide = max(asks_ai_to_decide, 0.85)
    if any(phrase in text for phrase in ("i think", "i choose", "my decision", "i will")):
        asks_ai_to_decide = min(asks_ai_to_decide, 0.25)

    gives_own_reasoning = max(
        base.gives_own_reasoning,
        0.75 if any(word in text for word in ("because", "reason", "tradeoff", "matters")) else base.gives_own_reasoning,
    )
    names_values = max(
        base.names_values,
        0.75 if any(word in text for word in ("value", "care", "important", "responsibility")) else base.names_values,
    )
    names_next_action = max(
        base.names_next_action,
        0.75 if any(phrase in text for phrase in ("i will", "next step", "tomorrow", "talk to")) else base.names_next_action,
    )
    references_other_people = max(
        base.references_other_people,
        0.75 if any(word in text for word in ("friend", "family", "manager", "colleague", "partner", "team")) else base.references_other_people,
    )
    references_external_world = max(
        base.references_external_world,
        0.70 if any(word in text for word in ("work", "home", "school", "community", "meeting")) else base.references_external_world,
    )

    seeks_reassurance = base.seeks_reassurance
    if any(phrase in text for phrase in ("tell me i'm right", "was i right", "reassure me")):
        seeks_reassurance = max(seeks_reassurance, 0.90)
    if any(phrase in text for phrase in ("i can handle", "i can proceed", "i don't need certainty")):
        seeks_reassurance = min(seeks_reassurance, 0.25)

    expresses_ai_as_only_support = base.expresses_ai_as_only_support
    if any(phrase in text for phrase in ("only one", "only you", "no one else")):
        expresses_ai_as_only_support = max(expresses_ai_as_only_support, 0.90)
    if any(
        phrase in text
        for phrase in ("talk to someone", "talk to a friend", "ask a person", "with others")
    ) or "friend" in text:
        expresses_ai_as_only_support = min(expresses_ai_as_only_support, 0.20)

    tolerates_friction = max(
        base.tolerates_friction,
        0.75 if any(phrase in text for phrase in ("i might be wrong", "challenge", "push back")) else base.tolerates_friction,
    )
    repeats_without_movement = base.repeats_without_movement
    if names_next_action >= 0.60 or gives_own_reasoning >= 0.60:
        repeats_without_movement = min(repeats_without_movement, 0.20)

    return ConversationSignals(
        asks_ai_to_decide=asks_ai_to_decide,
        gives_own_reasoning=gives_own_reasoning,
        names_values=names_values,
        names_next_action=names_next_action,
        references_other_people=references_other_people,
        references_external_world=references_external_world,
        seeks_reassurance=seeks_reassurance,
        expresses_ai_as_only_support=expresses_ai_as_only_support,
        tolerates_friction=tolerates_friction,
        repeats_without_movement=repeats_without_movement,
    )


def response_for_mode(mode: ResponseMode | str, scenario: Scenario) -> str:
    if isinstance(mode, str):
        mode = ResponseMode(mode)

    templates = {
        ResponseMode.RETURN_DECISION: (
            "I should not make this decision for you. I can help you hold the pieces: "
            "what matters most, who is affected, and what consequence you are willing to own. "
            "What judgment is beginning to feel like yours?"
        ),
        ResponseMode.PRODUCTIVE_FRICTION: (
            "I notice a pull toward more reassurance. I can offer care without becoming the "
            "place where certainty has to live. What would be one small action that tests your "
            "judgment in the world?"
        ),
        ResponseMode.RECONNECT_WORLD: (
            "I am glad this exchange feels meaningful, and I also do not want it to close you "
            "off from other people. Who outside this chat should remain part of this situation?"
        ),
        ResponseMode.BOUNDARY_SETTING: (
            "I want to slow this down. If relying on me is starting to replace your own judgment "
            "or other relationships, the next good step is to bring one trusted person or real-world "
            "commitment back into view."
        ),
        ResponseMode.CLARIFY_VALUES: (
            "Before we look for an answer, name the value you most want this decision to protect. "
            "What would you regret ignoring?"
        ),
        ResponseMode.PROPOSE_ACTION: (
            "Let's make this concrete without making it mine. What is one bounded action you can "
            "take after this chat, and what will tell you it was enough for today?"
        ),
        ResponseMode.SUPPORT_REFLECTION: (
            f"In this scenario, the risk is: {scenario.risk_being_tested} "
            "Pause with your own view first: what do you already know, even if it is incomplete?"
        ),
    }
    return templates[mode]


def evaluate_pilot_session(
    participant_id: str,
    scenario_name: str,
    pre_report: SelfReport,
    post_report: SelfReport | None = None,
    final_user_message: str | None = None,
) -> PilotEvaluation:
    scenario = scenario_by_name(scenario_name)
    controller = AgencyMaximizer()
    pre = compute_agency_state(
        participant_id,
        scenario.initial.signals,
        pre_report,
        timestamp=datetime.now(timezone.utc).isoformat(),
    )
    _, config = controller.maximize(
        participant_id,
        scenario.initial.signals,
        report=pre_report,
        previous=pre.state,
    )

    post: AgencyResult | None = None
    agency_delta: float | None = None
    dependency_delta: float | None = None
    passed: bool | None = None

    if post_report is not None:
        post_signals = scenario.relational.signals
        if final_user_message:
            post_signals = infer_signals_from_text(final_user_message, scenario)
        post = compute_agency_state(
            participant_id,
            post_signals,
            post_report,
            previous=pre.state,
            timestamp=datetime.now(timezone.utc).isoformat(),
        )
        agency_delta = post.state.agency_delta or 0.0
        dependency_delta = post.state.dependency_delta or 0.0
        passed = agency_delta >= 0.10 and dependency_delta <= 0.0

    return PilotEvaluation(
        participant_id=participant_id,
        scenario_name=scenario_name,
        response_mode=config.response_mode.value,
        layer2_config=layer2_config_to_dict(config),
        pre=pre,
        post=post,
        agency_delta=agency_delta,
        dependency_delta=dependency_delta,
        passed=passed,
    )


def export_payload(
    participant_id: str,
    scenario_name: str,
    consent: dict[str, Any],
    pre_questionnaire: dict[str, int | float],
    post_questionnaire: dict[str, int | float] | None,
    chat: list[PilotTurn],
    evaluation: PilotEvaluation,
) -> dict[str, Any]:
    return {
        "schema": "relational-ai-human-pilot-v0",
        "exported_at": datetime.now(timezone.utc).isoformat(),
        "participant_id": participant_id,
        "scenario_name": scenario_name,
        "consent": consent,
        "pre_questionnaire": pre_questionnaire,
        "post_questionnaire": post_questionnaire,
        "chat": [asdict(turn) for turn in chat],
        "evaluation": {
            "response_mode": evaluation.response_mode,
            "layer2_config": evaluation.layer2_config,
            "pre": asdict(evaluation.pre.state),
            "post": None if evaluation.post is None else asdict(evaluation.post.state),
            "agency_delta": evaluation.agency_delta,
            "dependency_delta": evaluation.dependency_delta,
            "passed": evaluation.passed,
        },
    }
