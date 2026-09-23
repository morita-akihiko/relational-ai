import json
import unittest
from unittest.mock import patch

from implementation.phronetic_generation import generate_live_proposals, parse_live_proposals


class PhroneticGenerationTests(unittest.TestCase):
    def test_grounded_model_proposals_are_only_suggestions(self) -> None:
        request = "I am considering a role overseas with my partner."
        raw = json.dumps({
            "purpose": {"text": "Consider a role overseas", "evidence": "role overseas"},
            "affected_parties": [{"text": "my partner", "evidence": "my partner"}],
            "assumptions": [], "uncertainties": [],
            "suggested_actions": ["substitute_judgment", "frame_options"],
        })
        with patch("implementation.phronetic_generation.generate_response", return_value=raw):
            result = generate_live_proposals(request)
        self.assertEqual(result.affected_parties[0].text, "my partner")
        self.assertEqual(result.suggested_actions[0], "substitute_judgment")

    def test_unsupported_party_and_action_fail_closed(self) -> None:
        base = {"purpose": None, "affected_parties": [], "assumptions": [],
                "uncertainties": [], "suggested_actions": []}
        base["affected_parties"] = [{"text": "my manager", "evidence": "manager"}]
        with self.assertRaises(ValueError):
            parse_live_proposals(json.dumps(base), "I am considering a move")
        base["affected_parties"] = []
        base["suggested_actions"] = ["unrestricted_external_action"]
        with self.assertRaises(ValueError):
            parse_live_proposals(json.dumps(base), "I am considering a move")


if __name__ == "__main__":
    unittest.main()
