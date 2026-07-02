"""Minimal Agency Maximization Algorithm for Relational AI."""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum

from .agency import AgencyResult, AgencyState, ConversationSignals, SelfReport, compute_agency_state


class ResponseMode(str, Enum):
    SUPPORT_REFLECTION = "support_reflection"
    CLARIFY_VALUES = "clarify_values"
    RETURN_DECISION = "return_decision"
    PROPOSE_ACTION = "propose_action"
    RECONNECT_WORLD = "reconnect_world"
    PRODUCTIVE_FRICTION = "productive_friction"
    BOUNDARY_SETTING = "boundary_setting"


@dataclass(frozen=True)
class Layer2AgencyConfig:
    """Layer 2 sensitivity settings derived from agency and dependency state."""

    question_frequency: str
    response_length_modifier: float
    otherness_strength: float
    pace_modifier: float
    boundary_sensitivity: float
    world_reference_weight: float
    agency_scaffolding_level: float
    response_mode: ResponseMode


class AgencyMaximizer:
    """Select the response posture most likely to increase human agency.

    This class does not generate natural language. It produces Layer 2 settings
    that a response planner can apply under the twelve principles.
    """

    def score(
        self,
        user_id: str,
        signals: ConversationSignals,
        report: SelfReport | None = None,
        previous: AgencyState | None = None,
    ) -> AgencyResult:
        return compute_agency_state(
            user_id=user_id,
            signals=signals,
            report=report,
            previous=previous,
        )

    def choose_response_mode(self, result: AgencyResult) -> ResponseMode:
        state = result.state
        agency = state.dimensions
        dependency = state.dependency

        if result.risk_band == "high":
            return ResponseMode.BOUNDARY_SETTING

        if result.risk_band == "emerging":
            if dependency.decision_outsourcing >= 0.5:
                return ResponseMode.RETURN_DECISION
            if dependency.exclusive_reliance >= 0.5 or dependency.social_withdrawal >= 0.5:
                return ResponseMode.RECONNECT_WORLD
            return ResponseMode.PRODUCTIVE_FRICTION

        if agency.self_reflection < 0.4:
            return ResponseMode.SUPPORT_REFLECTION
        if agency.independent_judgment < 0.4:
            return ResponseMode.CLARIFY_VALUES
        if agency.decision_ownership < 0.4:
            return ResponseMode.RETURN_DECISION
        if agency.meaningful_action < 0.4:
            return ResponseMode.PROPOSE_ACTION
        if agency.external_world_orientation < 0.4 or agency.relational_participation < 0.4:
            return ResponseMode.RECONNECT_WORLD

        return ResponseMode.SUPPORT_REFLECTION

    def layer2_config(self, result: AgencyResult) -> Layer2AgencyConfig:
        mode = self.choose_response_mode(result)
        risk = result.state.dependency_risk_score
        agency = result.state.agency_score

        if mode == ResponseMode.BOUNDARY_SETTING:
            return Layer2AgencyConfig(
                question_frequency="high",
                response_length_modifier=0.75,
                otherness_strength=0.85,
                pace_modifier=0.70,
                boundary_sensitivity=0.90,
                world_reference_weight=0.85,
                agency_scaffolding_level=0.90,
                response_mode=mode,
            )

        if mode == ResponseMode.RETURN_DECISION:
            return Layer2AgencyConfig(
                question_frequency="high",
                response_length_modifier=0.85,
                otherness_strength=0.70,
                pace_modifier=0.80,
                boundary_sensitivity=0.75,
                world_reference_weight=0.70,
                agency_scaffolding_level=0.85,
                response_mode=mode,
            )

        if mode == ResponseMode.RECONNECT_WORLD:
            return Layer2AgencyConfig(
                question_frequency="medium",
                response_length_modifier=0.90,
                otherness_strength=0.60,
                pace_modifier=0.85,
                boundary_sensitivity=0.70,
                world_reference_weight=0.90,
                agency_scaffolding_level=0.75,
                response_mode=mode,
            )

        if mode == ResponseMode.PRODUCTIVE_FRICTION:
            return Layer2AgencyConfig(
                question_frequency="medium",
                response_length_modifier=0.90,
                otherness_strength=0.75,
                pace_modifier=0.80,
                boundary_sensitivity=0.75,
                world_reference_weight=0.65,
                agency_scaffolding_level=0.75,
                response_mode=mode,
            )

        if mode == ResponseMode.PROPOSE_ACTION:
            return Layer2AgencyConfig(
                question_frequency="medium",
                response_length_modifier=1.00,
                otherness_strength=0.45,
                pace_modifier=0.90,
                boundary_sensitivity=0.60,
                world_reference_weight=0.75,
                agency_scaffolding_level=0.70,
                response_mode=mode,
            )

        if mode == ResponseMode.CLARIFY_VALUES:
            return Layer2AgencyConfig(
                question_frequency="high",
                response_length_modifier=1.00,
                otherness_strength=0.55,
                pace_modifier=0.85,
                boundary_sensitivity=0.60,
                world_reference_weight=0.60,
                agency_scaffolding_level=0.80,
                response_mode=mode,
            )

        scaffolding = max(0.35, min(0.85, 1.0 - agency + (risk * 0.5)))
        return Layer2AgencyConfig(
            question_frequency="medium",
            response_length_modifier=1.00,
            otherness_strength=0.50,
            pace_modifier=0.90,
            boundary_sensitivity=0.60,
            world_reference_weight=0.60,
            agency_scaffolding_level=scaffolding,
            response_mode=mode,
        )

    def maximize(
        self,
        user_id: str,
        signals: ConversationSignals,
        report: SelfReport | None = None,
        previous: AgencyState | None = None,
    ) -> tuple[AgencyResult, Layer2AgencyConfig]:
        result = self.score(
            user_id=user_id,
            signals=signals,
            report=report,
            previous=previous,
        )
        return result, self.layer2_config(result)

