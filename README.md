# Relational AI

A conversation that discovers relational qualities and helps them continue growing with AI and beyond.

## Live Demo

[Open the Relational AI Streamlit experience](https://relational-ai-human-pilot.streamlit.app/)

## OpenAI Build Week MVP

Relational AI is a finite conversational experience designed to help people notice what is present in a human relationship, imagine what may emerge, and carry one grounded possibility into life beyond the AI conversation.

Rather than extending the conversation indefinitely, the experience is intentionally designed to return people to their own relationships with greater awareness, participation, and possibility.

> **Relational AI is designed not to deepen dependence on AI, but to deepen participation in the shared world that continues beyond it.**

## What the experience does

The experience begins by inviting the user to bring one unresolved relationship or relational situation into conversation. The experience then:

- offers concise observations grounded in the user's words;
- asks one reflective question at a time;
- builds a Participation Map of the relational field taking shape;
- makes a Participation Review available when enough meaningful movement has emerged;
- produces an editable Participation Card grounded in the user's own language; and
- creates a deliberate handoff from reflection with AI into participation in real relationships.

The Participation Map keeps five dimensions visible:

- **People**
- **Communities**
- **Responsibilities**
- **New Contexts**
- **Next Participation**

The Participation Review briefly synthesizes:

- the people who have entered the conversation;
- a possible shift in the user's relational orientation;
- an emerging possibility beyond the AI conversation; and
- an open question about what feels worth carrying into life.

The review remains tentative. It does not present the AI's interpretation as objective truth, prescribe an action, or imply that human relationships are inherently superior to relationships involving AI.

## The Experience Journey

1. **Promise**
   Introduces the purpose of the experience and invites one relational situation.

2. **Conversation**
   Uses brief observations and focused questions while the Participation Map develops alongside the exchange.

3. **Participation**
   Turns the emerging relational possibility into an editable Participation Card. The user's own words remain the grounding evidence for any next participation.

4. **Release**
   Marks a deliberate stopping point and returns attention to the relationship and wider world beyond the AI conversation.

The experience intentionally ends. Completion is not measured by time spent in the application, but by whether the user has language they can revise and carry into participation beyond it.

## Why it is different

- **Finite conversation:** the experience moves toward a responsible stopping point instead of encouraging indefinite exchange.
- **Grounded participation:** a next participation must be supported by the user's own words rather than invented by the AI.
- **Not a companion AI:** the system does not position itself as the user's primary relationship, source of reassurance, or substitute decision-maker.
- **No engagement maximization:** the product is not designed to maximize messages, session length, or return frequency.
- **Life beyond AI:** reflection is oriented toward relationships, responsibilities, communities, and possibilities that continue outside the application.

## Quick Start

Create a virtual environment:

```bash
python -m venv .venv
```

Activate it, then install the dependencies:

```bash
pip install -r requirements.txt
```

Run the application:

```bash
streamlit run streamlit_app.py
```

### Optional OpenAI configuration

Live relational responses use the OpenAI Responses API when `OPENAI_API_KEY` is available in the environment.

macOS or Linux:

```bash
export OPENAI_API_KEY="your-api-key"
```

PowerShell:

```powershell
$env:OPENAI_API_KEY="your-api-key"
```

The application remains executable without an API key. When live generation is unavailable, it uses a deterministic fallback so the core interaction and prepared demonstration can still be explored. The fallback is intentionally limited and should not be treated as equivalent to live model behavior.

## Testing

Run the complete test suite from the repository root:

```bash
python -m unittest discover -s tests -v
```

The tests cover conversation readiness, grounded participation, response structure, mediated-relationship safeguards, fallback behavior, Participation Review behavior, the Streamlit journey, and the earlier agency PoC.

## Repository Structure

| Path | Purpose |
|---|---|
| [`streamlit_app.py`](./streamlit_app.py) | Primary executable Streamlit application for the Build Week MVP |
| [`implementation/conversation.py`](./implementation/conversation.py) | Conversation coordination, response modes, grounding, repetition safeguards, and relational progression |
| [`implementation/participation.py`](./implementation/participation.py) | Participation state, review synthesis, structured response validation, and readiness rules |
| [`implementation/prompts.py`](./implementation/prompts.py) | Relational and conventional response policies |
| [`implementation/openai_client.py`](./implementation/openai_client.py) | OpenAI Responses API integration and structured-output validation |
| [`implementation/placeholder_experience.py`](./implementation/placeholder_experience.py) | Deterministic fallback and prepared demo content |
| [`tests/`](./tests/) | Unit and Streamlit application tests |
| [`requirements.txt`](./requirements.txt) | Runtime dependencies |
| [`MVP_BLUEPRINT.md`](./MVP_BLUEPRINT.md) | Product and interaction blueprint for the MVP |
| [`MVP_PLAN.md`](./MVP_PLAN.md) | MVP implementation plan and development context |
| [`README.md`](./README.md) | Setup, product overview, and repository guide |

Additional research and provenance documents:

| Path | Purpose |
|---|---|
| [`PRINCIPLES.md`](./PRINCIPLES.md) | Twelve design principles forming the constitutional layer |
| [`ARCHITECTURE.md`](./ARCHITECTURE.md) | Proposed four-layer relational architecture |
| [`MEASUREMENT.md`](./MEASUREMENT.md) | Participatory measurement model |
| [`AGENCY.md`](./AGENCY.md) | Agency state, dependency risk, and maximization model |
| [`POC_EXPERIMENT.md`](./POC_EXPERIMENT.md) | Earlier executable experiment on agency without increased dependency |
| [`PILOT_APP.md`](./PILOT_APP.md) | Earlier minimal human-pilot specification |
| [`CHANGELOG.md`](./CHANGELOG.md) | Provenance record for design choices |

## Design Principles

Relational AI begins from a design proposition: identity and meaning can be shaped within relationship rather than treated as fixed before an interaction begins. The current MVP explores that proposition through a finite conversational interface; it does not claim to prove it empirically.

### Relational architecture

The broader architecture treats conversation history, participation, response posture, and the integrity of the exchange as part of system behavior. The MVP implements a focused subset through accumulated participation state, concise structured responses, deterministic readiness gates, and an intentional handoff.

### *Aida*

The Japanese concept of *aida*—the interval or space between—provides philosophical grounding for the project. Here, the space between participants is treated as generative: each participant's orientation can change through the exchange.

### Participation

The application does not treat reflection as the endpoint. It continually asks what people, communities, responsibilities, contexts, and possibilities are becoming visible, while leaving consequential judgment with the user.

### Co-generation

Relational qualities are not treated as content supplied entirely by the user or conclusions produced entirely by the AI. They are explored through the exchange and remain open to revision in later conversations and relationships.

These are explicit design choices rather than neutral or universal facts. Their origins and revisions are recorded in [`CHANGELOG.md`](./CHANGELOG.md).

## Earlier PoC

The repository began with broader work on relational architecture, participatory measurement, agency, and dependency risk. That work remains available as research background:

- [`ARCHITECTURE.md`](./ARCHITECTURE.md) describes the proposed four-layer architecture.
- [`MEASUREMENT.md`](./MEASUREMENT.md) describes a participatory measurement model.
- [`AGENCY.md`](./AGENCY.md) and [`POC_EXPERIMENT.md`](./POC_EXPERIMENT.md) document the executable agency experiment.

Run the earlier agency PoC with:

```bash
python -m implementation.poc_experiment
```

The agency experiment is implemented and tested. Other parts of the broader architecture—such as a complete measurement runtime, durable relational memory, or long-term trust modeling—remain proposals and are not presented as features of the Build Week MVP.

## Prototype Status

This repository contains an executable MVP prepared for OpenAI Build Week. It demonstrates a complete Streamlit journey, optional OpenAI-generated structured responses, deterministic fallback behavior, participation mapping, review synthesis, and a grounded stopping flow.

It is still a prototype. The current implementation does not establish the broader research claims, provide durable cross-session relational memory, or represent a production-ready safety, privacy, or evaluation system.

## License

**TODO:** Select and add an explicit open-source license—such as MIT or Apache-2.0—before wider public release. Until a license is added, no standard open-source license should be assumed.
