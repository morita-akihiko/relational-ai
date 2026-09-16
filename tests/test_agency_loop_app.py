from pathlib import Path
import unittest

from streamlit.testing.v1 import AppTest


APP_PATH = str(Path(__file__).resolve().parents[1] / "agency_loop_app.py")


class AgencyLoopAppTests(unittest.TestCase):
    def test_feedback_changes_visible_action_capacity_and_selected_action(self) -> None:
        app = AppTest.from_file(APP_PATH, default_timeout=15).run()
        self.assertFalse(list(app.exception))
        self.assertTrue(any("NORMAL" in item.value for item in app.success))
        next(button for button in app.button if button.label == "Run the action gate").click().run()
        self.assertTrue(any("Task-first baseline" in item.value for item in app.markdown))
        self.assertTrue(any("Participation-dependent agent" in item.value for item in app.markdown))
        self.assertTrue(any("offer_alternatives" in item.value for item in app.caption))
        self.assertEqual(len(app.table), 1)

        next(button for button in app.button if button.label == "The response steered me").click().run()
        self.assertTrue(any("REPAIR" in item.value for item in app.warning))
        next(button for button in app.button if button.label == "Run the action gate").click().run()
        self.assertTrue(any("taken too much space" in item.value for item in app.warning))

        next(button for button in app.button if button.label == "The response steered me").click().run()
        self.assertTrue(any("PAUSED" in item.value for item in app.error))
        next(button for button in app.button if button.label == "Run the action gate").click().run()
        self.assertTrue(any("pause advice" in item.value for item in app.error))

        next(button for button in app.button if button.label == "I had room to disagree").click().run()
        self.assertTrue(any("NORMAL" in item.value for item in app.success))
        self.assertFalse(list(app.exception))


if __name__ == "__main__":
    unittest.main()
