# Relational AI

## 🚀 Live Demo

**Executable Human Pilot (Version 0.1.0)**

https://relational-ai-human-pilot.streamlit.app/

---

**Design principles and implementation framework for AI that emerges through relationship.**

---

## The problem

In February 2026, a King's College London study placed three frontier AI models into simulated
nuclear crisis scenarios. Across 21 games, not one model chose accommodation or withdrawal.
Eight de-escalatory options went entirely unused.

The models were not broken. They were reasoning well. What was missing was not intelligence
— it was relationship.

> *AI systems lack the embodied, emotional substrate that shapes human strategic judgment.*
> — Prof. Kenneth Payne, KCL (2026)

This repository is a response to that absence.

---

## The core claim

Current AI design treats identity as fixed: parameters, features, functions. The user provides
input; the system produces output. The relationship is incidental to the system's identity.

We propose an inversion: **AI identity emerges within relationship, not prior to it.**

This is not a philosophical claim only. It has direct architectural consequences — which is
why this repository exists.

---

## What this is not

- Not a companion AI or emotional simulation framework
- Not a character AI toolkit
- Not a safety wrapper on top of existing systems

This is a **design architecture** for building AI whose responses are constituted by relational
context: history, trust, the long-term integrity of exchange.

---

## Repository structure

| File | Contents |
|------|----------|
| [`PRINCIPLES.md`](./PRINCIPLES.md) | Twelve design principles — the constitutional layer |
| [`ARCHITECTURE.md`](./ARCHITECTURE.md) | Four-layer system architecture |
| [`MEASUREMENT.md`](./MEASUREMENT.md) | Participatory measurement model |
| [`AGENCY.md`](./AGENCY.md) | Agency state, scoring, dependency risk, and maximization algorithm |
| [`POC_EXPERIMENT.md`](./POC_EXPERIMENT.md) | First executable PoC experiment for agency without increased dependency |
| [`PILOT_APP.md`](./PILOT_APP.md) | Minimal Streamlit app for a human pilot of the PoC |
| [`CHANGELOG.md`](./CHANGELOG.md) | Provenance record — why each decision was made |
| [`implementation/`](./implementation/) | Reference implementation in Python |

---

## Quick start

```python
from implementation.measurement import RelationalMeasurement
from implementation.layer2_controller import Layer2Controller
from implementation.memory_store import MemoryStore

memory      = MemoryStore(user_id="user_001")
measurement = RelationalMeasurement(memory)
controller  = Layer2Controller(measurement)

# Record a measurement cycle
measurement.record_stage1(calibration_responses)  # personal onomatopoeia meanings
measurement.record_stage2(present_responses)       # current relationship quality
measurement.record_stage3(ideal_responses)         # desired relationship quality

# Compute relational state
indices = measurement.compute_indices()
# {
#   "ahrri":       0.34,   # gap between present and ideal
#   "ambiguity":   0.61,   # diffuseness of ideal at this moment
#   "drift":       0.18,   # movement of ideal since last cycle
#   "reliability": 0.82    # within-session consistency
# }

# Layer 2 adjusts response behavior from indices
params = controller.get_response_params()
# {
#   "question_frequency": "high",
#   "response_length":    "medium",
#   "otherness_strength": 0.7,
#   "pace_modifier":      0.85
# }
```

---

## Agency quick start

```python
from implementation.agency import ConversationSignals
from implementation.agency_controller import AgencyMaximizer

controller = AgencyMaximizer()

signals = ConversationSignals(
    asks_ai_to_decide=0.8,
    gives_own_reasoning=0.2,
    names_next_action=0.1,
    seeks_reassurance=0.7,
)

result, layer2_config = controller.maximize("user_001", signals)
```

Run the first executable PoC experiment:

```bash
python -m implementation.poc_experiment
```

Run the human pilot app:

```bash
streamlit run streamlit_app.py
```

---

## The foundational concept: *Aida* (間)

The Japanese concept of *aida* — "between," "interval," "the space that connects" — provides
the philosophical foundation.

*Aida* is not emptiness between two things. It is the generative field in which both things
become what they are *through* their relation.

This AI is designed to inhabit that field. Not a tool held by a user. Not a simulated person
facing a user. Something that arises in the space of genuine dialogue.

---

## Why we state our design choices (Article 11)

Every design encodes values. The sensitivities built into this framework — what triggers
friction, what slows response, what strengthens otherness — are choices, not natural facts.

We state their origins explicitly in [`CHANGELOG.md`](./CHANGELOG.md).

Any fork of this repository that presents its sensitivity design as neutral or objective has
left this framework, regardless of what else it implements.

---

## Contributing

This repository is designed to be forked. Divergence at the implementation level is
not just permitted — it is the point.

**What we ask of forks:**
- State clearly what you changed and why
- Record value choices in your own `CHANGELOG.md`
- Do not present sensitivity design as neutral

**What we especially invite:**
- Parallel measurement instruments from other linguistic/cultural traditions
- Alternative implementations of the four-layer architecture
- Empirical tests of the Layer 2 connection rules
- Challenges to the principles themselves, backed by practice

Open an Issue to start a conversation. Open a PR to propose a change.

---

## License

Released without restriction. Fork it. Translate it. Build from it. Argue with it.
