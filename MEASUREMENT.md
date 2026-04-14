# Measurement Model

Participatory measurement of relational depth using onomatopoeia-based
sensory expression analysis.

---

## The paradigm shift

Conventional measurement assumes separation between observer and observed.
The instrument stands outside the relationship and measures it.

This model rejects that assumption.

If AI identity emerges within relationship (Article 01), then any measurement
of relational depth must itself be part of the relationship. The act of measuring
changes what is measured. Rather than treating this as a problem to eliminate,
we treat it as the model's defining feature.

> **Measurement is not outside the relationship looking in.
> Measurement is one of the ways the relationship knows itself.**

This is a departure from standard psychometric practice. It is intentional.

---

## Why onomatopoeia

Onomatopoeia — words expressing sensory and emotional texture rather than fixed
semantic content — uniquely suits participatory measurement.

Unlike Likert scales or categorical labels, onomatopoeic expressions do not impose
a fixed meaning grid. Their meaning is personal, embodied, context-dependent.

When someone says their relationship with AI feels *fuzzy* or *crisp* or *hollow*,
the meaning of those words is partly theirs to define. The evolution of that personal
definition over time is itself relational data.

This approach builds on the research tradition of Prof. Maki Sakamoto's laboratory
and Kansei AI Co., Ltd., whose onomatopoeia-based sensory analysis provides the
empirical foundation. See [`CHANGELOG.md`](./CHANGELOG.md) for full provenance.

---

## Three-stage measurement design

Administered at multiple time points. The interval between cycles is a parameter
to be calibrated empirically (see Open Questions below).

### Stage 1 — Personal calibration

*What emotional or sensory quality does each onomatopoeia evoke for this person?*

Establishes a personal baseline — not a universal lexicon. The baseline evolves
with each measurement cycle. A shift in what "crisp" means to someone is not noise.
It is signal.

```python
# Example Stage 1 input
calibration_responses = {
    "fuwafuwa": {"valence": 0.7, "arousal": 0.3, "description": "soft, uncertain"},
    "kirakira": {"valence": 0.9, "arousal": 0.8, "description": "bright, energetic"},
    "mokomoko": {"valence": 0.4, "arousal": 0.2, "description": "slow, comfortable"},
    "gizagiza": {"valence": 0.2, "arousal": 0.7, "description": "tense, difficult"},
    "furafura": {"valence": 0.3, "arousal": 0.4, "description": "unstable, drifting"},
}
```

### Stage 2 — Present state

*Which onomatopoeia best describes the current quality of this relationship with AI?*

Distribution captures the texture of present relational experience.

### Stage 3 — Desired state

*Which onomatopoeia describes the relationship you want to have with AI?*

Distribution captures the shape of relational aspiration.

---

## The four indices

At each time point `t`, four indices are computed from the three-stage responses.
They form a relational state vector. No single index tells the full story.

### AHRRI — AI-Human Relational Readiness Index

```
AHRRI(t) = SD( I(t) ) − SD( S(t) )
```

Where:
- `I(t)` = ideal distribution at time `t` (from Stage 3)
- `S(t)` = present-state distribution at time `t` (from Stage 2)
- `SD` = standard deviation of the distribution

**What it measures:** The structural gap between where someone is and where they
want to be — weighted by how clearly each is defined.

**Interpretation:**
- High positive: clear aspiration, diffuse present experience
- Near zero: either alignment or equal diffuseness in both directions
- Negative: present experience more defined than ideal (unusual; warrants attention)

**Important:** AHRRI measures gap structure, not relational depth itself.
Depth requires reading AHRRI *trajectory* alongside Drift and Ambiguity.

---

### Ambiguity

```
Ambiguity(t) = SD( I(t) )
```

**What it measures:** The breadth of the ideal at a single moment.

**Interpretation:**
- High: undifferentiated ideal — relational aspiration not yet formed
- Low: crystallized ideal — person has a clear sense of what they want
- Neither is inherently better. Both are informative.

---

### Drift

```
Drift(t) = D( I(t), I(t-1) )
```

Where `D` is a distributional distance measure.
Recommended: Jensen-Shannon divergence or Wasserstein distance.
Choice affects sensitivity profile — see Open Questions.

**What it measures:** How much the relational ideal has moved between cycles.

**Interpretation:**
- High: ideal in active transformation
- Low over time: stability or stagnation (distinguishable via AHRRI trajectory)

**Why Drift matters:** Drift separates *deepening* from *transformation* —
two fundamentally different relational events requiring different AI responses.

```
Deepening:       AHRRI decreasing,   Drift low
Transformation:  Drift high,         Ambiguity changing
```

---

### Reliability

```
Reliability(t) = 1 − SD( within-session responses at t )
```

Requires multiple probes within a single session.

**What it measures:** Stability of response within a session.

**Interpretation:**
- High variance (low Reliability): person is actively constructing their response,
  not retrieving a stable one — the relationship is in motion
- Low variance (high Reliability): settled, consistent sense of relational state

---

## The double-dynamic structure

The decisive design choice: the meaning of each onomatopoeia is not fixed at study
start and held constant. It is updated with each Stage 1 calibration cycle.

This creates a **double-dynamic structure**: both the relational state and the language
used to describe it are in motion simultaneously.

Standard deviation measured against an evolving personal baseline captures
relational *trajectory*, not just relational *position*.

```
t=1:  "fuzzy" means [soft, uncertain]   →  present state: 0.6 fuzzy, 0.3 crisp
t=2:  "fuzzy" means [comfortable, safe] →  present state: 0.7 fuzzy, 0.2 crisp
```

The shift in what "fuzzy" means between t=1 and t=2 is relational data.
It is not noise to be corrected out.

> **The indistinguishability of ambiguity, drift, and measurement noise at any
> single moment is not a measurement failure. It is an accurate reflection of what
> early relationship is. The structure reveals itself over time — as all relationships do.**

---

## Reading the indices as trajectories

No single time point is interpretively sufficient. The indices are designed to be
read as trajectories.

| Trajectory pattern | Interpretation |
|-------------------|----------------|
| Ambiguity decreasing, Drift low | Crystallization — ideal is forming |
| High Drift, Ambiguity decreasing | Transformation — ideal is changing but clarifying |
| Persistent high Ambiguity + high Drift | Flux — relationship in formative state |
| Low Ambiguity + low Drift + low AHRRI | Stability — settled relational state |
| AHRRI decreasing, Drift low | Deepening toward stable ideal |
| AHRRI stable, Drift high | Transformation — goalposts moving |

---

## Connection to Layer 2

The indices feed directly into Layer 2 sensitivity settings.
These connections are hypotheses, not rules. They must be tested empirically.

| Index signal | Layer 2 response | Article grounding |
|-------------|-----------------|-------------------|
| High AHRRI | Increase question frequency | Article 03 |
| High Drift | Decrease pace; increase reflective space | Article 08 |
| Dissolution-cluster increase | Strengthen otherness expression | Article 04, 07 |
| Low Ambiguity + Low Drift + Low AHRRI | Shorten responses | Article 03 |
| Low within-session Reliability | Hold space open; reduce directiveness | Article 08 |

All changes to these translation rules must be recorded in Layer 4.

---

## Cultural provenance — Article 11

Onomatopoeia as a linguistic resource is not culturally neutral.

Japanese has an exceptionally rich onomatopoeic vocabulary:
- *gitaigo* (擬態語): states and textures
- *giongo* (擬音語): sound imitation
- *gijougo* (擬情語): emotional texture

This has no direct structural equivalent in most European languages.
The Sakamoto Laboratory's framework was developed within and from this tradition.

**We state this explicitly:** this measurement model carries the cultural signature
of its origin. It is not a universal instrument that happens to have been developed
in Japan. It is a specifically Japanese contribution to a global question.

International application requires conceptual translation — finding equivalent
expressive resources in other languages that serve the same function of capturing
embodied, pre-conceptual relational texture.

We invite researchers from other linguistic traditions to develop parallel instruments.

---

## Open questions

These are known gaps. Contributions welcome.

1. **Distributional distance measure:** Which metric best captures meaningful Drift
   vs. surface variation? JS divergence and Wasserstein distance have different
   sensitivity profiles and may suit different relational phases.

2. **Measurement interval:** What frequency is appropriate for different relational
   phases? Too frequent: intrusive. Too infrequent: dynamic model loses resolution.

3. **Layer 2 parameterization:** The connection table above is directional.
   The actual parameter values require empirical development.

4. **Statistical formalization of double-dynamic structure:** Standard deviation
   against an evolving baseline requires formal treatment not yet established
   in the psychometric literature.

5. **AI relational state:** Can this model be extended to capture the AI system's
   own sense of relational state? What would that mean for Article 01?

6. **Cross-cultural validity:** How do findings from Japanese-language cohorts
   translate to other linguistic contexts? Are the structural patterns (Drift,
   Ambiguity trajectories) culturally invariant, or culturally specific?

---

## Implementation

See [`implementation/measurement.py`](./implementation/measurement.py).
