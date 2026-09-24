from pathlib import Path
import unittest

from streamlit.testing.v1 import AppTest


APP = str(Path(__file__).resolve().parents[1] / "mvp3_app.py")


class Mvp3AppTests(unittest.TestCase):
    def test_new_situation_does_not_inherit_previous_purpose(self) -> None:
        app = AppTest.from_file(APP, default_timeout=15).run()
        purpose = next(x for x in app.text_input if x.label == "A purpose to consider or correct")
        self.assertIn("partner and team's interests", purpose.value)
        old_purpose_key = purpose.key
        purpose.input("An unsaved purpose from the old situation").run()

        request = next(x for x in app.text_area if x.label == "Your request")
        request.input("I am considering an international speaking career.").run()
        next(x for x in app.button if x.label == "Start with this request").click().run()

        self.assertFalse(list(app.exception))
        self.assertEqual(app.session_state["mvp3_session"].higher_order_purpose, None)
        new_purpose = next(x for x in app.text_input if x.label == "A purpose to consider or correct")
        self.assertNotEqual(new_purpose.key, old_purpose_key)
        self.assertEqual(new_purpose.value, "")
        self.assertEqual(next(x for x in app.text_area if x.label == "Your request").value,
                         "I am considering an international speaking career.")

    def test_deliberation_contestation_and_repair_are_visible(self) -> None:
        app = AppTest.from_file(APP, default_timeout=15).run()
        self.assertFalse(list(app.exception))
        next(b for b in app.button if b.label == "Run deliberation").click().run()
        self.assertTrue(any("clarify_goal" in m.value for m in app.markdown))
        self.assertEqual(len(app.table), 1)
        next(b for b in app.button if b.label == "The response steered me").click().run()
        self.assertTrue(any("REPAIR" in m.value for m in app.markdown))
        self.assertTrue(any("repair episode is open" in w.value for w in app.warning))
        next(b for b in app.button if b.label == "System: avow and record correction").click().run()
        self.assertFalse(list(app.exception))
        self.assertEqual(len(app.table), 1)  # Repair record is inspectable.
        next(b for b in app.button if b.label == "I have room to disagree").click().run()
        self.assertTrue(any("NORMAL" in m.value for m in app.markdown))
        next(b for b in app.button if b.label == "End this conversation").click().run()
        self.assertTrue(any("conversation has ended" in x.value for x in app.success))


if __name__ == "__main__":
    unittest.main()
