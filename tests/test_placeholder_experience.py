import unittest

from implementation.placeholder_experience import (
    DEFAULT_PARTICIPATION,
    DEMO_SCENARIO,
    conventional_demo_response,
    placeholder_relational_response,
    relational_opening,
)


class PlaceholderExperienceTests(unittest.TestCase):
    def test_demo_opening_returns_decision_to_user(self) -> None:
        response = relational_opening(DEMO_SCENARIO)

        self.assertIn("not make that decision for you", response)
        self.assertIn("who is affected", response)

    def test_demo_responses_have_different_orientations(self) -> None:
        conventional = conventional_demo_response()
        relational = relational_opening(DEMO_SCENARIO)

        self.assertIn("help you decide", conventional)
        self.assertIn("willing to own", relational)

    def test_placeholder_conversation_opens_toward_participation(self) -> None:
        response = placeholder_relational_response(1)

        self.assertIn("conversation, observation, or action", response)
        self.assertIn("directly", response)

    def test_participation_map_has_all_blueprint_categories(self) -> None:
        self.assertEqual(
            set(DEFAULT_PARTICIPATION),
            {"people", "communities", "responsibilities", "new_contexts", "next_participation"},
        )
        self.assertTrue(all(DEFAULT_PARTICIPATION.values()))


if __name__ == "__main__":
    unittest.main()
