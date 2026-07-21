import unittest

from implementation.agency_controller import ResponseMode
from implementation.participation import (
    OBSERVATION_MAX_WORDS,
    QUESTION_MAX_WORDS,
    ParticipationState,
    RelationalResponse,
    StructuredResponseError,
    build_participation_review,
    evidence_is_grounded,
    is_ready_to_conclude,
    human_reference_from_reply,
    participation_review_ready,
)


class ParticipationTests(unittest.TestCase):
    def test_review_readiness_uses_depth_or_relational_movement(self) -> None:
        self.assertFalse(participation_review_ready(ParticipationState(), 3))
        self.assertTrue(participation_review_ready(ParticipationState(), 4))
        self.assertTrue(
            participation_review_ready(
                ParticipationState(
                    people=["My friend"], next_participation=["Talk with my friend"]
                ),
                2,
            )
        )
        self.assertFalse(
            participation_review_ready(
                ParticipationState(next_participation=["Reflect on it"]), 2
            )
        )

    def test_review_is_dynamic_grounded_and_opens_beyond_the_ai(self) -> None:
        review = build_participation_review(
            messages=[
                {"role": "user", "content": "I want my friend to accept me."},
                {"role": "user", "content": "I may listen more openly to my family."},
            ],
            participation=ParticipationState(
                people=["My friend"],
                next_participation=["Listen more openly to my family"],
            ),
            what_matters="Acceptance",
        )

        self.assertIn("My friend", review.people)
        self.assertIn("accept me", review.shift)
        self.assertIn("Listen more openly", review.emerging_possibility)
        self.assertEqual(
            review.bridge_question,
            "What feels worth carrying into your life beyond this conversation?",
        )

    def test_collective_human_references_do_not_require_proper_names(self) -> None:
        for reply in (
            "My classmates",
            "People my age and people from other generations",
            "My colleagues",
            "My family",
        ):
            self.assertEqual(human_reference_from_reply(reply), reply)

    def test_structured_response_validates_required_shape(self) -> None:
        response = RelationalResponse.from_dict(
            {
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
            RelationalResponse.from_dict({"observation": "Incomplete"})

    def test_hard_word_caps_reject_only_overlong_turn_parts(self) -> None:
        base = {
            "observation": "Grounded observation.",
            "question": "What belongs in your world?",
            "response_mode": "reconnect_world",
            "participation": {name: [] for name in (
                "people", "communities", "responsibilities", "new_contexts", "next_participation"
            )},
            "what_matters": None,
            "next_participation_evidence": None,
            "ready_to_conclude": False,
            "conclusion_reason": None,
        }

        RelationalResponse.from_dict(
            {**base, "observation": "word " * OBSERVATION_MAX_WORDS}
        )
        RelationalResponse.from_dict(
            {**base, "question": "word " * QUESTION_MAX_WORDS}
        )
        with self.assertRaises(StructuredResponseError):
            RelationalResponse.from_dict(
                {**base, "observation": "word " * (OBSERVATION_MAX_WORDS + 1)}
            )
        with self.assertRaises(StructuredResponseError):
            RelationalResponse.from_dict(
                {**base, "question": "word " * (QUESTION_MAX_WORDS + 1)}
            )

    def test_ready_turn_has_no_question_and_non_ready_turn_requires_one(self) -> None:
        participation = {
            "people": ["My partner"],
            "communities": [],
            "responsibilities": [],
            "new_contexts": [],
            "next_participation": ["Speak with my partner"],
        }
        ready = {
            "observation": "The next participation is yours.",
            "question": None,
            "response_mode": "support_reflection",
            "participation": participation,
            "what_matters": "Care",
            "next_participation_evidence": "I will speak with my partner",
            "ready_to_conclude": True,
            "conclusion_reason": "The user named it.",
        }

        RelationalResponse.from_dict(ready)
        with self.assertRaises(StructuredResponseError):
            RelationalResponse.from_dict({**ready, "question": "Continue?"})
        with self.assertRaises(StructuredResponseError):
            RelationalResponse.from_dict(
                {**ready, "ready_to_conclude": False, "conclusion_reason": None}
            )

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
