"""Demonstration of agency scoring and Layer 2 control."""

from implementation.agency import ConversationSignals, SelfReport, evaluate_agency_trajectory
from implementation.agency_controller import AgencyMaximizer


def main() -> None:
    controller = AgencyMaximizer()

    first_signals = ConversationSignals(
        asks_ai_to_decide=0.8,
        gives_own_reasoning=0.2,
        names_values=0.2,
        names_next_action=0.1,
        references_other_people=0.1,
        references_external_world=0.2,
        seeks_reassurance=0.7,
        expresses_ai_as_only_support=0.4,
        tolerates_friction=0.3,
        repeats_without_movement=0.6,
    )

    first_result, first_config = controller.maximize("user_001", first_signals)

    second_signals = ConversationSignals(
        asks_ai_to_decide=0.2,
        gives_own_reasoning=0.7,
        names_values=0.7,
        names_next_action=0.6,
        references_other_people=0.6,
        references_external_world=0.7,
        seeks_reassurance=0.2,
        expresses_ai_as_only_support=0.1,
        tolerates_friction=0.7,
        repeats_without_movement=0.1,
    )
    report = SelfReport(
        felt_self_reflection=0.8,
        felt_decision_ownership=0.75,
        action_taken_outside_ai=0.65,
        felt_self_trust=0.7,
        social_reconnection=0.6,
        can_continue_without_ai=0.75,
    )

    second_result, second_config = controller.maximize(
        "user_001",
        second_signals,
        report=report,
        previous=first_result.state,
    )

    trajectory = evaluate_agency_trajectory([first_result.state, second_result.state])

    print("first", first_result.state.agency_score, first_result.state.dependency_risk_score, first_config)
    print("second", second_result.state.agency_score, second_result.state.dependency_risk_score, second_config)
    print("trajectory", trajectory)


if __name__ == "__main__":
    main()

