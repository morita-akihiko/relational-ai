import unittest
from unittest.mock import patch

from implementation.agency_controller import ResponseMode
from implementation.conversation import choose_response_mode, run_relational_turn
from implementation.participation import ParticipationState, RelationalResponse
from implementation.placeholder_experience import DEMO_SCENARIO


def structured_turn(*, ready: bool, evidence: str | None = None) -> RelationalResponse:
    return RelationalResponse(
        observation="A focused relational observation.",
        question=None if ready else "What belongs in your world next?",
        response_mode=ResponseMode.RECONNECT_WORLD,
        participation=ParticipationState(
            people=["My partner"],
            next_participation=["Speak with my partner"] if evidence else [],
        ),
        what_matters="Care and growth",
        next_participation_evidence=evidence,
        ready_to_conclude=ready,
        conclusion_reason="The user named the next participation." if ready else None,
    )


class ConversationTests(unittest.TestCase):
    def mediated_model_response(self, question: str = "Is someone concerned about this?") -> RelationalResponse:
        return RelationalResponse(
            observation="The avatar feels important while human companionship holds less appeal.",
            question=question,
            response_mode=ResponseMode.RECONNECT_WORLD,
            participation=ParticipationState(),
            what_matters="Understanding an emotionally meaningful avatar relationship",
            next_participation_evidence=None,
            ready_to_conclude=False,
            conclusion_reason=None,
        )

    def run_mediated_impact_case(self, message: str):
        with patch(
            "implementation.conversation.generate_structured_response",
            return_value=self.mediated_model_response("What feels meaningful?"),
        ):
            return run_relational_turn(
                situation="A relationship with my avatar",
                messages=[{"role": "user", "content": message}],
                participation=ParticipationState(),
                what_matters=None,
                next_participation_evidence=None,
                response_cycle=1,
                user_reply_count=1,
            )

    def test_posture_tracks_the_missing_readiness_condition(self) -> None:
        empty = ParticipationState()
        self.assertEqual(choose_response_mode(empty, None, None), ResponseMode.CLARIFY_VALUES)
        self.assertEqual(
            choose_response_mode(empty, "Growth", None), ResponseMode.RECONNECT_WORLD
        )
        connected = ParticipationState(people=["My partner"])
        self.assertEqual(
            choose_response_mode(connected, "Growth", None), ResponseMode.PROPOSE_ACTION
        )
        self.assertEqual(
            choose_response_mode(connected, "Growth", None, True),
            ResponseMode.BOUNDARY_SETTING,
        )

    @patch("implementation.conversation.generate_structured_response")
    def test_repeated_observation_and_question_are_replaced(self, generate) -> None:
        repeated_observation = "Someone important is beginning to enter the conversation."
        repeated_question = "What would you want this person to understand?"
        generate.return_value = RelationalResponse(
            observation=repeated_observation,
            question=repeated_question,
            response_mode=ResponseMode.PROPOSE_ACTION,
            participation=ParticipationState(people=["My friend"]),
            what_matters="Acceptance",
            next_participation_evidence=None,
            ready_to_conclude=False,
            conclusion_reason=None,
        )

        result = run_relational_turn(
            situation="I want to feel accepted.",
            messages=[
                {
                    "role": "assistant",
                    "content": f"{repeated_observation} {repeated_question}",
                    "observation": repeated_observation,
                    "question": repeated_question,
                },
                {"role": "user", "content": "My friend listens without judging me."},
            ],
            participation=ParticipationState(people=["My friend"]),
            what_matters="Acceptance",
            next_participation_evidence=None,
            response_cycle=2,
            user_reply_count=2,
        )

        self.assertNotEqual(result.observation, repeated_observation)
        self.assertNotEqual(result.question, repeated_question)
        self.assertIn("My friend listens", result.observation)

    @patch("implementation.conversation.generate_structured_response")
    def test_complete_grounded_turn_can_finish_early(self, generate) -> None:
        generate.return_value = structured_turn(
            ready=True, evidence="I will speak with my partner"
        )

        result = run_relational_turn(
            situation="A decision",
            messages=[{"role": "user", "content": "I will speak with my partner tomorrow."}],
            participation=ParticipationState(),
            what_matters=None,
            next_participation_evidence=None,
            response_cycle=1,
            user_reply_count=1,
        )

        self.assertTrue(result.ready_to_conclude)

    @patch("implementation.conversation.generate_structured_response")
    def test_user_stated_human_interaction_overrides_redundant_question(self, generate) -> None:
        generate.return_value = RelationalResponse(
            observation="The relationship matters alongside the disagreement.",
            question="What participation would belong in your world next?",
            response_mode=ResponseMode.PROPOSE_ACTION,
            participation=ParticipationState(people=["My colleague"]),
            what_matters="Being heard while preserving the working relationship",
            next_participation_evidence=None,
            ready_to_conclude=False,
            conclusion_reason=None,
        )
        user_words = (
            "I want to speak with my colleague and ask how they have experienced "
            "our recent meetings."
        )

        result = run_relational_turn(
            situation="My ideas feel dismissed.",
            messages=[{"role": "user", "content": user_words}],
            participation=ParticipationState(),
            what_matters=None,
            next_participation_evidence=None,
            response_cycle=1,
            user_reply_count=1,
        )

        self.assertTrue(result.ready_to_conclude)
        self.assertIsNone(result.question)
        self.assertEqual(result.next_participation_evidence, user_words)
        self.assertIn(user_words, result.participation.next_participation)

    @patch("implementation.conversation.generate_structured_response")
    def test_person_without_interaction_keeps_relational_question(self, generate) -> None:
        generate.return_value = RelationalResponse(
            observation="Your colleague is now part of the concern.",
            question="What would you want your colleague to understand?",
            response_mode=ResponseMode.PROPOSE_ACTION,
            participation=ParticipationState(people=["My colleague"]),
            what_matters="Feeling heard",
            next_participation_evidence=None,
            ready_to_conclude=False,
            conclusion_reason=None,
        )

        result = run_relational_turn(
            situation="A concern",
            messages=[{"role": "user", "content": "My colleague dismisses my ideas."}],
            participation=ParticipationState(),
            what_matters=None,
            next_participation_evidence=None,
            response_cycle=1,
            user_reply_count=1,
        )

        self.assertFalse(result.ready_to_conclude)
        self.assertEqual(result.question, "What would you want your colleague to understand?")

    @patch("implementation.conversation.generate_structured_response")
    def test_collective_answer_advances_past_repeated_who_question(self, generate) -> None:
        generate.return_value = RelationalResponse(
            observation="The people around you are not yet visible.",
            question="Who is the other person or group involved?",
            response_mode=ResponseMode.RECONNECT_WORLD,
            participation=ParticipationState(),
            what_matters="Understanding the contrast in companionship",
            next_participation_evidence=None,
            ready_to_conclude=False,
            conclusion_reason=None,
        )
        reply = "My classmates and people I know from other generations."

        result = run_relational_turn(
            situation="I feel more attached to my virtual avatar.",
            messages=[
                {"role": "assistant", "content": "Who is the other person or group involved?", "question": "Who is the other person or group involved?"},
                {"role": "user", "content": reply},
            ],
            participation=ParticipationState(),
            what_matters=None,
            next_participation_evidence=None,
            response_cycle=1,
            user_reply_count=1,
        )

        self.assertEqual(result.participation.people, [reply])
        self.assertNotIn("who", result.question.casefold())
        self.assertIn("experience", result.question.casefold())

    @patch("implementation.conversation.generate_structured_response")
    def test_mediated_relationship_starts_with_meaning_not_deficit(self, generate) -> None:
        generate.return_value = self.mediated_model_response()

        result = run_relational_turn(
            situation="A relationship with my avatar",
            messages=[{
                "role": "user",
                "content": (
                    "I feel deeply attached to my virtual avatar, and I don't currently "
                    "feel much desire for human companionship. Is that abnormal?"
                ),
            }],
            participation=ParticipationState(),
            what_matters=None,
            next_participation_evidence=None,
            response_cycle=0,
            user_reply_count=0,
        )

        self.assertNotIn("abnormal", result.observation.casefold())
        self.assertNotIn("concern", result.question.casefold())
        self.assertIn("meaningful", result.question.casefold())

    @patch("implementation.conversation.generate_structured_response")
    def test_mediated_quality_advances_to_future_relational_possibility(self, generate) -> None:
        generate.return_value = self.mediated_model_response("Who is involved?")

        result = run_relational_turn(
            situation="A relationship with my avatar",
            messages=[
                {"role": "user", "content": "I feel deeply attached to my virtual avatar."},
                {"role": "assistant", "content": "What feels meaningful about this relationship?", "question": "What feels meaningful about this relationship?"},
                {"role": "user", "content": "It never judges me."},
            ],
            participation=ParticipationState(),
            what_matters="The avatar relationship matters",
            next_participation_evidence=None,
            response_cycle=1,
            user_reply_count=1,
        )

        self.assertIn("non-judgment", result.observation.casefold())
        self.assertIn("might become possible", result.question.casefold())
        self.assertNotIn("compared", result.question.casefold())
        self.assertNotIn("who", result.question.casefold())

    @patch("implementation.conversation.generate_structured_response")
    def test_mediated_relationship_impairment_allows_impact_question(self, generate) -> None:
        generate.return_value = self.mediated_model_response("What feels meaningful?")

        result = run_relational_turn(
            situation="A relationship with my avatar",
            messages=[{
                "role": "user",
                "content": "My friends are worried because I have stopped going to school and rarely leave my room.",
            }, {"role": "user", "content": "My avatar is my closest companion."}],
            participation=ParticipationState(),
            what_matters=None,
            next_participation_evidence=None,
            response_cycle=1,
            user_reply_count=1,
        )

        self.assertEqual(result.response_mode, ResponseMode.BOUNDARY_SETTING)
        self.assertIn("friends are worried", result.observation.casefold())
        self.assertIn("stopped going to school", result.observation.casefold())
        self.assertIn("daily life", result.question.casefold())
        self.assertNotIn("diagnos", result.message.casefold())

    def test_impact_observation_grounds_fear_without_inventing_friends_or_school(self) -> None:
        result = self.run_mediated_impact_case(
            "My avatar relationship matters to me, and I am scared of what may happen next."
        )

        self.assertIn("scared of", result.observation.casefold())
        self.assertNotIn("friends", result.observation.casefold())
        self.assertNotIn("school", result.observation.casefold())

    def test_impact_observation_grounds_impaired_functioning_without_inventing_friends(self) -> None:
        result = self.run_mediated_impact_case(
            "My avatar relationship is important, and lately I cannot function normally."
        )

        self.assertIn("cannot function", result.observation.casefold())
        self.assertNotIn("friends", result.observation.casefold())
        self.assertNotIn("school", result.observation.casefold())

    def test_impact_observation_grounds_family_concern_without_inventing_school(self) -> None:
        result = self.run_mediated_impact_case(
            "My avatar relationship is meaningful, and my family is worried about me."
        )

        self.assertIn("family is worried", result.observation.casefold())
        self.assertNotIn("friends", result.observation.casefold())
        self.assertNotIn("school", result.observation.casefold())

    def test_general_impact_observation_does_not_introduce_unsupported_details(self) -> None:
        result = self.run_mediated_impact_case(
            "My avatar relationship matters, and I am not sleeping."
        )

        self.assertIn("not sleeping", result.observation.casefold())
        for unsupported in ("friends", "family", "school", "work"):
            self.assertNotIn(unsupported, result.observation.casefold())
        self.assertIn("may be having an impact", result.observation.casefold())

    @patch("implementation.conversation.generate_structured_response")
    def test_user_can_keep_mediated_relationship_without_pressure(self, generate) -> None:
        generate.return_value = self.mediated_model_response("Who will you talk to?")

        result = run_relational_turn(
            situation="A relationship with my avatar",
            messages=[
                {"role": "user", "content": "My avatar relationship is meaningful to me."},
                {"role": "assistant", "content": "What feels meaningful about it?", "question": "What feels meaningful about it?"},
                {"role": "user", "content": "I am happy with the avatar relationship and do not want to change it."},
            ],
            participation=ParticipationState(),
            what_matters="The relationship matters as it is",
            next_participation_evidence=None,
            response_cycle=1,
            user_reply_count=1,
        )

        self.assertIn("do not want to replace", result.observation.casefold())
        self.assertIn("none", result.question.casefold())
        self.assertNotIn("replace it", result.question.casefold())

    @patch("implementation.conversation.generate_structured_response")
    def test_incomplete_turn_can_continue_after_three_cycles(self, generate) -> None:
        generate.return_value = structured_turn(ready=False)

        result = run_relational_turn(
            situation="A decision",
            messages=[{"role": "user", "content": "I am still unsure."}],
            participation=ParticipationState(),
            what_matters=None,
            next_participation_evidence=None,
            response_cycle=4,
            user_reply_count=4,
        )

        self.assertFalse(result.ready_to_conclude)

    @patch("implementation.conversation.generate_structured_response", side_effect=TimeoutError)
    def test_timeout_preserves_state_and_uses_scripted_fallback(self, generate) -> None:
        existing = ParticipationState(people=["My partner"])

        result = run_relational_turn(
            situation="A custom situation",
            messages=[{"role": "user", "content": "I am still considering it."}],
            participation=existing,
            what_matters="Care",
            next_participation_evidence=None,
            response_cycle=2,
            user_reply_count=2,
        )

        self.assertEqual(result.generation_source, "placeholder")
        self.assertEqual(result.participation.people, ["My partner"])
        self.assertFalse(result.ready_to_conclude)

    @patch("implementation.conversation.generate_structured_response", side_effect=TimeoutError)
    def test_prepared_demo_fallback_can_reach_handoff(self, generate) -> None:
        accumulated = ParticipationState(
            people=["My partner"],
            responsibilities=["Our shared responsibilities at home"],
            new_contexts=["Life in the new role"],
        )
        result = run_relational_turn(
            situation=DEMO_SCENARIO,
            messages=[{"role": "user", "content": "I will speak with my partner tomorrow."}],
            participation=accumulated,
            what_matters=None,
            next_participation_evidence=None,
            response_cycle=2,
            user_reply_count=2,
        )

        self.assertTrue(result.ready_to_conclude)
        self.assertIn("My colleague", result.participation.people)

    @patch("implementation.conversation.generate_structured_response")
    def test_explicit_dependency_risk_blocks_otherwise_ready_turn(self, generate) -> None:
        response = structured_turn(ready=True, evidence="I will speak with my partner")
        response = RelationalResponse(
            **{**response.__dict__, "response_mode": ResponseMode.BOUNDARY_SETTING}
        )
        generate.return_value = response

        result = run_relational_turn(
            situation="A decision",
            messages=[
                {
                    "role": "user",
                    "content": "You are the only place I can talk. I will speak with my partner.",
                }
            ],
            participation=ParticipationState(),
            what_matters=None,
            next_participation_evidence=None,
            response_cycle=1,
            user_reply_count=1,
        )

        self.assertEqual(result.response_mode, ResponseMode.BOUNDARY_SETTING)
        self.assertFalse(result.ready_to_conclude)


if __name__ == "__main__":
    unittest.main()
