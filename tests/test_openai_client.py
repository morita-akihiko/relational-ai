import os
import unittest
from types import SimpleNamespace
from unittest.mock import Mock, patch

from implementation.openai_client import (
    DEFAULT_MODEL,
    OpenAIConfigurationError,
    generate_response,
)
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
        self.assertIn("direct answer", CONVENTIONAL_DEMO_INSTRUCTIONS)
        self.assertNotIn("Article 12", CONVENTIONAL_DEMO_INSTRUCTIONS)


if __name__ == "__main__":
    unittest.main()
