import json
import os
import unittest
from types import SimpleNamespace
from unittest.mock import Mock, patch

from implementation.openai_client import (
    DEFAULT_MODEL,
    OpenAIConfigurationError,
    generate_response,
    generate_structured_response,
)
from implementation.agency_controller import ResponseMode
from implementation.participation import StructuredResponseError
from implementation.prompts import CONVENTIONAL_DEMO_INSTRUCTIONS, RELATIONAL_INSTRUCTIONS


class OpenAIClientTests(unittest.TestCase):
    def test_missing_api_key_is_explicit(self) -> None:
        with patch.dict(os.environ, {}, clear=True):
            with self.assertRaises(OpenAIConfigurationError):
                generate_response("Instructions", [{"role": "user", "content": "Hello"}])

    @patch("implementation.openai_client.OpenAI")
    def test_responses_api_call_is_direct_and_readable(self, openai_class: Mock) -> None:
        response = SimpleNamespace(output_text="  A grounded response.  ")
        client = openai_class.return_value
        client.responses.create.return_value = response
        messages = [{"role": "user", "content": "A situation"}]

        result = generate_response("Relational instructions", messages, api_key="test-key")

        self.assertEqual(result, "A grounded response.")
        openai_class.assert_called_once_with(api_key="test-key")
        client.responses.create.assert_called_once_with(
            model=DEFAULT_MODEL,
            instructions="Relational instructions",
            input=messages,
        )

    def test_prompt_policies_make_the_philosophical_difference_explicit(self) -> None:
        self.assertIn("world beyond this conversation", RELATIONAL_INSTRUCTIONS)
        self.assertIn("finite conversation", RELATIONAL_INSTRUCTIONS)
        self.assertIn("about 18 words", RELATIONAL_INSTRUCTIONS)
        self.assertIn("Never exceed 28 observation words", RELATIONAL_INSTRUCTIONS)
        self.assertIn("direct answer", CONVENTIONAL_DEMO_INSTRUCTIONS)
        self.assertIn("35 words", CONVENTIONAL_DEMO_INSTRUCTIONS)
        self.assertNotIn("Article 12", CONVENTIONAL_DEMO_INSTRUCTIONS)

    @patch("implementation.openai_client.OpenAI")
    def test_structured_response_is_validated(self, openai_class: Mock) -> None:
        payload = {
            "observation": "A grounded observation.",
            "question": "Who else belongs in this situation?",
            "response_mode": "reconnect_world",
            "participation": {
                "people": ["My partner"],
                "communities": [],
                "responsibilities": [],
                "new_contexts": [],
                "next_participation": [],
            },
            "what_matters": "Care",
            "next_participation_evidence": None,
            "ready_to_conclude": False,
            "conclusion_reason": None,
        }
        openai_class.return_value.responses.create.return_value = SimpleNamespace(
            output_text=json.dumps(payload)
        )

        result = generate_structured_response(
            "Instructions",
            [{"role": "user", "content": "Hello"}],
            ResponseMode.RECONNECT_WORLD,
            api_key="test-key",
            timeout=3,
        )

        self.assertEqual(
            result.message,
            "A grounded observation. Who else belongs in this situation?",
        )
        openai_class.assert_called_once_with(api_key="test-key", timeout=3)
        call = openai_class.return_value.responses.create.call_args.kwargs
        self.assertEqual(call["text"]["format"]["type"], "json_schema")

    @patch("implementation.openai_client.OpenAI")
    def test_malformed_output_gets_one_repair_attempt(self, openai_class: Mock) -> None:
        client = openai_class.return_value
        client.responses.create.side_effect = [
            SimpleNamespace(output_text="not json"),
            SimpleNamespace(output_text="still not json"),
        ]

        with self.assertRaises(StructuredResponseError):
            generate_structured_response(
                "Instructions",
                [{"role": "user", "content": "Hello"}],
                ResponseMode.CLARIFY_VALUES,
                api_key="test-key",
            )

        self.assertEqual(client.responses.create.call_count, 2)


if __name__ == "__main__":
    unittest.main()
