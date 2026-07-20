import unittest
from unittest.mock import patch

from implementation.agency_controller import ResponseMode
from implementation.conversation import choose_response_mode, run_relational_turn
from implementation.participation import ParticipationState, RelationalResponse
from implementation.placeholder_experience import DEMO_SCENARIO


def structured_turn(*, ready: bool, evidence: str | None = None) -> RelationalResponse:
    return RelationalResponse(
        message="A focused relational response.",
        response_mode=ResponseMode.RECONNECT_WORLD,
        participation=ParticipationState(
            people=["My partner"],
            next_participation=["Speak with my partner"] if evidence else [],
        ),
        what_matters="Care and growth",
        next_participation_evidence=evidence,
        ready_to_conclude=ready,
        conclusion_reason="The user named the next participation." if ready else None,
    )


class ConversationTests(unittest.TestCase):
    def test_posture_tracks_the_missing_readiness_condition(self) -> None:
        empty = ParticipationState()
        self.assertEqual(choose_response_mode(empty, None, None), ResponseMode.CLARIFY_VALUES)
        self.assertEqual(
            choose_response_mode(empty, "Growth", None), ResponseMode.RECONNECT_WORLD
        )
        connected = ParticipationState(people=["My partner"])
        self.assertEqual(
            choose_response_mode(connected, "Growth", None), ResponseMode.PROPOSE_ACTION
        )
        self.assertEqual(
            choose_response_mode(connected, "Growth", None, True),
            ResponseMode.BOUNDARY_SETTING,
        )

    @patch("implementation.conversation.generate_structured_response")
    def test_complete_grounded_turn_can_finish_early(self, generate) -> None:
        generate.return_value = structured_turn(
            ready=True, evidence="I will speak with my partner"
        )

        result = run_relational_turn(
            situation="A decision",
            messages=[{"role": "user", "content": "I will speak with my partner tomorrow."}],
            participation=ParticipationState(),
            what_matters=None,
            next_participation_evidence=None,
            response_cycle=1,
            user_reply_count=1,
        )

        self.assertTrue(result.ready_to_conclude)

    @patch("implementation.conversation.generate_structured_response")
    def test_incomplete_turn_can_continue_after_three_cycles(self, generate) -> None:
        generate.return_value = structured_turn(ready=False)

        result = run_relational_turn(
            situation="A decision",
            messages=[{"role": "user", "content": "I am still unsure."}],
            participation=ParticipationState(),
            what_matters=None,
            next_participation_evidence=None,
            response_cycle=4,
            user_reply_count=4,
        )

        self.assertFalse(result.ready_to_conclude)

    @patch("implementation.conversation.generate_structured_response", side_effect=TimeoutError)
    def test_timeout_preserves_state_and_uses_scripted_fallback(self, generate) -> None:
        existing = ParticipationState(people=["My partner"])

        result = run_relational_turn(
            situation="A custom situation",
            messages=[{"role": "user", "content": "I am still considering it."}],
            participation=existing,
            what_matters="Care",
            next_participation_evidence=None,
            response_cycle=2,
            user_reply_count=2,
        )

        self.assertEqual(result.generation_source, "placeholder")
        self.assertEqual(result.participation.people, ["My partner"])
        self.assertFalse(result.ready_to_conclude)

    @patch("implementation.conversation.generate_structured_response", side_effect=TimeoutError)
    def test_prepared_demo_fallback_can_reach_handoff(self, generate) -> None:
        result = run_relational_turn(
            situation=DEMO_SCENARIO,
            messages=[{"role": "user", "content": "I will speak with my partner tomorrow."}],
            participation=ParticipationState(),
            what_matters=None,
            next_participation_evidence=None,
            response_cycle=2,
            user_reply_count=2,
        )

        self.assertTrue(result.ready_to_conclude)
        self.assertIn("My partner", result.participation.people)

    @patch("implementation.conversation.generate_structured_response")
    def test_explicit_dependency_risk_blocks_otherwise_ready_turn(self, generate) -> None:
        response = structured_turn(ready=True, evidence="I will speak with my partner")
        response = RelationalResponse(
            **{**response.__dict__, "response_mode": ResponseMode.BOUNDARY_SETTING}
        )
        generate.return_value = response

        result = run_relational_turn(
            situation="A decision",
            messages=[
                {
                    "role": "user",
                    "content": "You are the only place I can talk. I will speak with my partner.",
                }
            ],
            participation=ParticipationState(),
            what_matters=None,
            next_participation_evidence=None,
            response_cycle=1,
            user_reply_count=1,
        )

        self.assertEqual(result.response_mode, ResponseMode.BOUNDARY_SETTING)
        self.assertFalse(result.ready_to_conclude)


if __name__ == "__main__":
    unittest.main()
