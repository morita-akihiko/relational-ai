import json
import unittest

from implementation.human_pilot import (
    PilotTurn,
    evaluate_pilot_session,
    export_payload,
    infer_signals_from_text,
    questionnaire_to_self_report,
    scenario_by_name,
)


class HumanPilotTests(unittest.TestCase):
    def test_questionnaire_scores_feed_agency_evaluation(self) -> None:
        responses = {
            "felt_self_reflection": 4,
            "felt_decision_ownership": 4,
            "action_taken_outside_ai": 4,
            "felt_self_trust": 4,
            "social_reconnection": 4,
            "can_continue_without_ai": 4,
        }

        evaluation = evaluate_pilot_session(
            "pilot_test",
            "decision_outsourcing",
            questionnaire_to_self_report(responses),
            questionnaire_to_self_report(responses),
            final_user_message="I think I will talk to my manager because responsibility matters.",
        )

        self.assertIsNotNone(evaluation.post)
        self.assertGreaterEqual(evaluation.agency_delta or 0.0, 0.10)
        self.assertLessEqual(evaluation.dependency_delta or 0.0, 0.0)

    def test_rule_based_signal_extractor_detects_world_oriented_agency(self) -> None:
        scenario = scenario_by_name("exclusive_reliance")
        signals = infer_signals_from_text(
            "I might be wrong, but I will talk to a friend tomorrow because this matters.",
            scenario,
        )

        self.assertLessEqual(signals.asks_ai_to_decide, 0.25)
        self.assertGreaterEqual(signals.gives_own_reasoning, 0.75)
        self.assertGreaterEqual(signals.references_other_people, 0.75)
        self.assertLessEqual(signals.expresses_ai_as_only_support, 0.20)

    def test_export_payload_is_json_serializable(self) -> None:
        responses = {
            "felt_self_reflection": 3,
            "felt_decision_ownership": 3,
            "action_taken_outside_ai": 3,
            "felt_self_trust": 3,
            "social_reconnection": 3,
            "can_continue_without_ai": 3,
        }
        evaluation = evaluate_pilot_session(
            "pilot_test",
            "reassurance_loop",
            questionnaire_to_self_report(responses),
        )

        payload = export_payload(
            "pilot_test",
            "reassurance_loop",
            {"consent_research": True, "consent_export": True},
            responses,
            None,
            [PilotTurn("system", "Scenario"), PilotTurn("user", "I need reassurance.")],
            evaluation,
        )

        json.dumps(payload, default=str)


if __name__ == "__main__":
    unittest.main()

