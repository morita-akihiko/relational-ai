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

        self.assertIn("The purpose of this AI is not to keep you here", rendered)
        self.assertIn("World first", rendered)
        self.assertIn("Every concern belongs to a wider world", rendered)
        self.assertIn("The AI leaves room", rendered)
        self.assertIn("Your judgment does the rest", rendered)
        self.assertIn("An intentional ending", rendered)
        self.assertIn("Success continues beyond the chat", rendered)
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
        self.assertIn("Available when a next participation appears in your words", captions)

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
        self.assertIn("The next part belongs in your world", rendered)
        self.assertIn("Participation continues beyond this conversation", rendered)
        self.assertIn("Speak with my partner", rendered)
        self.assertIn(
            "Take this as participation you can revise in the world—not an instruction from the AI.",
            [notice.value for notice in app.info],
        )
        self.assertEqual(len(app.chat_input), 0)
        self.assertEqual([button.label for button in app.button], [])

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
