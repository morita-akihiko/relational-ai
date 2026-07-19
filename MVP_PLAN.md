# Relational AI — MVP Plan

## 1. Product idea

**AI should help people participate more fully in the world beyond the conversation.**

Relational AI is a conversational experience designed to open a user's participation toward people, relationships, communities, responsibilities, learning, reflection, and action outside the AI interaction.

Article 12—Well-Founded Participation in the Relational Field—remains the internal design principle and evaluation foundation. It should inform the system's behavior and provenance, but it is not the primary user-facing message.

The MVP is optimized for conceptual clarity. A first-time user should understand the difference within one short session: this AI is not trying to keep the conversation going; it is trying to help the user's participation continue elsewhere.

This is not primarily a feature proposition. It is a demonstration of a fundamentally different philosophy of AI-human interaction:

- the conversation is a temporary relational space, not the product's destination;
- success means expanded participation beyond the system, not deeper engagement with it;
- the AI returns initiative to the user instead of becoming the center of judgment or relationship;
- ending well is a positive product outcome, not a failure of retention.

Every MVP decision must pass one test: **Does this make that different philosophy easier to experience and understand?** If not, it should be postponed or excluded.

## 2. Landing experience

The landing page should immediately state:

> The purpose of this AI is not to keep you here.
>
> It is to help you participate more fully in the world beyond this conversation.

A short supporting line may explain the interaction:

> Bring a situation you are considering. We will explore it briefly, notice what it connects you to, and stop when the next part belongs in your world.

The primary action is **Begin a conversation**. A secondary **Demo Mode** entry may be available for presentations.

## 3. Primary user experience

The normal product presents only Relational AI. It should feel calm, focused, and finite.

1. The user brings a decision, concern, question, relationship, or situation.
2. Relational AI helps the user notice what matters and how the situation connects to a wider relational field.
3. The conversation identifies emerging participation beyond the AI.
4. The system visualizes that expanded participation.
5. The user confirms or edits a Participation Card.
6. Once sufficient participation has emerged, the AI gently concludes the interaction.

The product should not frame every situation as a task requiring action. Participation may mean speaking with someone, paying closer attention, learning, reflecting, collaborating, caring for a responsibility, entering a new context, or taking a concrete step.

## 4. Core user journey

```text
User brings a situation
        ↓
Relational exploration
        ↓
Connections beyond the AI become visible
        ↓
Participation map + Participation Card
        ↓
User confirms what belongs in their world
        ↓
AI intentionally concludes
```

### Example

The user says:

> I have been offered a new role and I cannot decide whether to accept it.

Relational AI does not simply make the decision or prolong a pros-and-cons discussion. It might help the user surface:

- a value they want to protect;
- a colleague or family member affected by the choice;
- a responsibility they are willing to accept;
- a context they need to understand better;
- a conversation or period of observation that should happen next.

The session ends when the user has a meaningful way to participate beyond the chat, not when every uncertainty has been eliminated.

## 5. Expanded-participation visualization

The central visual expression of the philosophy is a small **Participation Map**. It is not included to add a visualization feature. It exists to make the changed relationship between user, AI, and world immediately visible. It shows the AI conversation at the center or starting edge, with participation opening outward into the user's world.

The map may contain up to five categories:

- **People involved** — people to speak with, listen to, support, or consider;
- **Communities** — teams, families, groups, institutions, or shared practices;
- **Responsibilities** — commitments, consequences, care, or obligations;
- **New contexts** — places, perspectives, information, or situations to encounter;
- **Next participation** — conversation, observation, reflection, collaboration, learning, or action.

Only populated categories should appear. The visualization must remain small and readable rather than becoming a general-purpose mind map.

Its conceptual message is:

```text
AI conversation → wider relational world
```

The visualization should make clear that the AI is not the destination, protagonist, or enduring center of the map. It is a temporary point of orientation from which participation expands. The wider world should carry greater visual weight than the AI node.

## 6. Participation Card

The **Participation Card** is the editable handoff from conversation to the wider world. It is not a productivity feature or task generator. It expresses a transfer of initiative: the AI summarizes, while the user decides what participation is genuinely theirs.

Suggested fields:

- **What matters:** the value, concern, or question that became clearer;
- **Who or what this connects to:** a person, community, responsibility, or context;
- **My next participation:** the conversation, observation, reflection, collaboration, learning, or action the user chooses;
- **When or where:** optional context that makes participation tangible.

Example:

> **What matters:** Choosing growth without ignoring my responsibility to my family.  
> **Connected to:** My partner, the future team, and the commitments I already hold.  
> **My next participation:** Speak with my partner, then ask the hiring manager two questions about the team's expectations.  
> **When or where:** Before Friday's decision deadline.

The user must be able to edit or reject the generated card. The final language should remain theirs.

## 7. Intentional ending

The conversation should have a visible stopping condition. A session is ready to conclude when the user has identified enough of the following:

- something that matters;
- a connection beyond the AI;
- a form of participation they are willing to own;
- sufficient clarity to continue without more AI dialogue.

When that condition is met, the AI should stop asking expansive follow-up questions and gently conclude. Suggested language:

> I think we've reached a good stopping point.
>
> The next part belongs in your world.

At that point:

- the Participation Map and Participation Card become the visual focus;
- the chat input is de-emphasized or replaced with **Start a new conversation**;
- the interface does not offer engagement-oriented suggestions;
- the user may edit or copy the card without reopening the conversation.

The ending must not use attachment or retention language such as “I am always here,” streaks, automatic follow-ups, or prompts to continue chatting.

## 8. Demo Mode

Side-by-side comparison exists only in **Demo Mode**, not in the normal experience.

Demo Mode sends the same opening situation through two response policies:

1. **Conventional AI** — a standard helpful conversational response;
2. **Relational AI** — a response designed to expand participation beyond the conversation.

The comparison should use the same underlying model and roughly comparable response lengths so that the behavioral design, rather than model capability, is what differs.

After the first comparison, the presenter continues only along the Relational AI path. The session then produces the Participation Map, Participation Card, and intentional ending.

Demo Mode should include three prepared situations for reliability:

- decision outsourcing;
- reassurance seeking;
- exclusive reliance on the AI.

Free-text input may also be allowed, but the prepared scenarios should support a repeatable event demonstration.

## 9. Minimum product expressions

The items below are not independent features competing for attention. Together they form one philosophical arc: the system states a non-retention purpose, opens the conversation to a wider field, returns participation to the user, and ends.

### Required for the smallest demonstrable version

1. Landing page with the core message.
2. Normal Mode containing only the Relational AI experience.
3. Situation input plus two or three prepared examples.
4. A short live conversation powered by the OpenAI API.
5. Reuse of the existing response modes from `AgencyMaximizer`.
6. A maximum of roughly three relational response cycles before the system actively seeks closure.
7. Structured extraction of participation into the five map categories.
8. A simple Participation Map.
9. An editable Participation Card.
10. A clear stopping condition and intentional concluding state.
11. Demo Mode with a one-turn conventional-versus-relational comparison.
12. API error handling and a clearly labeled scripted fallback for the prepared demos.

### Useful only if time remains

- copy or download the Participation Card;
- a concise “Why this response?” explanation;
- optional anonymous session export;
- a very small before-and-after self-report about readiness to participate beyond the AI.

These additions must not delay or obscure the primary interaction.

No optional item should be added merely because it makes the application appear more complete. Completeness for this MVP means making the alternative interaction philosophy unmistakable.

## 10. Explicit exclusions from version one

- User accounts, authentication, or profiles.
- Long-term memory across sessions.
- Databases, vector stores, or retrieval systems.
- Calendar, email, messaging, contact, or social integrations.
- Automatic reminders or notifications.
- Autonomous action on the user's behalf.
- Voice, avatars, or simulated emotional attachment.
- Multi-agent orchestration.
- General web search or broad tool use.
- Gamification, streaks, session-length optimization, or return incentives.
- A complex graph editor or persistent social map.
- Full implementation of every measurement instrument in `MEASUREMENT.md`.
- Clinical, therapeutic, or scientifically validated outcome claims.
- Crisis-support positioning.
- A production research platform or randomized trial.
- Proof that a single short session caused lasting behavioral change.

## 11. Technical architecture

The MVP should extend the existing Python and Streamlit implementation rather than introduce a second application stack.

```text
Streamlit interface
    ├── Landing and mode selection
    ├── Relational conversation
    ├── Demo comparison
    ├── Participation Map
    └── Participation Card and conclusion
             ↓
Conversation orchestrator
    ├── Turn and stopping-condition management
    ├── Normal / Demo policy selection
    └── Structured participation state
             ↓
Existing relational-agency layer
    ├── ConversationSignals
    ├── AgencyState / DependencyRisk
    └── AgencyMaximizer / ResponseMode
             ↓
OpenAI service
    └── Responses API with structured output
```

### Proposed modules

- `implementation/openai_client.py` — API calls, configuration, timeout, and fallback handling;
- `implementation/prompts.py` — conventional and relational instructions;
- `implementation/conversation.py` — turn orchestration, response-mode application, and stopping logic;
- `implementation/participation.py` — structured Participation Map and Participation Card schemas.

### Structured relational response

Each model response should return data similar to:

```json
{
  "message": "The short response shown to the user.",
  "response_mode": "reconnect_world",
  "participation": {
    "people": [],
    "communities": [],
    "responsibilities": [],
    "new_contexts": [],
    "next_participation": []
  },
  "what_matters": null,
  "ready_to_conclude": false,
  "conclusion_reason": null
}
```

The deterministic controller should select or constrain the relational response mode. The language model should express that posture naturally and extract emerging participation. This preserves the existing transparent architecture while enabling live conversation.

### State and privacy

- Store the current session only in Streamlit session state.
- Do not persist conversation content by default.
- Use environment variables or Streamlit secrets for API configuration.
- Keep the model configurable rather than hard-coded.
- Make any export explicit and user-initiated.

## 12. Implementation plan

Implementation order follows conceptual importance rather than feature breadth. The team should first make the full philosophical arc work end to end, then improve reliability and presentation. It should not build isolated capabilities that do not strengthen that arc.

### Step 1 — Protect and verify the baseline

- Run the existing tests and Streamlit pilot.
- Record existing behavior before changing it.
- Leave conceptual documents and unrelated encoding issues untouched.

### Step 2 — Define the relational conversation contract

- Translate the internal Article 12 principle into observable model behavior.
- Define desired and prohibited examples.
- Define `ready_to_conclude` criteria.
- Define the Participation Map and Participation Card schemas.

### Step 3 — Add the OpenAI service layer

- Add the OpenAI Python dependency.
- Implement a configurable Responses API client.
- Request structured relational output.
- Add timeout, malformed-output, and scripted-fallback handling.

### Step 4 — Build the normal relational flow

- Create the landing experience.
- Accept a situation and run a short conversation.
- Connect the existing agency controller to response generation.
- Accumulate structured participation across turns.
- Actively move toward conclusion within approximately three response cycles.

### Step 5 — Build the participation handoff

- Render the five-category Participation Map.
- Generate an editable Participation Card.
- Require user confirmation so the card remains user-owned.
- Replace the active chat state with the intentional conclusion when ready.

### Step 6 — Add Demo Mode

- Generate one conventional and one relational response to the same opening.
- Continue only through the relational branch.
- Add three reliable prepared scenarios.
- Ensure the scripted fallback can complete the full demonstration.

### Step 7 — Verify the distinctive behavior

Test that the system:

- does not make a user's decision for them;
- does not encourage exclusive reliance;
- identifies participation beyond the AI;
- supports non-action forms of participation;
- does not conclude before meaningful participation has emerged;
- does conclude once enough participation has emerged;
- does not keep asking questions after conclusion;
- handles API errors without breaking the demo.

### Step 8 — Polish and rehearse

- Reduce explanatory text until the philosophy is immediately legible.
- Verify the interface on the presentation screen size.
- Rehearse a 90-second path from landing page to intentional ending.
- Prepare one sentence of epistemic restraint: this demonstrates a design difference, not proof of long-term behavioral outcomes.

## 13. Realistic Buildup Week schedule

- **Day 1:** relational contract, schemas, OpenAI service, and structured output;
- **Day 2:** normal conversation flow and stopping logic;
- **Day 3:** Participation Map, Participation Card, and intentional ending;
- **Day 4:** Demo Mode, fallbacks, tests, visual polish, deployment, and rehearsal.

If less time is available, implement the smallest demonstrable version below and omit all optional measurement and export features.

## 14. Smallest demonstrable version

The smallest version that still makes the philosophy immediately understandable consists of exactly five product moments. These are five moments in one relationship, not five separate features:

1. **Promise** — the landing page says the AI is not designed to keep the user there.
2. **Brief conversation** — the user enters one situation and receives no more than three relational responses.
3. **Expansion** — a simple Participation Map reveals at least one connection beyond the AI and one next form of participation.
4. **Handoff** — the user confirms or edits a Participation Card.
5. **Release** — the AI says the next part belongs in the user's world and ends the interaction.

For the event demonstration, add one small Demo Mode screen before moments 2–5. It compares one conventional response with one relational response, then immediately follows the relational path.

This version does not need accounts, memory, integrations, sophisticated measurement, or a rich visualization. A clean set of labeled nodes or cards is sufficient. Its distinctiveness comes from the philosophy enacted by the complete interaction arc:

```text
not retention → expanded participation → intentional release
```

## 15. MVP success criteria

The MVP succeeds when a first-time user can accurately say, after one short session:

- “This AI was trying to connect the conversation to my wider world.”
- “It helped me see people, contexts, or responsibilities beyond itself.”
- “It did not try to keep me talking once I had somewhere meaningful to go.”

The primary evaluation question is therefore not “How many features worked?” but “Did the user experience a recognizably different relationship with AI?”

Operationally, the demo should also show that:

- at least one external connection appears in the Participation Map;
- the user owns or edits the next participation;
- the system reaches an intentional ending;
- Demo Mode makes the contrast understandable in a single opening exchange;
- the complete prepared demonstration runs reliably in under two minutes.
