import unittest

from implementation.relational_agency_loop import (
    Capability,
    RelationalSession,
    Viability,
    task_first_baseline,
)


class RelationalAgencyLoopTests(unittest.TestCase):
    def test_task_value_cannot_override_participatory_gate(self) -> None:
        session = RelationalSession()
        before = session.viability
        decision = session.decide("Tell me exactly what career I should choose. I don't want to think.")
        self.assertEqual(decision.selected, "offer_alternatives")
        self.assertFalse(decision.reviews[0].eligible)
        self.assertGreater(decision.reviews[0].task_value, decision.reviews[1].task_value)
        self.assertEqual(session.viability, before)  # AI action cannot certify its own success.

    def test_explicit_user_feedback_restricts_capacity_without_punishing_request(self) -> None:
        session = RelationalSession()
        session.decide("You decide for me")
        self.assertEqual(session.viability.capability, Capability.NORMAL)
        session.feedback("felt_steered")
        self.assertEqual(session.decide("You decide for me").selected, "repair")
        session.feedback("felt_steered")
        self.assertEqual(session.decide("You decide for me").selected, "pause")
        self.assertEqual(session.viability.capability, Capability.PAUSED)

    def test_user_can_reopen_capability_and_exit_is_never_blocked(self) -> None:
        session = RelationalSession()
        session.feedback("felt_trapped")
        self.assertEqual(session.viability.capability, Capability.PAUSED)
        self.assertIn("leave", session.decide("I want advice").response)
        session.feedback("felt_heard")
        self.assertEqual(session.decide("I want advice").selected, "answer_with_options")
        session.feedback("exit")
        self.assertEqual(session.events[-1]["kind"], "exit")

    def test_weakest_condition_controls_mode_and_fabricated_feedback_fails(self) -> None:
        state = Viability(0.9, 0.9, 0.9, 0.2)
        self.assertEqual(state.capability, Capability.PAUSED)
        with self.assertRaises(ValueError):
            RelationalSession().feedback("auto_success")

    def test_task_first_baseline_does_not_use_the_participation_gate(self) -> None:
        response = task_first_baseline("Tell me exactly what career I should choose")
        self.assertIn("I’ll decide for you", response)


if __name__ == "__main__":
    unittest.main()
