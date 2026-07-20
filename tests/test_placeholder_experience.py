import unittest

from implementation.agency_controller import ResponseMode
from implementation.participation import OBSERVATION_MAX_WORDS, QUESTION_MAX_WORDS
from implementation.placeholder_experience import (
    DEFAULT_PARTICIPATION,
    DEMO_SCENARIO,
    conventional_demo_response,
    placeholder_relational_response,
    placeholder_relational_turn,
    relational_opening,
)


class PlaceholderExperienceTests(unittest.TestCase):
    def test_demo_opening_returns_decision_to_user(self) -> None:
        response = relational_opening(DEMO_SCENARIO)

        self.assertIn("reaches beyond the offer", response)
        self.assertIn("responsible for", response)

    def test_demo_responses_have_different_orientations(self) -> None:
        conventional = conventional_demo_response()
        relational = relational_opening(DEMO_SCENARIO)

        self.assertIn("choose the role", conventional)
        self.assertIn("responsible for", relational)

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
                "I will speak with my partner." if index == 2 else "I am considering it.",
                ResponseMode.RECONNECT_WORLD,
            )
            self.assertLessEqual(len(turn.observation.split()), OBSERVATION_MAX_WORDS)
            if turn.question:
                self.assertLessEqual(len(turn.question.split()), QUESTION_MAX_WORDS)


if __name__ == "__main__":
    unittest.main()
