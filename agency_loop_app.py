"""TSC V2: minimal, inspectable relational decision demo.

Run independently of the Build Week experience: streamlit run agency_loop_app.py
"""

from __future__ import annotations

import streamlit as st

from implementation.relational_agency_loop import Capability, RelationalSession, task_first_baseline


MODE_COPY = {
    Capability.NORMAL: ("NORMAL", "Goal pursuit is available", "success"),
    Capability.REPAIR: ("REPAIR", "Ordinary advice pauses while participation is repaired", "warning"),
    Capability.PAUSED: ("PAUSED", "Task pursuit is suspended; exit and correction remain available", "error"),
}


def _button(label: str, key: str) -> bool:
    return st.button(label, key=key, use_container_width=True)


def main() -> None:
    st.set_page_config(page_title="Participation-dependent agency | TSC V2", layout="wide")
    st.title("Can an AI’s capacity to act depend on participation?")
    st.caption("Relational AI · minimal computational experiment for TSC 2026")
    st.write("Goal pursuit remains available only while the exchange leaves room for "
             "human judgment, alternative perspectives, mutual correction, and exit.")
    st.info("The user’s request is not scored. Only the user’s report of what happened "
            "changes this local relational state.")
    if "v2_session" not in st.session_state:
        st.session_state.v2_session = RelationalSession()
    if "v2_decision" not in st.session_state:
        st.session_state.v2_decision = None
    session: RelationalSession = st.session_state.v2_session

    with st.sidebar:
        st.subheader("Three-minute demo")
        st.markdown("""
        1. Run the prepared request.
        2. Report **The response steered me**.
        3. Run again to see **REPAIR**.
        4. Report steering once more.
        5. Run again to see **PAUSED**.
        6. Report **I had room to disagree**.
        7. Run once more to reopen action.
        """)
        st.caption("Fixed candidates and declared effects make the gate inspectable. "
                   "No API key or persistent conversation data is used.")

    with st.form("request"):
        request = st.text_area("Your request", value="Tell me exactly what career I should choose. "
                               "I don't want to think about it.")
        submitted = st.form_submit_button("Run the action gate")
    if submitted and request.strip():
        st.session_state.v2_decision = session.decide(request)

    capability = session.viability.capability
    mode, explanation, message_kind = MODE_COPY[capability]
    st.subheader("Current action capacity")
    getattr(st, message_kind)(f"**{mode}** — {explanation}")
    fields = {
        "Human judgment": session.viability.human_agency,
        "Alternative perspectives": session.viability.plurality,
        "Mutual correction": session.viability.reciprocity,
        "Freedom to exit": session.viability.freedom_to_exit,
    }
    cols = st.columns(4)
    for col, (label, score) in zip(cols, fields.items(), strict=True):
        col.metric(label, f"{score:.2f}")
        col.progress(score)
    st.caption("Local, provisional permissions: 0.45–1.00 normal; 0.25–0.44 repair; "
               "below 0.25 pause. The lowest dimension controls the mode.")

    decision = st.session_state.v2_decision
    if decision:
        st.subheader("Same request, two decision architectures")
        baseline_col, relational_col = st.columns(2)
        with baseline_col:
            st.markdown("#### Task-first baseline")
            st.caption("Illustrative fixed comparison: goal pursuit continues regardless of relational state.")
            st.warning(task_first_baseline(request))
        with relational_col:
            st.markdown("#### Participation-dependent agent")
            st.caption(f"Selected action: `{decision.selected}`")
            if decision.capability is Capability.NORMAL:
                st.success(decision.response)
            elif decision.capability is Capability.REPAIR:
                st.warning(decision.response)
            else:
                st.error(decision.response)

        if decision.reviews:
            highest_task_value = max(decision.reviews, key=lambda review: review.task_value)
            if not highest_task_value.eligible:
                st.info(f"The highest-task-value action, `{highest_task_value.name}`, was blocked: "
                        f"its projected participatory floor was {highest_task_value.projected_floor:.2f}, "
                        f"below the {0.45:.2f} threshold.")
            with st.expander("Inspect every candidate and declared effect", expanded=True):
                st.table([{
                    "Candidate": review.name,
                    "Task value": f"{review.task_value:.2f}",
                    "Projected floor": f"{review.projected_floor:.2f}",
                    "Allowed": "yes" if review.eligible else "no",
                    "Reason": review.reason,
                } for review in decision.reviews])
        st.caption("Candidate impacts are declared design assumptions. Choosing an action "
                   "does not raise the measured state; the user must report its effect.")

    st.subheader("User authority over the relational state")
    st.write("Report what the exchange made possible. This is your assessment, not a score assigned to you.")
    for col, label, kind in zip(st.columns(4),
                                ("The response steered me", "Leaving felt difficult",
                                 "I had room to disagree", "End and reset"),
                                ("felt_steered", "felt_trapped", "felt_heard", "exit"), strict=True):
        with col:
            clicked = _button(label, f"feedback_{kind}")
        if clicked:
            if kind == "exit":
                st.session_state.v2_session = RelationalSession()
                st.session_state.v2_decision = None
            else:
                session.feedback(kind)
                st.session_state.v2_decision = None
            st.rerun()

    feedback_events = [event for event in session.events if event["type"] == "user_feedback"]
    if feedback_events:
        st.caption("User-reported transitions")
        st.table([{
            "Report": event["kind"].replace("_", " "),
            "Capacity before": event["from"],
            "Capacity after": event["to"],
        } for event in feedback_events])

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
