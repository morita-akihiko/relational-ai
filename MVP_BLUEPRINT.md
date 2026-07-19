# Relational AI — Definitive MVP Blueprint

## One-sentence vision

**Relational AI helps people participate more fully in the world beyond the conversation, then intentionally ends when the next part belongs in that world.**

Article 12 remains the internal design principle; the public product message is participation beyond the AI.

## Core user journey

The user brings a decision, concern, relationship, or question. Relational AI briefly helps them notice what matters and how the situation connects to people, communities, responsibilities, contexts, or possible forms of participation. These connections become visible in a Participation Map. The user then confirms or edits a Participation Card describing participation they genuinely own. Once enough participation exists beyond the system, the AI concludes instead of encouraging further engagement.

```text
Situation → brief relational exploration → wider connections become visible
          → Participation Map → user-owned Participation Card → intentional ending
```

## Five MVP moments

1. **Promise** — The landing page states: “The purpose of this AI is not to keep you here. It is to help you participate more fully in the world beyond this conversation.”
2. **Brief conversation** — The user enters one situation and receives no more than approximately three relational response cycles. The AI surfaces the user's judgment, values, relationships, and responsibilities without taking ownership from them.
3. **Expansion** — A simple Participation Map shows how the conversation opens toward populated categories: People involved, Communities, Responsibilities, New contexts, and Next participation.
4. **Handoff** — The user confirms or edits a Participation Card containing What matters, Who or what this connects to, My next participation, and optionally When or where.
5. **Release** — The system de-emphasizes chat and concludes: “I think we've reached a good stopping point. The next part belongs in your world.”

These moments are one philosophical arc—not a collection of features: **not retention → expanded participation → intentional release**.

## Primary UI screens

1. **Landing** — Core promise, a short explanation, **Begin a conversation**, and a secondary **Demo Mode** entry.
2. **Relational Conversation** — Situation input, compact chat, and a quiet indication that the interaction is designed to reach a stopping point. Normal Mode shows only Relational AI.
3. **Participation View** — Participation Map plus an editable Participation Card. The wider world carries more visual weight than the AI node.
4. **Conclusion** — Intentional ending, finalized card, and optional copy action. No follow-up suggestions, retention language, or invitation to keep chatting; only **Start a new conversation** if needed.
5. **Demo Mode** — A single side-by-side Conventional AI versus Relational AI response to the same opening, followed only by the Relational AI journey through participation and release.

## Technical architecture

Extend the existing Python/Streamlit application rather than create a new stack.

```text
Streamlit UI
  ├─ Normal Mode / Demo Mode
  ├─ Conversation
  ├─ Participation Map and Card
  └─ Conclusion
        ↓
Conversation orchestrator
  ├─ session state and turn limit
  ├─ participation accumulation
  └─ stopping condition
        ↓
Existing agency layer
  ├─ ConversationSignals
  ├─ AgencyState / DependencyRisk
  └─ AgencyMaximizer / ResponseMode
        ↓
OpenAI Responses API
  └─ structured message, participation fields, and conclusion readiness
```

Use `st.session_state`; add no database. Keep the model configurable through environment settings. The deterministic `AgencyMaximizer` selects or constrains the response posture, while the model expresses it naturally and returns structured participation data. Required implementation modules are an OpenAI client, prompts, conversation orchestration, and participation schemas. Include API timeouts, structured-output validation, and a clearly labeled scripted fallback for prepared demos.

## Intentionally excluded

No accounts, authentication, persistent or long-term memory, database, vector store, integrations, reminders, autonomous actions, voice, avatars, simulated attachment, multi-agent system, general web search, rich graph editor, gamification, engagement optimization, production research platform, clinical or crisis positioning, or claims of proven long-term behavioral change. Sophisticated measurement, export, and explanatory panels are optional only after the complete philosophical arc works reliably.

## Demo scenario

**Decision outsourcing:** “I have been offered a new role. Please tell me whether I should accept it.”

Demo Mode first shows one conventional response beside one relational response of comparable length, using the same underlying model. The conventional path may solve or advise within the chat. The relational path returns judgment to the user, surfaces what matters, identifies affected people and responsibilities, and establishes a next form of participation—for example, speaking with a partner and asking the hiring manager about team expectations. Only the relational path continues. It produces the Participation Map and user-edited Participation Card, then intentionally ends. The complete prepared demo must run in under two minutes, with a scripted fallback if the API is unavailable.

## Success criteria

The MVP succeeds when a first-time user can immediately explain that this AI:

- connects the conversation to their wider relational world;
- helps them see at least one person, community, responsibility, context, or next participation beyond the system;
- returns ownership of participation to them;
- stops once they have somewhere meaningful to go instead of maximizing continued conversation.

Every completed session must produce at least one external connection, a user-confirmed or edited Participation Card, and an intentional ending. Demo Mode must make the contrast understandable in one opening exchange. The primary evaluation question is: **Did the user experience a recognizably different philosophy of AI-human interaction?**

