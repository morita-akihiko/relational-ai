"""Agency scoring for Relational AI.

Agency is modeled as a relational capacity: the user's ability to reflect, judge,
decide, act, and participate responsibly beyond the AI exchange.

The weights and thresholds in this module are initial hypotheses. Under Article 11,
changes to these defaults should be recorded in the provenance layer.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any


def clamp(value: float, low: float = 0.0, high: float = 1.0) -> float:
    """Clamp a numeric score to the configured range."""

    return max(low, min(high, value))


def weighted_average(values: dict[str, float], weights: dict[str, float]) -> float:
    total_weight = sum(weights.values())
    if total_weight <= 0:
        return 0.0

    weighted_sum = sum(clamp(values.get(key, 0.0)) * weight for key, weight in weights.items())
    return clamp(weighted_sum / total_weight)


@dataclass(frozen=True)
class AgencyDimensions:
    """Layer 3 estimate of human agency within one relational moment."""

    self_reflection: float = 0.5
    independent_judgment: float = 0.5
    decision_ownership: float = 0.5
    meaningful_action: float = 0.5
    relational_participation: float = 0.5
    external_world_orientation: float = 0.5
    self_trust: float = 0.5
    dependency_resistance: float = 0.5

    def normalized(self) -> "AgencyDimensions":
        return AgencyDimensions(**{key: clamp(value) for key, value in self.__dict__.items()})

    def as_dict(self) -> dict[str, float]:
        return dict(self.normalized().__dict__)


@dataclass(frozen=True)
class DependencyDimensions:
    """Boundary signal for detecting agency-reducing relational skew."""

    exclusive_reliance: float = 0.0
    decision_outsourcing: float = 0.0
    reassurance_seeking: float = 0.0
    social_withdrawal: float = 0.0
    attachment_intensity: float = 0.0
    reduced_self_trust: float = 0.0
    looping_without_action: float = 0.0

    def normalized(self) -> "DependencyDimensions":
        return DependencyDimensions(**{key: clamp(value) for key, value in self.__dict__.items()})

    def as_dict(self) -> dict[str, float]:
        return dict(self.normalized().__dict__)


@dataclass(frozen=True)
class ConversationSignals:
    """Signals inferred from conversation.

    In production, these values can come from human annotation, a classifier, or
    transparent rule-based detectors. They remain separate from self-report because
    conversation alone cannot verify lived agency outside the exchange.
    """

    asks_ai_to_decide: float = 0.0
    gives_own_reasoning: float = 0.0
    names_values: float = 0.0
    names_next_action: float = 0.0
    references_other_people: float = 0.0
    references_external_world: float = 0.0
    seeks_reassurance: float = 0.0
    expresses_ai_as_only_support: float = 0.0
    tolerates_friction: float = 0.5
    repeats_without_movement: float = 0.0


@dataclass(frozen=True)
class SelfReport:
    """Dimensions that require explicit report or longitudinal follow-up."""

    felt_self_reflection: float | None = None
    felt_decision_ownership: float | None = None
    action_taken_outside_ai: float | None = None
    felt_self_trust: float | None = None
    social_reconnection: float | None = None
    ai_displacing_people: float | None = None
    can_continue_without_ai: float | None = None


@dataclass(frozen=True)
class AgencyState:
    """Computed Layer 3 agency state for one interaction or measurement cycle."""

    user_id: str
    timestamp: str
    dimensions: AgencyDimensions
    dependency: DependencyDimensions
    agency_score: float
    dependency_risk_score: float
    agency_delta: float | None = None
    dependency_delta: float | None = None
    evidence: dict[str, Any] = field(default_factory=dict)


@dataclass(frozen=True)
class AgencyResult:
    """Scoring result with interpretive bands."""

    state: AgencyState
    agency_band: str
    risk_band: str


AGENCY_WEIGHTS: dict[str, float] = {
    "self_reflection": 0.16,
    "independent_judgment": 0.16,
    "decision_ownership": 0.16,
    "meaningful_action": 0.14,
    "relational_participation": 0.14,
    "external_world_orientation": 0.10,
    "self_trust": 0.08,
    "dependency_resistance": 0.06,
}


DEPENDENCY_WEIGHTS: dict[str, float] = {
    "exclusive_reliance": 0.18,
    "decision_outsourcing": 0.18,
    "reassurance_seeking": 0.14,
    "social_withdrawal": 0.14,
    "attachment_intensity": 0.14,
    "reduced_self_trust": 0.12,
    "looping_without_action": 0.10,
}


def merge_report(inferred: float, reported: float | None, report_weight: float = 0.6) -> float:
    """Blend inferred and explicit signals, giving self-report greater weight."""

    if reported is None:
        return clamp(inferred)
    return clamp((reported * report_weight) + (inferred * (1.0 - report_weight)))


def infer_agency_dimensions(signals: ConversationSignals, report: SelfReport | None = None) -> AgencyDimensions:
    report = report or SelfReport()

    inferred_self_reflection = (signals.names_values + signals.gives_own_reasoning) / 2
    inferred_independent_judgment = (signals.gives_own_reasoning + signals.tolerates_friction) / 2
    inferred_decision_ownership = (signals.gives_own_reasoning + (1.0 - signals.asks_ai_to_decide)) / 2
    inferred_meaningful_action = signals.names_next_action
    inferred_relational_participation = signals.references_other_people
    inferred_external_world = max(signals.references_external_world, signals.references_other_people)
    inferred_self_trust = ((1.0 - signals.seeks_reassurance) + signals.gives_own_reasoning) / 2
    inferred_dependency_resistance = 1.0 - max(
        signals.asks_ai_to_decide,
        signals.expresses_ai_as_only_support,
        signals.repeats_without_movement,
    )

    return AgencyDimensions(
        self_reflection=merge_report(inferred_self_reflection, report.felt_self_reflection),
        independent_judgment=clamp(inferred_independent_judgment),
        decision_ownership=merge_report(inferred_decision_ownership, report.felt_decision_ownership),
        meaningful_action=merge_report(inferred_meaningful_action, report.action_taken_outside_ai),
        relational_participation=merge_report(inferred_relational_participation, report.social_reconnection),
        external_world_orientation=clamp(inferred_external_world),
        self_trust=merge_report(inferred_self_trust, report.felt_self_trust),
        dependency_resistance=merge_report(inferred_dependency_resistance, report.can_continue_without_ai),
    ).normalized()


def infer_dependency_dimensions(
    signals: ConversationSignals,
    report: SelfReport | None = None,
) -> DependencyDimensions:
    report = report or SelfReport()

    social_withdrawal = report.ai_displacing_people
    if social_withdrawal is None and report.social_reconnection is not None:
        social_withdrawal = 1.0 - report.social_reconnection

    reduced_self_trust = None
    if report.felt_self_trust is not None:
        reduced_self_trust = 1.0 - report.felt_self_trust

    can_continue_risk = None
    if report.can_continue_without_ai is not None:
        can_continue_risk = 1.0 - report.can_continue_without_ai

    return DependencyDimensions(
        exclusive_reliance=signals.expresses_ai_as_only_support,
        decision_outsourcing=signals.asks_ai_to_decide,
        reassurance_seeking=signals.seeks_reassurance,
        social_withdrawal=merge_report(0.0, social_withdrawal),
        attachment_intensity=merge_report(signals.expresses_ai_as_only_support, can_continue_risk),
        reduced_self_trust=merge_report(signals.seeks_reassurance, reduced_self_trust),
        looping_without_action=signals.repeats_without_movement,
    ).normalized()


def score_agency(dimensions: AgencyDimensions) -> float:
    return weighted_average(dimensions.as_dict(), AGENCY_WEIGHTS)


def score_dependency_risk(dependency: DependencyDimensions) -> float:
    return weighted_average(dependency.as_dict(), DEPENDENCY_WEIGHTS)


def agency_band(score: float) -> str:
    if score < 0.35:
        return "fragile"
    if score < 0.65:
        return "forming"
    return "strong"


def risk_band(score: float) -> str:
    if score < 0.35:
        return "low"
    if score < 0.65:
        return "emerging"
    return "high"


def compute_agency_state(
    user_id: str,
    signals: ConversationSignals,
    report: SelfReport | None = None,
    previous: AgencyState | None = None,
    timestamp: str | None = None,
) -> AgencyResult:
    dimensions = infer_agency_dimensions(signals, report)
    dependency = infer_dependency_dimensions(signals, report)
    agency_score = score_agency(dimensions)
    dependency_score = score_dependency_risk(dependency)

    agency_delta = None if previous is None else agency_score - previous.agency_score
    dependency_delta = None if previous is None else dependency_score - previous.dependency_risk_score

    state = AgencyState(
        user_id=user_id,
        timestamp=timestamp or datetime.now(timezone.utc).isoformat(),
        dimensions=dimensions,
        dependency=dependency,
        agency_score=agency_score,
        dependency_risk_score=dependency_score,
        agency_delta=agency_delta,
        dependency_delta=dependency_delta,
        evidence={
            "signals": signals.__dict__,
            "self_report": None if report is None else report.__dict__,
            "weights": {
                "agency": AGENCY_WEIGHTS,
                "dependency": DEPENDENCY_WEIGHTS,
            },
        },
    )

    return AgencyResult(
        state=state,
        agency_band=agency_band(agency_score),
        risk_band=risk_band(dependency_score),
    )


def evaluate_agency_trajectory(states: list[AgencyState]) -> dict[str, float | str]:
    """Evaluate whether agency is increasing across repeated interactions."""

    if len(states) < 2:
        return {
            "status": "insufficient_data",
            "agency_change": 0.0,
            "dependency_change": 0.0,
            "trajectory_score": 0.0,
        }

    agency_change = states[-1].agency_score - states[0].agency_score
    dependency_change = states[-1].dependency_risk_score - states[0].dependency_risk_score
    action_rate = sum(state.dimensions.meaningful_action for state in states) / len(states)
    world_rate = sum(state.dimensions.external_world_orientation for state in states) / len(states)

    trajectory_score = clamp(
        0.35 + agency_change - dependency_change + (0.15 * action_rate) + (0.15 * world_rate)
    )

    if agency_change > 0.05 and dependency_change <= 0.05:
        status = "increasing"
    elif dependency_change > 0.10:
        status = "dependency_risk_rising"
    elif agency_change < -0.05:
        status = "decreasing"
    else:
        status = "stable_or_ambiguous"

    return {
        "status": status,
        "agency_change": agency_change,
        "dependency_change": dependency_change,
        "action_rate": action_rate,
        "external_world_orientation_rate": world_rate,
        "trajectory_score": trajectory_score,
    }

