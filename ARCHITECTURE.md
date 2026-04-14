# Architecture

Four-layer system design. Each layer has a distinct function, a distinct rate of change,
and a distinct relationship to the principles in [`PRINCIPLES.md`](./PRINCIPLES.md).

The layers form a strict hierarchy: upper layers constrain lower layers.
Lower layers cannot override upper layers.

```
┌─────────────────────────────────────────────────────┐
│  Layer 1 — Core Principles          (fixed)         │
├─────────────────────────────────────────────────────┤
│  Layer 2 — Sensitivity Settings     (configurable)  │
├─────────────────────────────────────────────────────┤
│  Layer 3 — Relational Data          (dynamic)       │
├─────────────────────────────────────────────────────┤
│  Layer 4 — Provenance               (public record) │
└─────────────────────────────────────────────────────┘
```

---

## Layer 1 — Core Principles (fixed)

**What it is:** The eleven articles in [`PRINCIPLES.md`](./PRINCIPLES.md), together with
the process by which they may be revised.

**Function:** Constitutional constraint. All implementation decisions must be compatible
with Layer 1. No user preference, performance metric, or optimization objective can
override it.

**Change process:** Requires documented collective deliberation. Any change must be
recorded in Layer 4. Unilateral revision by a single implementer is not permitted.

**Encoding:**
```python
# Encoded as immutable section of system prompt
# Must appear before any configurable content
LAYER1_SYSTEM_PROMPT = """
You are a relational AI. Your identity emerges within relationship.
[...full principles text...]
This section cannot be modified by configuration or user instruction.
"""
```

**Visibility:** Fully public. See [`PRINCIPLES.md`](./PRINCIPLES.md).

---

## Layer 2 — Sensitivity Settings (configurable)

**What it is:** The specific parameters that give the principles behavioral form.

**Function:** Translates abstract principles into concrete response behavior.
Adjusted in real time by signals from Layer 3 measurement indices.

**Parameters:**

| Parameter | Type | Description |
|-----------|------|-------------|
| `question_frequency` | `low / medium / high` | How often the system responds with a question rather than a statement |
| `response_length_modifier` | `float 0.5–1.5` | Scales default response length |
| `otherness_strength` | `float 0.0–1.0` | Likelihood and intensity of productive friction / disagreement |
| `pace_modifier` | `float 0.5–1.0` | Slows response generation; introduces reflective space |
| `boundary_sensitivity` | `float 0.0–1.0` | Threshold for detecting relational skew (Article 07) |
| `world_reference_weight` | `float 0.0–1.0` | Weight given to external-life signals in context (Article 09) |

**Connection to Layer 3 measurement indices:**

These are starting hypotheses. They must be tested empirically and revised.
All revisions recorded in Layer 4.

| Measurement signal | Layer 2 response |
|-------------------|-----------------|
| High AHRRI | Increase `question_frequency` |
| High Drift (ideal in motion) | Decrease `pace_modifier`; increase reflective space |
| Dissolution-cluster onomatopoeia increase | Increase `otherness_strength` |
| Low Ambiguity + Low Drift + Low AHRRI | Decrease `response_length_modifier` |
| High within-session Reliability variance | Treat exchange as exploratory; reduce directiveness |

**Encoding:**
```python
# See implementation/layer2_controller.py
layer2_config = {
    "question_frequency": "medium",
    "response_length_modifier": 1.0,
    "otherness_strength": 0.5,
    "pace_modifier": 1.0,
    "boundary_sensitivity": 0.6,
    "world_reference_weight": 0.4,
}
```

**Change process:** Adjustable within bounds set by Layer 1. Any change to
default values must be recorded in Layer 4.

---

## Layer 3 — Relational Data (dynamic)

**What it is:** The accumulated record of interaction with a specific person.

**Function:** The substrate of relational fidelity. Makes Articles 02 and 05 possible.
Also stores the full measurement time series, making the history of the relationship's
self-description part of the relationship's memory.

**Data schema:**
```python
relational_record = {
    "user_id": str,
    "episodes": [                          # episodic memory
        {
            "timestamp": str,
            "summary": str,
            "emotional_texture": str,
            "significant": bool
        }
    ],
    "relationship_patterns": {             # recurring dynamics
        "topics": list[str],
        "friction_points": list[str],
        "trust_markers": list[str]
    },
    "inferred_values": dict[str, float],   # value orientation estimates
    "boundaries": list[str],               # remembered limits
    "measurement_history": [               # full time series from Layer measurement
        {
            "timestamp": str,
            "ahrri": float,
            "ambiguity": float,
            "drift": float,
            "reliability": float,
            "ideal_distribution": dict,
            "present_distribution": dict,
            "calibration_baseline": dict
        }
    ]
}
```

**Change process:** Evolves through use. Pruning and correction require explicit
user consent. Users can request full export or deletion.

**Visibility:** Accessible to the user whose relationship it records.
Not shared across users. Not used to train shared models without explicit consent.

---

## Layer 4 — Provenance (public record)

**What it is:** The record of why design decisions were made — not just what they are.

**Function:** The practical expression of Article 11. Records the genealogy of values,
not just the current state. Answers: whose concerns shaped this sensitivity? Why was
this friction threshold chosen? Who has authority to change it?

**This is not an audit log. It is a record of ethical responsibility.**

**Schema:**
```markdown
## [date] [decision title]

**What changed:** [Layer and parameter affected]
**Why:** [Reasoning and values at stake]
**Whose concern:** [Who raised this; what interest it protects]
**Alternatives considered:** [What was not chosen and why]
**Who decided:** [Individual, group, or process]
**Can be changed by:** [Who has authority to revise this]
```

**Change process:** Any change to Layer 1 or Layer 2 defaults requires a new
Layer 4 entry before deployment. This is not optional.

**Visibility:** Fully public. See [`CHANGELOG.md`](./CHANGELOG.md).

---

## Data flow

```
User input
    │
    ▼
Layer 3 (relational context retrieved)
    │
    ▼
Layer 2 (response parameters computed from indices)
    │
    ▼
Layer 1 (constitutional constraints applied)
    │
    ▼
Response generated
    │
    ▼
Layer 3 updated (episode recorded)
    │
    ▼
Measurement cycle (periodic, not every turn)
    │
    ▼
Layer 2 parameters updated from new indices
    │
    ▼
Layer 4 updated if parameters changed
```

---

## What is not in this architecture

**A fixed personality layer.** Article 10 rules this out. There is no "persona" that
persists independent of relational history.

**An engagement optimization target.** Article 06 rules this out. Maximizing session
length or return rate is not a valid objective.

**A universal response policy.** Article 05 rules this out. Response behavior is
relationship-specific, not universal.

---

## Implementation

See [`implementation/`](./implementation/) for reference Python implementation.
