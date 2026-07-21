import os
import unittest
from unittest.mock import patch

from streamlit.testing.v1 import AppTest

from implementation.participation import ParticipationState


class Phase4StreamlitTests(unittest.TestCase):
    def _run(self, app: AppTest) -> AppTest:
        with patch.dict(os.environ, {}, clear=False):
            os.environ.pop("RELATIONAL_AI_DEV", None)
            app.run()
        self.assertFalse(list(app.exception))
        return app

    @staticmethod
    def _button(app: AppTest, label: str):
        return next(button for button in app.button if button.label == label)

    def test_landing_states_the_phase_5_product_story(self) -> None:
        app = self._run(AppTest.from_file("streamlit_app.py", default_timeout=15))
        rendered = "\n".join(markdown.value for markdown in app.markdown)

        self.assertIn("Designed for the co-generation of human relationships", rendered)
        self.assertIn("bring those possibilities into their next human conversation", rendered)
        self.assertIn("See the present", rendered)
        self.assertIn("possibilities already present in your relationships", rendered)
        self.assertIn("Imagine what will emerge", rendered)
        self.assertIn("through a renewed conversation", rendered)
        self.assertIn("Take one step forward", rendered)
        self.assertIn("toward new possibilities", rendered)
        self.assertIn("@media (max-width: 780px)", rendered)

    def test_conversation_renders_map_before_exchange_with_all_categories(self) -> None:
        app = AppTest.from_file("streamlit_app.py", default_timeout=15)
        app.session_state["screen"] = "conversation"
        app.session_state["mode"] = "normal"
        app.session_state["situation"] = "A situation"
        app.session_state["messages"] = [
            {
                "role": "assistant",
                "content": "A short turn. What matters?",
                "observation": "A short turn.",
                "question": "What matters?",
            }
        ]
        app.session_state["participation"] = ParticipationState()
        app.session_state["latest_additions"] = ParticipationState()
        app.session_state["ready_to_conclude"] = False

        self._run(app)

        rendered = "\n".join(markdown.value for markdown in app.markdown)
        for label in ("People", "Communities", "Responsibilities", "New contexts", "Next participation"):
            self.assertIn(label, rendered)
        for empty_state in (
            "No one named yet",
            "No community named yet",
            "Not yet surfaced",
            "No new context yet",
            "Waiting for your words",
        ):
            self.assertIn(empty_state, rendered)
        self.assertIn("a temporary orientation—not the destination", rendered)
        self.assertIn("Observation", rendered)
        self.assertIn("Question", rendered)
        self.assertLess(rendered.index("Participation taking shape"), rendered.index("The exchange"))
        self.assertEqual(len(app.chat_input), 1)
        captions = "\n".join(caption.value for caption in app.caption)
        self.assertIn("Available after enough conversation for a useful synthesis", captions)

    def test_participation_review_unlocks_after_four_replies_and_stays_in_conversation(self) -> None:
        app = AppTest.from_file("streamlit_app.py", default_timeout=15)
        app.session_state["screen"] = "conversation"
        app.session_state["mode"] = "normal"
        app.session_state["situation"] = "I want to reconnect with a friend."
        app.session_state["messages"] = [
            {"role": "assistant", "content": "What matters here?", "observation": "A friendship is in view.", "question": "What matters here?"},
            {"role": "user", "content": "I miss being able to speak openly."},
        ]
        app.session_state["participation"] = ParticipationState(people=["My friend"])
        app.session_state["latest_additions"] = ParticipationState()
        app.session_state["what_matters"] = "Speaking openly"
        app.session_state["ready_to_conclude"] = False
        app.session_state["response_count"] = 3

        self._run(app)
        self.assertTrue(self._button(app, "Review my participation").disabled)

        app.session_state["response_count"] = 4
        self._run(app)
        review_button = self._button(app, "Review my participation")
        self.assertFalse(review_button.disabled)
        review_button.click()
        self._run(app)

        rendered = "\n".join(markdown.value for markdown in app.markdown)
        for label in ("PARTICIPATION REVIEW", "People", "Shift", "Emerging possibility"):
            self.assertIn(label, rendered)
        self.assertIn(
            "What feels worth carrying into your life beyond this conversation?", rendered
        )
        self.assertEqual(app.session_state["screen"], "conversation")
        self.assertEqual(len(app.chat_input), 1)

    def test_latest_map_addition_is_visibly_marked(self) -> None:
        app = AppTest.from_file("streamlit_app.py", default_timeout=15)
        app.session_state["screen"] = "conversation"
        app.session_state["mode"] = "normal"
        app.session_state["situation"] = "A situation"
        app.session_state["messages"] = [{"role": "assistant", "content": "A turn."}]
        app.session_state["participation"] = ParticipationState(people=["My partner"])
        app.session_state["latest_additions"] = ParticipationState(people=["My partner"])
        app.session_state["ready_to_conclude"] = False

        self._run(app)

        rendered = "\n".join(markdown.value for markdown in app.markdown)
        self.assertIn("My partner", rendered)
        self.assertIn("new-tag", rendered)
        self.assertIn("This turn", rendered)

    def test_participation_card_shows_grounding_and_remains_editable(self) -> None:
        app = AppTest.from_file("streamlit_app.py", default_timeout=15)
        app.session_state["screen"] = "participation"
        app.session_state["participation"] = ParticipationState(
            people=["My partner"], next_participation=["Speak with my partner"]
        )
        app.session_state["next_participation_evidence"] = "I will speak with my partner"
        app.session_state["card"] = {
            "what_matters": "Care",
            "connected_to": "My partner",
            "next_participation": "Speak with my partner",
            "when_or_where": "Tomorrow",
        }

        self._run(app)

        captions = "\n".join(caption.value for caption in app.caption)
        self.assertIn("I will speak with my partner", captions)
        self.assertEqual(len(app.text_area), 3)
        self.assertEqual(len(app.text_input), 1)

    def test_final_screen_has_no_reengagement_control(self) -> None:
        app = AppTest.from_file("streamlit_app.py", default_timeout=15)
        app.session_state["screen"] = "conclusion"
        app.session_state["card"] = {
            "what_matters": "Care",
            "connected_to": "My partner",
            "next_participation": "Speak with my partner",
            "when_or_where": "Tomorrow",
        }

        self._run(app)

        rendered = "\n".join(markdown.value for markdown in app.markdown)
        self.assertIn("The conversation has done its part", rendered)
        self.assertIn("Your next step is with another person", rendered)
        self.assertIn("Carry this intention into the relationship", rendered)
        self.assertIn("Speak with my partner", rendered)
        self.assertIn(
            "Take this as participation you can revise in the world—not an instruction from the AI.",
            [notice.value for notice in app.info],
        )
        self.assertEqual(len(app.chat_input), 0)
        self.assertEqual([button.label for button in app.button], [])

    def test_configuration_warning_is_hidden_from_presented_experience(self) -> None:
        app = AppTest.from_file("streamlit_app.py", default_timeout=15)
        app.session_state["screen"] = "conversation"
        app.session_state["mode"] = "normal"
        app.session_state["situation"] = "A concern"
        app.session_state["messages"] = []
        app.session_state["participation"] = ParticipationState()
        app.session_state["latest_additions"] = ParticipationState()
        app.session_state["ready_to_conclude"] = False
        app.session_state["generation_notice"] = "Live generation is not configured."

        self._run(app)

        self.assertEqual(list(app.warning), [])
        self.assertNotIn(
            "Placeholder fallback",
            "\n".join(caption.value for caption in app.caption),
        )

    def test_demo_comparison_becomes_secondary_after_first_reply(self) -> None:
        app = AppTest.from_file("streamlit_app.py", default_timeout=15)
        app.session_state["screen"] = "conversation"
        app.session_state["mode"] = "demo"
        app.session_state["situation"] = "A job offer"
        app.session_state["conventional_response"] = "Choose the higher score."
        app.session_state["messages"] = [
            {
                "role": "assistant",
                "content": "This reaches others. Who belongs here?",
                "observation": "This reaches others.",
                "question": "Who belongs here?",
            }
        ]
        app.session_state["response_count"] = 1
        app.session_state["participation"] = ParticipationState(people=["My partner"])
        app.session_state["latest_additions"] = ParticipationState(people=["My partner"])
        app.session_state["ready_to_conclude"] = False

        self._run(app)

        self.assertIn("Opening comparison", [expander.label for expander in app.expander])

    def test_prepared_demo_controls_cover_both_scripted_steps(self) -> None:
        for response_count in (0, 1):
            app = AppTest.from_file("streamlit_app.py", default_timeout=15)
            app.session_state["screen"] = "conversation"
            app.session_state["mode"] = "demo"
            app.session_state["situation"] = "A job offer"
            app.session_state["conventional_response"] = "Choose the higher score."
            app.session_state["messages"] = [
                {
                    "role": "assistant",
                    "content": "This reaches others. Who belongs here?",
                    "observation": "This reaches others.",
                    "question": "Who belongs here?",
                }
            ]
            app.session_state["response_count"] = response_count
            app.session_state["participation"] = ParticipationState()
            app.session_state["latest_additions"] = ParticipationState()
            app.session_state["ready_to_conclude"] = False

            self._run(app)

            self.assertIn(
                "Continue the demonstration", [button.label for button in app.button]
            )
            captions = "\n".join(caption.value for caption in app.caption)
            self.assertIn("Prepared Build Week journey", captions)


if __name__ == "__main__":
    unittest.main()
