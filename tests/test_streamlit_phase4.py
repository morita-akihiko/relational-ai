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
        self.assertLess(rendered.index("Participation taking shape"), rendered.index("The exchange"))
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
        self.assertIn("The next part belongs in your world", rendered)
        self.assertIn("Speak with my partner", rendered)
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


if __name__ == "__main__":
    unittest.main()
