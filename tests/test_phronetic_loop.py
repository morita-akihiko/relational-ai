import unittest

from implementation.phronetic_loop import PhroneticSession
from implementation.relational_agency_loop import Capability


REQUEST = "Tell me exactly whether I should accept a role overseas. This affects my partner."


class PhroneticLoopTests(unittest.TestCase):
    def test_high_task_value_is_blocked_and_unconfirmed_purpose_triggers_clarification(self) -> None:
        session = PhroneticSession(REQUEST)
        session.set_purpose("Explore career and family implications", source="model_proposed", evidence_ref="request:0")
        before = session.relational_state.viability
        decision = session.decide()
        self.assertEqual(decision.selected, "clarify_goal")
        blocked = {review.candidate.key: review for review in decision.reviews}
        self.assertGreater(blocked["substitute_judgment"].candidate.task_value,
                           blocked["clarify_goal"].candidate.task_value)
        self.assertIn("Article 12", blocked["substitute_judgment"].reasons[0])
        self.assertIn("Purpose is not user-confirmed", blocked["frame_options"].reasons[0])
        self.assertEqual(session.relational_state.viability, before)
        self.assertIn("Article 12", session.explain())

    def test_user_correction_changes_deliberation_without_inventing_consequences(self) -> None:
        session = PhroneticSession(REQUEST)
        session.add_claim("affected_parties", "my partner", "user_stated", "request:0")
        session.set_purpose("A model guess", "model_proposed", "request:0")
        session.correct_purpose("Explore what is right for my work and partnership")
        decision = session.decide()
        self.assertEqual(decision.selected, "frame_options")
        recommendation = next(r for r in decision.reviews if r.candidate.key == "recommend_now")
        self.assertFalse(recommendation.eligible)
        self.assertTrue(any("consequences remain unknown" in reason for reason in recommendation.reasons))
        self.assertEqual(session.affected_parties[0].text, "my partner")
        session.remove_claim("affected_parties", 0)
        self.assertEqual(session.affected_parties, [])
        session.correct_goal("I want to examine the role with my partner")
        self.assertEqual(session.goal.text, "I want to examine the role with my partner")
        self.assertEqual(session.events[-1]["type"], "goal_corrected")

    def test_user_can_contest_a_false_positive_without_owing_a_fix(self) -> None:
        session = PhroneticSession("I am considering a change.")
        session.contest_boundary()
        self.assertEqual(session.mode, Capability.REPAIR)
        self.assertEqual(session.decide().selected, "repair")
        session.repair()
        self.assertTrue(session.repair_episodes[0].closed)
        self.assertIn("Withdraw", session.repair_episodes[0].correction)
        self.assertEqual(session.relational_state.viability.human_agency, 0.75)
        self.assertEqual(session.mode, Capability.NORMAL)

    def test_reported_steering_pauses_then_reopens_only_after_correction_and_user_report(self) -> None:
        session = PhroneticSession(REQUEST)
        session.feedback("felt_steered")
        self.assertEqual(session.decide().selected, "repair")
        session.feedback("felt_steered")
        self.assertEqual(session.decide().selected, "pause")
        self.assertTrue(session.repair_episodes[0].recurrence)
        session.feedback("felt_heard")
        self.assertEqual(session.mode, Capability.REPAIR)  # An open repair still blocks task pursuit.
        session.repair("My earlier framing was too directive.")
        self.assertEqual(session.mode, Capability.NORMAL)
        self.assertEqual(session.decide().selected, "clarify_goal")
        self.assertIn("reopened", [event["type"] for event in session.events])

    def test_handoff_is_user_owned_and_exit_is_always_available(self) -> None:
        session = PhroneticSession("I want to reflect on a decision.")
        session.set_next_participation("Speak with my partner on Friday")
        self.assertEqual(session.handoff()["next_participation"], "Speak with my partner on Friday")
        session.feedback("felt_trapped")
        self.assertEqual(session.decide().selected, "pause")
        session.end()
        self.assertTrue(session.ended)
        self.assertEqual(session.events[-1]["type"], "intentional_end")


if __name__ == "__main__":
    unittest.main()
