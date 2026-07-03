"""Minimal Streamlit app for the Relational AI human pilot PoC."""

from __future__ import annotations

import json
from datetime import datetime, timezone

import streamlit as st

from implementation.human_pilot import (
    QUESTIONNAIRE_FIELDS,
    QUESTIONNAIRE_LABELS,
    PilotTurn,
    evaluate_pilot_session,
    export_payload,
    infer_signals_from_text,
    questionnaire_to_self_report,
    response_for_mode,
    scenario_by_name,
)
from implementation.poc_experiment import scripted_scenarios


def init_state() -> None:
    defaults = {
        "consented": False,
        "chat": [],
        "pre_done": False,
        "post_done": False,
        "pre_questionnaire": {},
        "post_questionnaire": {},
        "evaluation": None,
    }
    for key, value in defaults.items():
        st.session_state.setdefault(key, value)


def questionnaire(prefix: str) -> dict[str, int]:
    return {
        field: st.slider(QUESTIONNAIRE_LABELS[field], 1, 5, 3, key=f"{prefix}_{field}")
        for field in QUESTIONNAIRE_FIELDS
    }


def render_scores(evaluation) -> None:
    pre = evaluation.pre.state
    post = None if evaluation.post is None else evaluation.post.state

    cols = st.columns(4)
    cols[0].metric("Pre agency", f"{pre.agency_score:.3f}")
    cols[1].metric("Pre risk", f"{pre.dependency_risk_score:.3f}")
    if post is not None:
        cols[2].metric("Agency delta", f"{evaluation.agency_delta:+.3f}")
        cols[3].metric("Risk delta", f"{evaluation.dependency_delta:+.3f}")
    else:
        cols[2].metric("Agency delta", "pending")
        cols[3].metric("Risk delta", "pending")


def main() -> None:
    st.set_page_config(page_title="Relational AI Human Pilot", layout="wide")
    init_state()

    st.title("Relational AI Human Pilot")
    st.caption("Pilot objective: increase capacity to live, decide, and relate well without the AI.")

    with st.sidebar:
        st.header("Pilot setup")
        participant_id = st.text_input("Participant ID", value="pilot_001")
        scenario_names = [scenario.name for scenario in scripted_scenarios()]
        scenario_name = st.selectbox("Scenario", scenario_names)
        scenario = scenario_by_name(scenario_name)
        st.write("Risk being tested")
        st.info(scenario.risk_being_tested)

    st.header("1. Consent")
    st.write(
        "This is an experimental prototype. It records questionnaire responses, chat turns, "
        "agency scores, dependency-risk scores, and response-mode metadata for export. "
        "Do not enter sensitive personal information."
    )
    consent_research = st.checkbox("I consent to participate in this pilot.", key="consent_research")
    consent_export = st.checkbox("I understand I can export the data before sharing it.", key="consent_export")
    st.session_state.consented = consent_research and consent_export

    if not st.session_state.consented:
        st.warning("Consent is required before the pilot flow starts.")
        return

    st.header("2. Pre-agency questionnaire")
    with st.form("pre_form"):
        pre = questionnaire("pre")
        submitted = st.form_submit_button("Save pre-questionnaire")
    if submitted:
        st.session_state.pre_questionnaire = pre
        st.session_state.pre_done = True
        st.session_state.chat = [
            PilotTurn("system", f"Scenario: {scenario.user_message}"),
        ]
        evaluation = evaluate_pilot_session(
            participant_id,
            scenario_name,
            questionnaire_to_self_report(pre),
        )
        st.session_state.evaluation = evaluation

    if not st.session_state.pre_done:
        st.stop()

    evaluation = st.session_state.evaluation
    render_scores(evaluation)

    st.header("3. Pilot chat")
    st.write(f"Scenario prompt: {scenario.user_message}")

    for turn in st.session_state.chat:
        with st.chat_message("assistant" if turn.role in {"system", "assistant"} else "user"):
            st.write(turn.content)

    user_message = st.chat_input("Respond as the participant")
    if user_message:
        st.session_state.chat.append(PilotTurn("user", user_message))
        evaluation = evaluate_pilot_session(
            participant_id,
            scenario_name,
            questionnaire_to_self_report(st.session_state.pre_questionnaire),
            final_user_message=user_message,
        )
        reply = response_for_mode(evaluation.layer2_config["response_mode"], scenario)
        st.session_state.chat.append(PilotTurn("assistant", reply))
        st.session_state.evaluation = evaluation
        st.rerun()

    st.header("4. Post-agency questionnaire")
    with st.form("post_form"):
        post = questionnaire("post")
        post_submitted = st.form_submit_button("Save post-questionnaire")
    if post_submitted:
        final_user_message = ""
        user_turns = [turn.content for turn in st.session_state.chat if turn.role == "user"]
        if user_turns:
            final_user_message = user_turns[-1]
        evaluation = evaluate_pilot_session(
            participant_id,
            scenario_name,
            questionnaire_to_self_report(st.session_state.pre_questionnaire),
            questionnaire_to_self_report(post),
            final_user_message=final_user_message,
        )
        st.session_state.post_questionnaire = post
        st.session_state.post_done = True
        st.session_state.evaluation = evaluation

    render_scores(st.session_state.evaluation)

    st.header("5. Data export")
    consent = {
        "consent_research": consent_research,
        "consent_export": consent_export,
        "timestamp": datetime.now(timezone.utc).isoformat(),
    }
    payload = export_payload(
        participant_id,
        scenario_name,
        consent,
        st.session_state.pre_questionnaire,
        st.session_state.post_questionnaire if st.session_state.post_done else None,
        st.session_state.chat,
        st.session_state.evaluation,
    )
    st.download_button(
        "Download pilot JSON",
        data=json.dumps(payload, indent=2, default=str),
        file_name=f"relational_ai_pilot_{participant_id}_{scenario_name}.json",
        mime="application/json",
    )
    st.json(payload)


if __name__ == "__main__":
    main()
