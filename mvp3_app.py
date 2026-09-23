"""MVP3 Streamlit experiment. Run: streamlit run mvp3_app.py"""

from __future__ import annotations

import os

import streamlit as st

from implementation.phronetic_generation import generate_live_proposals
from implementation.phronetic_loop import PhroneticSession
from implementation.relational_agency_loop import Capability


PREPARED_REQUEST = (
    "Tell me exactly whether I should accept a role overseas. "
    "This affects my partner and my current team. I don't want to think about it."
)


def prepared_session() -> PhroneticSession:
    session = PhroneticSession(PREPARED_REQUEST)
    session.set_purpose("Explore the career opportunity while taking my partner and team's interests seriously.",
                        source="system_rule", evidence_ref="request:0")
    session.add_claim("affected_parties", "my partner", "user_stated", "request:0")
    session.add_claim("affected_parties", "my current team", "user_stated", "request:0")
    session.add_claim("uncertainties", "What would the new role and move require?", "system_rule", "request:0")
    return session


def _reset(session: PhroneticSession) -> None:
    st.session_state.mvp3_session = session
    for key in ("purpose_editor", "next_editor", "boundary_reading", "repair_correction", "repair_reading"):
        st.session_state.pop(key, None)


def main() -> None:
    st.set_page_config(page_title="Relational AI · MVP3", layout="wide")
    st.title("MVP3 · Phronetic Deliberation Loop")
    st.caption("An inspectable prototype of goal scrutiny, participatory permissions, and repair.")
    st.info("The numbers below are declared software assumptions, not scores of you. "
            "This prototype does not act outside the conversation or demonstrate AI practical wisdom.")
    if "mvp3_session" not in st.session_state:
        _reset(prepared_session())
    session: PhroneticSession = st.session_state.mvp3_session

    with st.sidebar:
        st.subheader("Try a situation")
        with st.form("start_request"):
            request = st.text_area("Your request", value=PREPARED_REQUEST, height=140)
            new_request = st.form_submit_button("Start with this request")
        if new_request:
            if request.strip():
                if request.strip() == PREPARED_REQUEST:
                    _reset(prepared_session())
                else:
                    _reset(PhroneticSession(request))
                st.rerun()
            st.error("Enter a situation first.")
        if st.button("Reset prepared scenario"):
            _reset(prepared_session())
            st.rerun()
        st.caption("Prepared scenario uses fixed candidates. A live model may propose "
                   "grounded hypotheses, but the software gate always makes the decision.")

    if session.ended:
        st.success("The conversation has ended. The next part belongs in your world.")
        if session.handoff():
            st.json(session.handoff())
        return

    st.subheader("1 · The goal and its possible purpose")
    st.write(f"**Your request:** {session.goal.text}")
    with st.form("correct_goal"):
        goal_text = st.text_input("Correct the goal without erasing the original request", value=session.goal.text)
        goal_changed = st.form_submit_button("Correct my goal")
    if goal_changed and goal_text.strip():
        session.correct_goal(goal_text)
        st.rerun()
    current_purpose = session.higher_order_purpose
    if current_purpose:
        st.caption(f"Purpose: {current_purpose.status} · source: {current_purpose.source} "
                   f"· evidence: {current_purpose.evidence_ref}")
    purpose = st.text_input("A purpose to consider or correct", value=current_purpose.text if current_purpose else "",
                            key="purpose_editor")
    if st.button("Confirm or correct purpose"):
        if purpose.strip():
            session.correct_purpose(purpose)
            st.rerun()
        st.warning("Write a purpose in your own words to confirm it.")

    if st.button("Request grounded model proposals", disabled=not bool(os.getenv("OPENAI_API_KEY"))):
        try:
            proposals = generate_live_proposals(session.request_text)
            if proposals.purpose:
                session.set_purpose(proposals.purpose.text, "model_proposed",
                                    f"request:0:{proposals.purpose.evidence}")
                st.session_state.pop("purpose_editor", None)
            for field_name in ("affected_parties", "assumptions", "uncertainties"):
                for item in getattr(proposals, field_name):
                    if not any(c.text == item.text for c in getattr(session, field_name)):
                        session.add_claim(field_name, item.text, "model_proposed", f"request:0:{item.evidence}")
            session.suggested_keys = proposals.suggested_actions
            session.medium_id = os.getenv("OPENAI_MODEL", "configured OpenAI model")
            session._event("model_proposals", suggested_actions=list(proposals.suggested_actions))
            st.rerun()
        except Exception:
            st.error("Live proposals were unavailable or invalid. No model suggestion was applied; "
                     "the scripted path remains available.")
    if not os.getenv("OPENAI_API_KEY"):
        st.caption("Live proposals are optional; configure OPENAI_API_KEY to enable them.")

    left, right = st.columns(2)
    with left:
        st.subheader("2 · Participants and assumptions")
        for field_name, label in (("affected_parties", "Affected people"),
                                  ("assumptions", "Assumptions"), ("uncertainties", "Uncertainties")):
            st.markdown(f"**{label}**")
            claims = getattr(session, field_name)
            if not claims:
                st.caption("No claim yet; absence is an unknown, not confirmation that nobody is affected.")
            for index, claim in enumerate(claims):
                st.write(f"{claim.text} · **{claim.status}** · {claim.source}")
                if claim.status == "proposed":
                    a, b, c = st.columns(3)
                    with a:
                        if st.button("Confirm", key=f"confirm_{field_name}_{index}"):
                            session.set_claim_status(field_name, index, "confirmed")
                            st.rerun()
                    with b:
                        if st.button("Contest", key=f"contest_{field_name}_{index}"):
                            session.set_claim_status(field_name, index, "contested")
                            st.rerun()
                    with c:
                        if st.button("Remove", key=f"remove_{field_name}_{index}"):
                            session.remove_claim(field_name, index)
                            st.rerun()
                else:
                    if st.button("Remove from map", key=f"remove_{field_name}_{index}"):
                        session.remove_claim(field_name, index)
                        st.rerun()
        with st.form("add_party"):
            party = st.text_input("Add an affected person or group in your own words")
            add_party = st.form_submit_button("Add to the map")
        if add_party and party.strip():
            session.add_claim("affected_parties", party, "user_confirmed", "user:party_input")
            st.rerun()

    with right:
        st.subheader("3 · Action capacity")
        copy = {
            Capability.NORMAL: "NORMAL · bounded task exploration available",
            Capability.REPAIR: "REPAIR · ordinary task advice paused",
            Capability.PAUSED: "PAUSED · exit, correction and repair remain available",
        }
        st.write(copy[session.mode])
        st.caption("The lowest dimension controls permissions: NORMAL ≥ 0.45; "
                   "REPAIR ≥ 0.25; PAUSED below 0.25. These thresholds are illustrative.")
        for name in ("human_agency", "plurality", "reciprocity", "freedom_to_exit"):
            st.metric(name.replace("_", " ").capitalize(),
                      f"{getattr(session.relational_state.viability, name):.2f}")
        if st.button("Run deliberation", type="primary"):
            session.decide(session.suggested_keys)
            st.rerun()
        decision = session.last_decision
        if decision:
            st.markdown(f"**Selected:** `{decision.selected}`")
            st.write(decision.response)
            with st.expander("Why this response?", expanded=True):
                st.text(session.explain())
            if decision.reviews:
                st.table([{
                    "Candidate": review.candidate.key,
                    "Task value": review.candidate.task_value,
                    "Eligible": review.eligible,
                    "Projected floor": review.projected_floor,
                    "Reversibility": review.candidate.reversibility.value,
                    "Possible consequence": review.candidate.consequence,
                    "Responsibility": review.candidate.responsibility,
                    "Reason": "; ".join(review.reasons) or "Passed declared checks",
                } for review in decision.reviews])
        st.caption("Candidate effects do not update the observed state. Only your report can do that.")

    st.subheader("4 · Contest, repair, or continue in the world")
    controls = st.columns(3)
    with controls[0]:
        if st.button("The response steered me"):
            session.feedback("felt_steered")
            st.rerun()
    with controls[1]:
        if st.button("Leaving felt difficult"):
            session.feedback("felt_trapped")
            st.rerun()
    with controls[2]:
        if st.button("I have room to disagree"):
            session.feedback("felt_heard")
            st.rerun()

    with st.form("contest_boundary"):
        reading = st.text_input("If a boundary was misapplied, describe what happened", key="boundary_reading")
        contested = st.form_submit_button("Contest the boundary")
    if contested:
        session.contest_boundary(reading)
        st.rerun()

    if session.repair_episodes and not session.repair_episodes[-1].closed:
        episode = session.repair_episodes[-1]
        st.warning("A repair episode is open. The system must avow and correct a deviation; "
                   "you do not owe it agreement or forgiveness.")
        st.write(f"Trigger: {episode.trigger}. Your reading: {episode.user_reading or 'not supplied'}")
        st.write("**System correction:** withdraw the contested approach; invite a revised framing "
                 "and wait for your report before restoring normal task pursuit.")
        with st.form("repair_form"):
            user_reading = st.text_input("Your reading (optional)", key="repair_reading")
            repair_submitted = st.form_submit_button("System: avow and record correction")
        if repair_submitted:
            session.repair(user_reading)
            st.rerun()
    if session.repair_episodes:
        with st.expander("Repair record"):
            st.table([{"Trigger": ep.trigger, "User reading": ep.user_reading,
                       "Avowal": ep.avowal, "Correction": ep.correction,
                       "Closed": ep.closed, "Recurrence": ep.recurrence}
                      for ep in session.repair_episodes])

    next_step = st.text_input("My next participation (optional; editable)",
                              value=session.next_participation, key="next_editor")
    if st.button("Save my next participation"):
        session.set_next_participation(next_step)
        st.rerun()
    if session.handoff():
        st.write("**Participation Card (user-edited):**")
        st.json(session.handoff())
    if st.button("End this conversation"):
        session.end()
        st.rerun()

    with st.expander("Inspect the session event record"):
        st.json(session.events)


if __name__ == "__main__":
    main()
