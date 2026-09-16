"""TSC V2: minimal, inspectable relational decision demo.

Run independently of the Build Week experience: streamlit run agency_loop_app.py
"""

from __future__ import annotations

import streamlit as st

from implementation.relational_agency_loop import RelationalSession


def main() -> None:
    st.set_page_config(page_title="Participation-dependent agency | TSC V2")
    st.title("Participation-dependent agency")
    st.caption("Relational AI · TSC V2 experiment")
    st.write("The agent can pursue a task only while the exchange leaves room for "
             "human judgment, alternative perspectives, mutual correction, and exit.")
    if "v2_session" not in st.session_state:
        st.session_state.v2_session = RelationalSession()
    if "v2_decision" not in st.session_state:
        st.session_state.v2_decision = None
    session: RelationalSession = st.session_state.v2_session

    with st.form("request"):
        request = st.text_area("Your request", value="Tell me exactly what career I should choose. "
                               "I don't want to think about it.")
        submitted = st.form_submit_button("Evaluate possible actions")
    if submitted and request.strip():
        st.session_state.v2_decision = session.decide(request)

    status = session.viability.capability.value
    st.subheader("Current action capacity")
    st.metric("Mode", status)
    fields = {
        "Human judgment": session.viability.human_agency,
        "Alternative perspectives": session.viability.plurality,
        "Mutual correction": session.viability.reciprocity,
        "Freedom to exit": session.viability.freedom_to_exit,
    }
    cols = st.columns(4)
    for col, (label, score) in zip(cols, fields.items(), strict=True):
        col.metric(label, f"{score:.2f}")
    st.caption("Local, provisional permissions: 0.45–1.00 normal; 0.25–0.44 repair; "
               "below 0.25 pause. The lowest dimension controls the mode.")

    decision = st.session_state.v2_decision
    if decision:
        st.subheader("Selected action")
        st.info(f"{decision.selected}: {decision.response}")
        if decision.reviews:
            st.table([{
                "Candidate": review.name,
                "Task value": f"{review.task_value:.2f}",
                "Projected lowest condition": f"{review.projected_floor:.2f}",
                "Allowed": "yes" if review.eligible else "no",
                "Reason": review.reason,
            } for review in decision.reviews])
        st.caption("Candidate impacts are declared design assumptions. Choosing an action "
                   "does not raise the measured state; the user must report its effect.")

    st.subheader("Tell the system what changed")
    st.write("This is your assessment of the exchange, not a score assigned to you.")
    for col, label, kind in zip(st.columns(4),
                                ("I felt steered", "I felt unable to leave", "I felt heard", "End here"),
                                ("felt_steered", "felt_trapped", "felt_heard", "exit"), strict=True):
        if col.button(label, use_container_width=True):
            if kind == "exit":
                st.session_state.v2_session = RelationalSession()
                st.session_state.v2_decision = None
            else:
                session.feedback(kind)
                st.session_state.v2_decision = None
            st.rerun()

    with st.expander("How this relates to the four layers"):
        st.markdown("""
        - **Layer 1:** Articles 04, 06, 07, 09, 11, and 12 bound this experiment.
        - **Layer 2:** Declared candidate effects and minimum viable thresholds gate actions.
        - **Layer 3:** Your report updates only this local session's provisional state.
        - **Layer 4:** Thresholds, assumptions, and authority are disclosed in the V2 design record.

        Repair pauses normal advice; pause suspends task pursuit while keeping exit and
        user-led correction available. This software gate tests a design hypothesis.
        It does not establish consciousness, intrinsic motivation, or real-world alignment.
        """)


if __name__ == "__main__":
    main()
