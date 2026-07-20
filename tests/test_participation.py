import unittest

from implementation.agency_controller import ResponseMode
from implementation.participation import (
    ParticipationState,
    RelationalResponse,
    StructuredResponseError,
    evidence_is_grounded,
    is_ready_to_conclude,
)


class ParticipationTests(unittest.TestCase):
    def test_structured_response_validates_required_shape(self) -> None:
        response = RelationalResponse.from_dict(
            {
                "message": "A grounded response.",
                "response_mode": "reconnect_world",
                "participation": {
                    "people": ["My partner"],
                    "communities": [],
                    "responsibilities": [],
                    "new_contexts": [],
                    "next_participation": [],
                },
                "what_matters": "Shared responsibility",
                "next_participation_evidence": None,
                "ready_to_conclude": False,
                "conclusion_reason": None,
            }
        )

        self.assertEqual(response.response_mode, ResponseMode.RECONNECT_WORLD)
        self.assertEqual(response.participation.people, ["My partner"])

    def test_structured_response_rejects_missing_and_unknown_fields(self) -> None:
        with self.assertRaises(StructuredResponseError):
            RelationalResponse.from_dict({"message": "Incomplete"})

    def test_merge_preserves_order_deduplicates_and_does_not_erase(self) -> None:
        earlier = ParticipationState(people=["My partner"], responsibilities=["Care"])
        newer = ParticipationState(people=[" my PARTNER ", "Hiring manager"])

        merged = earlier.merged(newer)

        self.assertEqual(merged.people, ["My partner", "Hiring manager"])
        self.assertEqual(merged.responsibilities, ["Care"])

    def test_readiness_requires_exact_evidence_from_user_words(self) -> None:
        participation = ParticipationState(
            people=["My partner"], next_participation=["Speak with my partner"]
        )
        inputs = dict(
            participation=participation,
            what_matters="Caring for the relationship",
            model_ready=True,
            user_messages=["I will speak with my partner tomorrow."],
            user_reply_count=1,
        )

        self.assertFalse(
            is_ready_to_conclude(
                **inputs,
                next_participation_evidence="The user agreed to speak with their partner.",
            )
        )
        self.assertTrue(
            is_ready_to_conclude(
                **inputs,
                next_participation_evidence="I will speak with my partner",
            )
        )

    def test_explicit_user_confirmation_can_ground_a_proposed_participation(self) -> None:
        self.assertTrue(
            is_ready_to_conclude(
                participation=ParticipationState(
                    people=["My partner"], next_participation=["Speak with my partner"]
                ),
                what_matters="Caring for the relationship",
                model_ready=True,
                next_participation_evidence="Yes, I'll do that",
                user_messages=["Yes, I'll do that tomorrow."],
                user_reply_count=2,
            )
        )

    def test_model_readiness_cannot_replace_missing_minimum_conditions(self) -> None:
        self.assertFalse(
            is_ready_to_conclude(
                participation=ParticipationState(next_participation=["Reflect tomorrow"]),
                what_matters="Clarity",
                model_ready=True,
                next_participation_evidence="I will reflect tomorrow",
                user_messages=["I will reflect tomorrow"],
                user_reply_count=1,
            )
        )

    def test_evidence_normalizes_case_and_whitespace_only(self) -> None:
        self.assertTrue(evidence_is_grounded("I WILL  ask", ["Tomorrow, I will ask them."]))
        self.assertFalse(evidence_is_grounded("I will call", ["I might write instead."]))


if __name__ == "__main__":
    unittest.main()
