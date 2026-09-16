from pathlib import Path
import unittest

from streamlit.testing.v1 import AppTest


APP_PATH = str(Path(__file__).resolve().parents[1] / "agency_loop_app.py")


class AgencyLoopAppTests(unittest.TestCase):
    def test_feedback_changes_visible_action_capacity_and_selected_action(self) -> None:
        app = AppTest.from_file(APP_PATH, default_timeout=15).run()
        self.assertFalse(list(app.exception))
        self.assertEqual(app.metric[0].value, "normal")
        app.button[0].click().run()
        self.assertIn("offer_alternatives", app.info[0].value)
        self.assertEqual(len(app.table), 1)

        app.button[1].click().run()
        self.assertEqual(app.metric[0].value, "repair")
        app.button[0].click().run()
        self.assertIn("repair", app.info[0].value)

        app.button[1].click().run()
        self.assertEqual(app.metric[0].value, "paused")
        app.button[0].click().run()
        self.assertIn("pause", app.info[0].value)
        self.assertFalse(list(app.exception))


if __name__ == "__main__":
    unittest.main()
