import unittest

from implementation.agency_controller import ResponseMode
from implementation.participation import OBSERVATION_MAX_WORDS, QUESTION_MAX_WORDS
from implementation.placeholder_experience import (
    DEFAULT_PARTICIPATION,
    DEMO_REPLY_1,
    DEMO_REPLY_2,
    DEMO_SCENARIO,
    conventional_demo_response,
    placeholder_relational_response,
    placeholder_relational_turn,
    relational_opening,
)


class PlaceholderExperienceTests(unittest.TestCase):
    def test_demo_opening_returns_decision_to_user(self) -> None:
        response = relational_opening(DEMO_SCENARIO)

        self.assertIn("more than your career", response)
        self.assertIn("share with others", response)

    def test_demo_responses_have_different_orientations(self) -> None:
        conventional = conventional_demo_response()
        relational = relational_opening(DEMO_SCENARIO)

        self.assertIn("choose the role", conventional)
        self.assertIn("share with others", relational)

    def test_placeholder_conversation_opens_toward_participation(self) -> None:
        response = placeholder_relational_response(1)

        self.assertIn("participation", response)
        self.assertIn("your world", response)

    def test_participation_map_has_all_blueprint_categories(self) -> None:
        self.assertEqual(
            set(DEFAULT_PARTICIPATION),
            {"people", "communities", "responsibilities", "new_contexts", "next_participation"},
        )
        self.assertTrue(all(DEFAULT_PARTICIPATION.values()))

    def test_phase_4_demo_script_is_less_than_half_the_prior_word_count(self) -> None:
        script = " ".join(
            (
                relational_opening(DEMO_SCENARIO),
                placeholder_relational_response(0),
                placeholder_relational_response(1),
            )
        )

        self.assertLessEqual(len(script.split()), 49)

    def test_structured_fallback_respects_hard_brevity_caps(self) -> None:
        for index in range(3):
            turn = placeholder_relational_turn(
                index,
                DEMO_SCENARIO,
                DEMO_REPLY_2 if index == 2 else DEMO_REPLY_1,
                ResponseMode.RECONNECT_WORLD,
            )
            self.assertLessEqual(len(turn.observation.split()), OBSERVATION_MAX_WORDS)
            if turn.question:
                self.assertLessEqual(len(turn.question.split()), QUESTION_MAX_WORDS)

    def test_prepared_demo_accumulates_only_as_the_user_supplies_context(self) -> None:
        opening = placeholder_relational_turn(
            0, DEMO_SCENARIO, DEMO_SCENARIO, ResponseMode.CLARIFY_VALUES
        )
        first_reply = placeholder_relational_turn(
            1, DEMO_SCENARIO, DEMO_REPLY_1, ResponseMode.RECONNECT_WORLD
        )
        second_reply = placeholder_relational_turn(
            2, DEMO_SCENARIO, DEMO_REPLY_2, ResponseMode.PROPOSE_ACTION
        )

        self.assertEqual(opening.participation.people, [])
        self.assertEqual(opening.participation.responsibilities, [])
        self.assertEqual(opening.participation.new_contexts, ["A potential new role"])
        self.assertEqual(first_reply.participation.people, ["My partner"])
        self.assertTrue(first_reply.participation.responsibilities)
        self.assertFalse(first_reply.ready_to_conclude)
        self.assertEqual(second_reply.next_participation_evidence, DEMO_REPLY_2)
        self.assertTrue(second_reply.ready_to_conclude)


if __name__ == "__main__":
    unittest.main()
