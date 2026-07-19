"""Streamlit interface for the Relational AI MVP.

Live responses use the OpenAI Responses API when configured. Deterministic Phase 1
content remains available as a transparent fallback.
"""

from __future__ import annotations

from copy import deepcopy
from html import escape

import streamlit as st

from implementation.openai_client import OpenAIConfigurationError, generate_response
from implementation.placeholder_experience import (
    DEFAULT_PARTICIPATION,
    DEMO_SCENARIO,
    EXAMPLE_SITUATIONS,
    conventional_demo_response,
    placeholder_relational_response,
    relational_opening,
)
from implementation.prompts import CONVENTIONAL_DEMO_INSTRUCTIONS, RELATIONAL_INSTRUCTIONS


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
        "participation": deepcopy(DEFAULT_PARTICIPATION),
        "conventional_response": "",
        "generation_source": "placeholder",
        "generation_notice": "",
        "card": {
            "what_matters": "Choosing growth without losing sight of the people and commitments I care for.",
            "connected_to": "My partner, the future team, and my current responsibilities.",
            "next_participation": "Speak with my partner and ask the hiring manager two questions about the team's expectations.",
            "when_or_where": "Before the decision deadline on Friday.",
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
        "conventional_response",
        "generation_source",
        "generation_notice",
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
        .hero {
            font-family: Georgia, serif; font-size: clamp(2.3rem, 6vw, 4.8rem);
            line-height: 1.02; letter-spacing: -.035em; max-width: 900px;
            margin: 0 0 1.2rem;
        }
        .hero-sub { font-size: 1.18rem; line-height: 1.65; max-width: 690px; color: #4b5950; }
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
        .release {
            text-align: center; padding: 3.2rem 1.4rem; border-radius: 24px;
            background: #e7eee4; border: 1px solid #c8d5c5;
        }
        .release h1 { font-family: Georgia, serif; font-size: 2.5rem; line-height: 1.15; }
        .release p { font-size: 1.2rem; color: #4c5d50; }
        div.stButton > button { border-radius: 999px; min-height: 2.8rem; }
        </style>
        """,
        unsafe_allow_html=True,
    )


def render_sidebar() -> None:
    with st.sidebar:
        st.markdown("### Relational AI")
        st.caption("A finite conversation that opens toward the world.")
        current = SCREENS.index(st.session_state.screen)
        st.progress(current / (len(SCREENS) - 1))
        for index, screen in enumerate(SCREENS):
            marker = "●" if index == current else "○"
            st.write(f"{marker} {SCREEN_LABELS[screen]}")
        st.divider()
        mode_label = "Demo Mode" if st.session_state.mode == "demo" else "Relational Mode"
        st.caption(f"Current experience: {mode_label}")
        source = (
            "OpenAI Responses API"
            if st.session_state.generation_source == "live"
            else "Placeholder fallback"
        )
        st.caption(f"Response source: {source}")
        if st.session_state.screen != "landing" and st.button("Start over", use_container_width=True):
            reset_experience()
            st.rerun()


def conversation_input(messages: list[dict[str, str]] | None = None) -> list[dict[str, str]]:
    history = [{"role": "user", "content": st.session_state.situation}]
    history.extend(messages or [])
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
    opening = live_or_placeholder(
        RELATIONAL_INSTRUCTIONS,
        initial_input,
        relational_opening(st.session_state.situation),
    )
    st.session_state.messages = [
        {"role": "assistant", "content": opening}
    ]
    if mode == "demo":
        st.session_state.conventional_response = live_or_placeholder(
            CONVENTIONAL_DEMO_INSTRUCTIONS,
            initial_input,
            conventional_demo_response(),
        )
    st.session_state.response_count = 0
    st.session_state.screen = "conversation"


def render_landing() -> None:
    st.markdown('<div class="eyebrow">Relational AI</div>', unsafe_allow_html=True)
    st.markdown(
        '<div class="hero">The purpose of this AI is not to keep you here.</div>',
        unsafe_allow_html=True,
    )
    st.markdown(
        """
        <div class="hero-sub">
        It is to help you participate more fully in the world beyond this conversation.
        Bring a situation you are considering. We will explore it briefly, notice what it
        connects you to, and stop when the next part belongs in your world.
        </div>
        """,
        unsafe_allow_html=True,
    )
    st.write("")
    st.write("")

    st.markdown("#### What would you like to consider?")
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
    st.caption("The comparison ends here. The experience continues only along the relational path.")
    st.divider()


def render_conversation() -> None:
    if st.session_state.mode == "demo":
        render_demo_comparison()
    else:
        st.markdown('<div class="eyebrow">A brief relational conversation</div>', unsafe_allow_html=True)
        st.title("Let’s notice what this opens toward.")
        st.markdown(f"> {st.session_state.situation}")

    st.markdown(
        '<div class="quiet-note">This conversation will pause when a meaningful next participation has emerged.</div>',
        unsafe_allow_html=True,
    )
    if st.session_state.generation_notice:
        st.warning(st.session_state.generation_notice)

    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.write(message["content"])

    if st.session_state.response_count < 2:
        response = st.chat_input("Respond in your own words")
        if response:
            st.session_state.messages.append({"role": "user", "content": response})
            with st.spinner("Noticing what this connects to…"):
                reply = live_or_placeholder(
                    RELATIONAL_INSTRUCTIONS,
                    conversation_input(st.session_state.messages),
                    placeholder_relational_response(st.session_state.response_count),
                )
            st.session_state.messages.append({"role": "assistant", "content": reply})
            st.session_state.response_count += 1
            st.rerun()
    else:
        st.success("There is enough here to see how participation might extend beyond this chat.")

    ready = st.session_state.response_count >= 1
    if st.button(
        "See the participation taking shape",
        type="primary",
        disabled=not ready,
        help="Respond once to make the placeholder participation view available." if not ready else None,
    ):
        st.session_state.screen = "participation"
        st.rerun()


def render_map_node(title: str, values: list[str]) -> None:
    content = "<br>".join(values) if values else "Still open"
    st.markdown(
        f'<div class="map-node"><h4>{title}</h4><p>{content}</p></div>',
        unsafe_allow_html=True,
    )


def render_participation() -> None:
    st.markdown('<div class="eyebrow">Participation beyond the conversation</div>', unsafe_allow_html=True)
    st.title("Your wider relational field is coming into view.")
    st.write(
        "The conversation is not the destination. These are the people, contexts, and forms of participation it has helped bring forward."
    )
    st.markdown('<div class="map-origin">AI conversation<br>temporary point of orientation</div>', unsafe_allow_html=True)

    participation = st.session_state.participation
    first_row = st.columns(3)
    with first_row[0]:
        render_map_node("People involved", participation["people"])
    with first_row[1]:
        render_map_node("Communities", participation["communities"])
    with first_row[2]:
        render_map_node("Responsibilities", participation["responsibilities"])
    second_row = st.columns([1, 1, 0.5])
    with second_row[0]:
        render_map_node("New contexts", participation["new_contexts"])
    with second_row[1]:
        render_map_node("Next participation", participation["next_participation"])

    st.divider()
    st.subheader("Participation Card")
    st.caption("This is an editable handoff, not a prescription. Make the language yours.")
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
    st.markdown(
        """
        <div class="release">
          <div class="eyebrow">A good stopping point</div>
          <h1>I think we've reached a good stopping point.</h1>
          <p>The next part belongs in your world.</p>
        </div>
        """,
        unsafe_allow_html=True,
    )
    st.write("")
    st.subheader("Your Participation Card")
    card = st.session_state.card
    st.markdown(
        f"""
        <dl>
          <dt><strong>What matters</strong></dt>
          <dd>{card['what_matters']}</dd>
          <dt><strong>Who or what this connects to</strong></dt>
          <dd>{card['connected_to']}</dd>
          <dt><strong>My next participation</strong></dt>
          <dd>{card['next_participation']}</dd>
          <dt><strong>When or where</strong></dt>
          <dd>{card['when_or_where'] or 'Left open'}</dd>
        </dl>
        """
        ,
        unsafe_allow_html=True,
    )
    st.info("The conversation is now complete. No further response is needed here.")
    if st.button("Start a new conversation"):
        reset_experience()
        st.rerun()


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
