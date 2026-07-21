"""Streamlit interface for the Relational AI MVP.

Live responses use the OpenAI Responses API when configured. Deterministic Phase 1
content remains available as a transparent fallback.
"""

from __future__ import annotations

from html import escape
import os

import streamlit as st

from implementation.conversation import run_relational_turn
from implementation.openai_client import OpenAIConfigurationError, generate_response
from implementation.participation import ParticipationReview
from implementation.participation import (
    ParticipationState,
    build_participation_review,
    participation_review_ready,
)
from implementation.placeholder_experience import (
    DEMO_REPLY_1,
    DEMO_REPLY_2,
    DEMO_SCENARIO,
    EXAMPLE_SITUATIONS,
    conventional_demo_response,
)
from implementation.prompts import CONVENTIONAL_DEMO_INSTRUCTIONS


SCREENS = ("landing", "conversation", "participation", "conclusion")
SCREEN_LABELS = {
    "landing": "Promise",
    "conversation": "Conversation",
    "participation": "Participation",
    "conclusion": "Release",
}


def init_state() -> None:
    defaults = {
        "screen": "landing",
        "mode": "normal",
        "situation": "",
        "messages": [],
        "response_count": 0,
        "participation": ParticipationState(),
        "latest_additions": ParticipationState(),
        "what_matters": None,
        "next_participation_evidence": None,
        "ready_to_conclude": False,
        "conventional_response": "",
        "generation_source": "placeholder",
        "generation_notice": "",
        "review_opened": False,
        "card": {
            "what_matters": "",
            "connected_to": "",
            "next_participation": "",
            "when_or_where": "",
        },
    }
    for key, value in defaults.items():
        st.session_state.setdefault(key, value)


def reset_experience() -> None:
    for key in (
        "screen",
        "mode",
        "situation",
        "messages",
        "response_count",
        "participation",
        "latest_additions",
        "what_matters",
        "next_participation_evidence",
        "ready_to_conclude",
        "conventional_response",
        "generation_source",
        "generation_notice",
        "review_opened",
        "card",
    ):
        st.session_state.pop(key, None)
    init_state()


def apply_styles() -> None:
    st.markdown(
        """
        <style>
        .stApp { background: #f7f5ef; color: #17211b; }
        .block-container { max-width: 1050px; padding-top: 2.5rem; padding-bottom: 4rem; }
        [data-testid="stSidebar"] { background: #ebe8df; }
        .eyebrow {
            color: #58705e; font-size: .78rem; font-weight: 700;
            letter-spacing: .12em; text-transform: uppercase; margin-bottom: .8rem;
        }
        .landing-eyebrow { font-size: .96rem; }
        .hero {
            font-family: Georgia, serif; font-size: clamp(2.3rem, 6vw, 4.8rem);
            line-height: 1.02; letter-spacing: -.035em; max-width: 900px;
            margin: 0 0 1.2rem;
        }
        .hero-sub { font-size: 1.18rem; line-height: 1.65; max-width: 690px; color: #4b5950; }
        .story-grid {
            display: grid; grid-template-columns: repeat(3, 1fr); gap: .75rem;
            margin: 1.6rem 0 2rem;
        }
        .story-card {
            padding: 1rem; border-top: 2px solid #91a68f; background: rgba(255,255,255,.45);
        }
        .story-card strong { display: block; margin-bottom: .25rem; color: #304d38; }
        .story-card span { color: #5a665e; line-height: 1.4; }
        .quiet-note {
            border-left: 3px solid #91a68f; padding: .65rem 1rem;
            color: #536057; background: rgba(255,255,255,.45); margin: 1rem 0 1.5rem;
        }
        .mode-card {
            min-height: 150px; padding: 1.25rem; border: 1px solid #d5d8ce;
            border-radius: 14px; background: rgba(255,255,255,.68);
        }
        .mode-card.relational { border-color: #708c72; background: #eef3eb; }
        .mode-label { font-size: .75rem; letter-spacing: .08em; text-transform: uppercase; color: #637067; }
        .mode-copy { font-family: Georgia, serif; font-size: 1.08rem; line-height: 1.55; margin-top: .6rem; }
        .map-origin {
            padding: 1rem; border-radius: 999px; text-align: center; background: #233d2d;
            color: white; max-width: 210px; margin: 0 auto 1.5rem; font-weight: 700;
        }
        .map-node {
            min-height: 125px; padding: 1rem; border-radius: 14px; background: white;
            border: 1px solid #d8ddd4; box-shadow: 0 5px 18px rgba(34,54,41,.05);
        }
        .map-node h4 { color: #42604b; margin: 0 0 .5rem; font-size: .85rem; text-transform: uppercase; letter-spacing: .06em; }
        .map-node p { margin: 0; line-height: 1.45; }
        .map-node.next-ready { border-color: #708c72; background: #eef3eb; }
        .map-item { display: block; margin: .3rem 0; }
        .map-item.new { color: #244b31; font-weight: 700; }
        .new-tag {
            display: inline-block; margin-left: .35rem; padding: .05rem .35rem;
            border-radius: 999px; background: #dbe9d8; color: #365b3e;
            font-size: .62rem; letter-spacing: .05em; text-transform: uppercase;
        }
        .assistant-turn {
            padding: 1rem 1.1rem; border-left: 3px solid #708c72;
            background: rgba(255,255,255,.58); border-radius: 0 12px 12px 0;
            margin: .55rem 0 1rem;
        }
        .assistant-turn p { margin: 0 0 .45rem; color: #4b5950; }
        .assistant-turn strong { font-family: Georgia, serif; font-size: 1.05rem; }
        .turn-label {
            display: block; margin-bottom: .2rem; color: #718078; font-size: .66rem;
            font-weight: 700; letter-spacing: .09em; text-transform: uppercase;
        }
        .question-block { margin-top: .8rem; }
        .participation-review {
            padding: 1rem 1.1rem; border: 1px solid #c8d5c5; border-radius: 12px;
            background: #eef3eb; margin: .75rem 0 1rem;
        }
        .participation-review h4 { margin: 0 0 .8rem; color: #304d38; }
        .participation-review p { margin: 0 0 .7rem; color: #4b5950; }
        .participation-review strong {
            display: block; color: #718078; font-size: .66rem;
            letter-spacing: .09em; text-transform: uppercase;
        }
        .participation-review .bridge { margin: .9rem 0 0; color: #17211b; }
        .release {
            text-align: center; padding: 3.2rem 1.4rem; border-radius: 24px;
            background: #e7eee4; border: 1px solid #c8d5c5;
        }
        .release h1 { font-family: Georgia, serif; font-size: 2.5rem; line-height: 1.15; }
        .release p { font-size: 1.2rem; color: #4c5d50; }
        div.stButton > button { border-radius: 999px; min-height: 2.8rem; }
        @media (max-width: 780px) {
            .block-container { padding-top: 1.25rem; padding-left: 1rem; padding-right: 1rem; }
            .hero { font-size: 2.55rem; }
            .hero-sub { font-size: 1.02rem; }
            .story-grid { grid-template-columns: 1fr; gap: .45rem; }
            .map-origin { margin-bottom: .75rem; padding: .7rem; }
            .map-node { min-height: auto; padding: .8rem; }
            .mode-card { min-height: auto; }
        }
        </style>
        """,
        unsafe_allow_html=True,
    )


def render_sidebar() -> None:
    with st.sidebar:
        st.markdown("### Relational AI")
        st.caption("A finite conversation that helps a human relationship develop.")
        current = SCREENS.index(st.session_state.screen)
        st.progress(current / (len(SCREENS) - 1))
        for index, screen in enumerate(SCREENS):
            marker = "●" if index == current else "○"
            st.write(f"{marker} {SCREEN_LABELS[screen]}")
        st.divider()
        mode_label = "Demo Mode" if st.session_state.mode == "demo" else "Relational Mode"
        st.caption(f"Current experience: {mode_label}")
        if os.getenv("RELATIONAL_AI_DEV") == "1":
            source = (
                "OpenAI Responses API"
                if st.session_state.generation_source == "live"
                else "Placeholder fallback"
            )
            st.caption(f"Response source: {source}")
        if os.getenv("RELATIONAL_AI_DEV") == "1" and st.session_state.screen != "landing":
            st.divider()
            st.caption("Development only")
        if (
            os.getenv("RELATIONAL_AI_DEV") == "1"
            and st.session_state.screen != "landing"
            and st.button("Reset session", use_container_width=True)
        ):
            reset_experience()
            st.rerun()


def conversation_input(messages: list[dict[str, str]] | None = None) -> list[dict[str, str]]:
    history = [{"role": "user", "content": st.session_state.situation}]
    history.extend(
        message for message in (messages or []) if message.get("role") in {"user", "assistant"}
    )
    return history


def live_or_placeholder(
    instructions: str,
    messages: list[dict[str, str]],
    fallback: str,
) -> str:
    try:
        response = generate_response(instructions, messages)
        st.session_state.generation_source = "live"
        st.session_state.generation_notice = ""
        return response
    except OpenAIConfigurationError:
        st.session_state.generation_source = "placeholder"
        st.session_state.generation_notice = (
            "Live generation is not configured. This response uses the Phase 1 placeholder."
        )
    except Exception as exc:  # The MVP remains demonstrable if the API is temporarily unavailable.
        st.session_state.generation_source = "placeholder"
        st.session_state.generation_notice = (
            f"Live generation was unavailable ({type(exc).__name__}). A placeholder is shown."
        )
    return fallback


def begin_experience(mode: str, situation: str) -> None:
    st.session_state.mode = mode
    st.session_state.situation = situation.strip() or DEMO_SCENARIO
    initial_input = conversation_input()
    if mode == "demo":
        st.session_state.conventional_response = live_or_placeholder(
            CONVENTIONAL_DEMO_INSTRUCTIONS,
            initial_input,
            conventional_demo_response(),
        )
    opening = run_relational_turn(
        situation=st.session_state.situation,
        messages=initial_input,
        participation=ParticipationState(),
        what_matters=None,
        next_participation_evidence=None,
        response_cycle=0,
        user_reply_count=0,
    )
    st.session_state.messages = [
        {
            "role": "assistant",
            "content": opening.message,
            "observation": opening.observation,
            "question": opening.question,
        }
    ]
    opening_participation = opening.participation
    if mode == "demo":
        opening_participation = ParticipationState(
            people=["My colleague"],
            new_contexts=["A recent change in how meetings feel"],
        )
    st.session_state.participation = opening_participation
    st.session_state.latest_additions = opening_participation
    st.session_state.what_matters = opening.what_matters
    st.session_state.next_participation_evidence = opening.next_participation_evidence
    st.session_state.ready_to_conclude = opening.ready_to_conclude
    st.session_state.generation_source = opening.generation_source
    st.session_state.generation_notice = opening.generation_notice
    st.session_state.review_opened = False
    st.session_state.response_count = 0
    st.session_state.screen = "conversation"


def render_landing() -> None:
    st.markdown('<div class="eyebrow landing-eyebrow">Relational AI</div>', unsafe_allow_html=True)
    st.markdown(
        '<div class="hero">Designed for the co-generation of human relationships.</div>',
        unsafe_allow_html=True,
    )
    st.markdown(
        """
        <div class="hero-sub">
        Relational AI helps people see the present, imagine new possibilities, and
        bring those possibilities into their next human conversation.
        </div>
        <div class="story-grid">
          <div class="story-card"><strong>See the present</strong><span>Notice the people, expectations, tensions, and possibilities already present in your relationships.</span></div>
          <div class="story-card"><strong>Imagine what will emerge</strong><span>through a renewed conversation.</span></div>
          <div class="story-card"><strong>Take one step forward</strong><span>Take one step forward toward new possibilities.</span></div>
        </div>
        """,
        unsafe_allow_html=True,
    )
    st.write("")
    st.write("")

    st.markdown("#### What would you like to make possible?")
    example = st.selectbox(
        "Start with an example",
        ("Write my own", *EXAMPLE_SITUATIONS),
        label_visibility="collapsed",
    )
    default = "" if example == "Write my own" else example
    situation = st.text_area(
        "Your situation",
        value=default,
        placeholder="A decision, relationship, concern, or question…",
        height=120,
    )

    primary, secondary, space = st.columns([1.35, 1, 2])
    with primary:
        if st.button("Begin a conversation", type="primary", use_container_width=True):
            with st.spinner("Opening a brief relational conversation…"):
                begin_experience("normal", situation)
            st.rerun()
    with secondary:
        if st.button("Open Demo Mode", use_container_width=True):
            with st.spinner("Generating two orientations to the same situation…"):
                begin_experience("demo", DEMO_SCENARIO)
            st.rerun()

    st.markdown(
        '<div class="quiet-note">This prototype is designed to reach a stopping point—not to maximize time in conversation.</div>',
        unsafe_allow_html=True,
    )


def render_demo_comparison() -> None:
    st.markdown('<div class="eyebrow">Demo Mode · One situation, two orientations</div>', unsafe_allow_html=True)
    st.markdown(f"> {st.session_state.situation}")
    conventional, relational = st.columns(2)
    with conventional:
        st.markdown(
            f"""
            <div class="mode-card">
              <div class="mode-label">Conventional AI</div>
              <div class="mode-copy">{escape(st.session_state.conventional_response)}</div>
            </div>
            """,
            unsafe_allow_html=True,
        )
    with relational:
        st.markdown(
            f"""
            <div class="mode-card relational">
              <div class="mode-label">Relational AI</div>
              <div class="mode-copy">{escape(st.session_state.messages[0]['content'])}</div>
            </div>
            """,
            unsafe_allow_html=True,
        )
    st.caption("One answers inside the chat. One opens participation beyond it.")


def participation_additions(
    previous: ParticipationState, current: ParticipationState
) -> ParticipationState:
    additions: dict[str, list[str]] = {}
    for name, values in current.as_dict().items():
        prior = {" ".join(item.casefold().split()) for item in getattr(previous, name)}
        additions[name] = [
            item for item in values if " ".join(item.casefold().split()) not in prior
        ]
    return ParticipationState(**additions)


def render_assistant_turn(message: dict[str, str | None]) -> None:
    observation = escape(str(message.get("observation") or message.get("content") or ""))
    question = message.get("question")
    question_html = (
        '<div class="question-block"><span class="turn-label">Question</span>'
        f"<strong>{escape(str(question))}</strong></div>"
        if question
        else ""
    )
    st.markdown(
        '<div class="assistant-turn"><span class="turn-label">Observation</span>'
        f"<p>{observation}</p>{question_html}</div>",
        unsafe_allow_html=True,
    )


def render_participation_review(review: ParticipationReview) -> None:
    st.markdown(
        f"""
        <div class="participation-review">
          <h4>PARTICIPATION REVIEW</h4>
          <p><strong>People</strong>{escape(review.people)}</p>
          <p><strong>Shift</strong>{escape(review.shift)}</p>
          <p><strong>Emerging possibility</strong>{escape(review.emerging_possibility)}</p>
          <p class="bridge"><strong>Reflection</strong>{escape(review.bridge_question)}</p>
        </div>
        """,
        unsafe_allow_html=True,
    )


def prepare_participation_card() -> None:
    participation = st.session_state.participation
    connected = [
        *participation.people,
        *participation.communities,
        *participation.responsibilities,
        *participation.new_contexts,
    ]
    st.session_state.card = {
        "what_matters": st.session_state.what_matters or "",
        "connected_to": ", ".join(connected),
        "next_participation": ", ".join(participation.next_participation),
        "when_or_where": "",
    }


def process_user_response(response: str) -> None:
    st.session_state.messages.append({"role": "user", "content": response})
    previous = st.session_state.participation
    with st.spinner("Updating the field…"):
        turn = run_relational_turn(
            situation=st.session_state.situation,
            messages=conversation_input(st.session_state.messages),
            participation=previous,
            what_matters=st.session_state.what_matters,
            next_participation_evidence=st.session_state.next_participation_evidence,
            response_cycle=st.session_state.response_count + 1,
            user_reply_count=st.session_state.response_count + 1,
        )
    st.session_state.messages.append(
        {
            "role": "assistant",
            "content": turn.message,
            "observation": turn.observation,
            "question": turn.question,
        }
    )
    st.session_state.latest_additions = participation_additions(previous, turn.participation)
    st.session_state.participation = turn.participation
    st.session_state.what_matters = turn.what_matters
    st.session_state.next_participation_evidence = turn.next_participation_evidence
    st.session_state.ready_to_conclude = turn.ready_to_conclude
    st.session_state.generation_source = turn.generation_source
    st.session_state.generation_notice = turn.generation_notice
    st.session_state.response_count += 1


def render_conversation() -> None:
    if st.session_state.mode == "demo":
        if st.session_state.response_count == 0:
            render_demo_comparison()
        else:
            with st.expander("Opening comparison"):
                render_demo_comparison()
    else:
        st.markdown('<div class="eyebrow">A brief relational conversation</div>', unsafe_allow_html=True)
        st.markdown(f"> {st.session_state.situation}")

    map_column, exchange_column = st.columns([1.7, 1], gap="large")
    with map_column:
        st.markdown('<div class="eyebrow">Participation taking shape</div>', unsafe_allow_html=True)
        render_participation_map(
            st.session_state.participation, st.session_state.latest_additions
        )

    with exchange_column:
        st.markdown('<div class="eyebrow">The exchange</div>', unsafe_allow_html=True)
        if os.getenv("RELATIONAL_AI_DEV") == "1" and st.session_state.generation_notice:
            st.warning(st.session_state.generation_notice)

        for message in st.session_state.messages:
            if message["role"] == "assistant":
                render_assistant_turn(message)
            elif message["role"] == "review":
                render_participation_review(ParticipationReview(**message["review"]))
            else:
                with st.chat_message("user"):
                    st.write(message["content"])

        if st.session_state.ready_to_conclude:
            st.success("A grounded participation is ready for your review.")

        ready = st.session_state.ready_to_conclude
        review_ready = participation_review_ready(
            st.session_state.participation, st.session_state.response_count
        )
        review_is_latest = bool(
            st.session_state.messages
            and st.session_state.messages[-1].get("role") == "review"
        )
        if st.button(
            "Review my participation",
            type="primary",
            disabled=not review_ready or review_is_latest,
            help="Available after the conversation has developed enough for a useful synthesis."
            if not review_ready
            else None,
            use_container_width=True,
        ):
            review = build_participation_review(
                messages=conversation_input(st.session_state.messages),
                participation=st.session_state.participation,
                what_matters=st.session_state.what_matters,
            )
            st.session_state.messages.append(
                {"role": "review", "review": review.__dict__}
            )
            st.session_state.review_opened = True
            st.rerun()

        if not review_ready:
            st.caption("Available after enough conversation for a useful synthesis.")

        if st.session_state.review_opened and ready:
            if st.button("Continue to participation card", use_container_width=True):
                prepare_participation_card()
                st.session_state.screen = "participation"
                st.rerun()

        if (
            st.session_state.mode == "demo"
            and not ready
            and st.session_state.response_count < 2
        ):
            st.divider()
            st.caption("Prepared Build Week journey")
            prepared_reply = (
                DEMO_REPLY_1 if st.session_state.response_count == 0 else DEMO_REPLY_2
            )
            if st.button(
                "Continue the demonstration",
                key=f"demo_continue_{st.session_state.response_count}",
                use_container_width=True,
            ):
                process_user_response(prepared_reply)
                st.rerun()

    if not st.session_state.ready_to_conclude or st.session_state.review_opened:
        response = st.chat_input("Respond in your own words")
        if response:
            process_user_response(response)
            st.rerun()


def render_map_node(
    title: str,
    values: list[str],
    empty_state: str,
    new_values: list[str] | None = None,
) -> None:
    new_keys = {" ".join(value.casefold().split()) for value in (new_values or [])}
    items = []
    for value in values:
        is_new = " ".join(value.casefold().split()) in new_keys
        marker = '<span class="new-tag">This turn</span>' if is_new else ""
        css_class = "map-item new" if is_new else "map-item"
        items.append(f'<span class="{css_class}">{escape(value)}{marker}</span>')
    content = (
        "".join(items)
        if items
        else f'<span class="map-item">{escape(empty_state)}</span>'
    )
    node_class = "map-node next-ready" if title == "Next participation" and values else "map-node"
    st.markdown(
        f'<div class="{node_class}"><h4>{title}</h4><p>{content}</p></div>',
        unsafe_allow_html=True,
    )


def render_participation_map(
    participation: ParticipationState, additions: ParticipationState | None = None
) -> None:
    additions = additions or ParticipationState()
    st.markdown(
        '<div class="map-origin">This conversation<br>a temporary orientation—not the destination</div>',
        unsafe_allow_html=True,
    )
    first_row = st.columns(3)
    with first_row[0]:
        render_map_node("People", participation.people, "No one named yet", additions.people)
    with first_row[1]:
        render_map_node(
            "Communities",
            participation.communities,
            "No community named yet",
            additions.communities,
        )
    with first_row[2]:
        render_map_node(
            "Responsibilities",
            participation.responsibilities,
            "Not yet surfaced",
            additions.responsibilities,
        )
    second_row = st.columns(2)
    with second_row[0]:
        render_map_node(
            "New contexts",
            participation.new_contexts,
            "No new context yet",
            additions.new_contexts,
        )
    with second_row[1]:
        render_map_node(
            "Next participation",
            participation.next_participation,
            "Waiting for your words",
            additions.next_participation,
        )


def render_participation() -> None:
    st.markdown('<div class="eyebrow">Participation beyond the conversation</div>', unsafe_allow_html=True)
    st.title("Your wider relational field is coming into view.")
    render_participation_map(st.session_state.participation)

    st.divider()
    st.subheader("Participation Card")
    st.caption("This is an editable handoff, not a prescription. Make the language yours.")
    if st.session_state.next_participation_evidence:
        st.caption(
            f'Grounded in your words: “{st.session_state.next_participation_evidence}”'
        )
    card = st.session_state.card
    with st.form("participation_card"):
        what_matters = st.text_area("What matters", value=card["what_matters"])
        connected_to = st.text_area("Who or what this connects to", value=card["connected_to"])
        next_participation = st.text_area("My next participation", value=card["next_participation"])
        when_or_where = st.text_input("When or where (optional)", value=card["when_or_where"])
        confirmed = st.form_submit_button("This participation is mine", type="primary")
    if confirmed:
        st.session_state.card = {
            "what_matters": what_matters,
            "connected_to": connected_to,
            "next_participation": next_participation,
            "when_or_where": when_or_where,
        }
        st.session_state.screen = "conclusion"
        st.rerun()


def render_conclusion() -> None:
    card = st.session_state.card
    st.markdown(
        f"""
        <div class="release">
          <div class="eyebrow">The conversation has done its part.</div>
          <h1>Your next step is with another person.</h1>
          <p><strong>{escape(card['next_participation'])}</strong></p>
          <p>Carry this intention into the relationship.</p>
        </div>
        """,
        unsafe_allow_html=True,
    )
    st.write("")
    st.subheader("Your Participation Card")
    st.markdown(
        f"""
        <dl>
          <dt><strong>What matters</strong></dt>
          <dd>{escape(card['what_matters'])}</dd>
          <dt><strong>Who this connects to</strong></dt>
          <dd>{escape(card['connected_to'])}</dd>
          <dt><strong>My next participation</strong></dt>
          <dd>{escape(card['next_participation'])}</dd>
          <dt><strong>When or where</strong></dt>
          <dd>{escape(card['when_or_where']) if card['when_or_where'] else 'Left open'}</dd>
        </dl>
        """
        ,
        unsafe_allow_html=True,
    )
    st.info(
        "Take this as participation you can revise in the world—not an instruction from the AI."
    )


def main() -> None:
    st.set_page_config(
        page_title="Relational AI",
        page_icon="↗",
        layout="wide",
        initial_sidebar_state="collapsed",
    )
    init_state()
    apply_styles()
    render_sidebar()

    screen = st.session_state.screen
    if screen == "landing":
        render_landing()
    elif screen == "conversation":
        render_conversation()
    elif screen == "participation":
        render_participation()
    else:
        render_conclusion()


if __name__ == "__main__":
    main()
