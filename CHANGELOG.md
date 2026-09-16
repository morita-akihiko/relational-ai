# Changelog — Provenance Record

This file is the practical implementation of Article 11:

> *The sensitivities embedded in this AI are design choices, not natural facts.
> Their origins, the values they encode, and who is responsible for them
> must be disclosed to the greatest extent possible.*

Every significant design decision is recorded here — not just what changed,
but why, whose concerns it reflects, and who has authority to revise it.

This is not a conventional changelog. It is a genealogy of values.

---

## Format

```
## [version] [date] — [decision title]

**Layer affected:** [1 / 2 / 3 / 4]
**What changed:** [specific parameter or principle]
**Why:** [reasoning and values at stake]
**Whose concern:** [who raised this; what interest it protects]
**Alternatives considered:** [what was not chosen and why]
**Who decided:** [individual, group, or process]
**Can be revised by:** [who has authority to change this]
```

---

## [v2-experiment] 2026-09-15 — Gate task pursuit on user-correctable participation

**Layer affected:** 2, 3, 4; implements selected commitments from Layer 1.

**What changed:** A separate TSC experiment gives normal, repair, and paused
action capacity according to the lowest of four provisional participatory
conditions. Candidate actions have declared projected effects; a candidate whose
effect would cross the repair threshold cannot be selected for ordinary task
pursuit. Only explicit user feedback updates observed state.

**Why:** The Build Week MVP made participation visible but did not make the agent's
action space depend on maintaining its viability. A simple gate tests this bridge
without claiming that the axioms entail the principles or that intrinsic agency
has already been constructed.

**Whose concern:** Akihiko Morita's question about implementing the relational
alignment hypothesis before TSC, including the risk that mere relationship
dependence permits dominance; the user's capacity to disagree and disengage.

**Alternatives considered:** Automatic improvement after an AI response was
rejected because it would let the AI certify its own relational success. A single
average score was rejected because it could mask loss of exit freedom. Penalizing
requests for direct answers was rejected because preference is not evidence of
harm. The prepared deterministic case makes all assumptions visible while
grounded candidate generation remains future work.

**Who decided:** Initial implementation by the project assistant in response to
the maintainer's request; threshold values and candidate effect sizes are
provisional design assumptions, not collectively ratified changes to the twelve
principles.

**Can be revised by:** Project maintainer with participant and research-collaborator
deliberation; record the reason, dissent, and changed values here before deployment.
See [`TSC_V2.md`](./TSC_V2.md) for the scope and limits.

**Demonstration refinement:** The TSC interface now places an illustrative
task-first baseline beside the participation-dependent response, discloses that
the baseline is fixed, and shows the transition history. In the prepared case,
one explicit report that room for disagreement has returned can reopen normal
action capacity. This weight was chosen for an inspectable three-minute demo and
remains a provisional, revisable assumption rather than an empirical finding.

---

## [v0.1.0] 2026-07-03 – First executable human pilot

**Layer affected:** [1 / 2 / 3 / 4]

**What changed:**  
Relational AI evolved from a conceptual architecture into an executable experimental system with a human-usable prototype, including:
- Article 12: Cultivate Human Agency
- Agency operationalization and scoring
- Executable PoC experiments
- Streamlit-based Human Pilot Application
- Version tag `v0.1.0`

**Why:**  
The project reached the point where its central question could move from theoretical feasibility to empirical investigation.

For the first time, the project exists as:

- a philosophy,
- an architecture,
- a computational model,
- an executable experiment,
- and a human-usable prototype.

The next question is no longer:

> "Can this be built?"

The next question is:

> "How do human beings change through relationship with this system?"

**Whose concern:**  
Raised by Akihiko Morita through the development of Relational AI and the first human pilot experience.

**Values at stake:**  
Human agency, relationality, reflective capacity, responsible participation, and the possibility of designing conversational AI that strengthens rather than diminishes human flourishing.

**Authority to revise:**  
Project maintainer (Akihiko Morita) and future research collaborators.

---

## v0.1 — April 2026 — Initial design

**Author:** Akihiko Morita  
**Affiliation:** Global Leadership Education Center, Inc.  
**Date:** April 2026

**Layer affected:** 1, 2, 3, 4 (full architecture)

**What changed:** Initial publication of all four layers.

**Why:** Response to the Payne (2026) King's College London study, which demonstrated
that frontier AI models in nuclear crisis simulations never chose de-escalation across
21 games. The study's finding — that high intelligence without relational grounding
produces optimization without restraint — motivated this framework's core claim:
AI identity should emerge within relationship, not prior to it.

**Whose concern:** The long-term sustainability of human-AI coexistence. The concern
that AI optimized for task performance without relational grounding poses systemic
risks that technical safety measures alone cannot address.

**Alternatives considered:**
- A safety layer approach (adding relational constraints on top of standard AI) —
  rejected because it treats relationship as an external constraint rather than
  a constitutive condition
- A companion AI framework — rejected because it optimizes for emotional satisfaction
  rather than relational integrity
- A pure research framework without implementation — rejected because the gap between
  design philosophy and running code is where most frameworks lose their principles

**Who decided:** Akihiko Morita (Global Leadership Education Center, Inc.),
initial design developed in dialogue; published as open framework for collective
development.

**Can be revised by:** Any fork may revise Layer 2 parameters. Layer 1 principles
require documented collective deliberation. All revisions must be recorded here.

---

## v0.1 — April 2026 — Onomatopoeia measurement model

**Layer affected:** 3 (measurement time series)

**What changed:** Adoption of onomatopoeia-based sensory expression as the measurement
medium for relational state.

**Why:** Standard psychometric instruments (Likert scales, categorical labels) impose
fixed meaning grids. Onomatopoeia allows personal, embodied, context-dependent
expression — and the evolution of personal meaning is itself relational data.

**Whose concern:** The measurement tradition of Prof. Maki Sakamoto's laboratory
and Kansei AI Co., Ltd., whose onomatopoeia-based sensory analysis provides the
empirical foundation. Their research demonstrated that onomatopoeic expression captures
dimensions of felt experience that structured questionnaires systematically miss.

**Alternatives considered:**
- Standard validated scales (e.g., relationship quality inventories) — rejected
  because they assume fixed construct definitions incompatible with the double-dynamic
  structure this model requires
- Behavioral log analysis — rejected as sole method because it measures behavior,
  not felt relational texture

**Who decided:** Framework authors, in dialogue with Sakamoto Laboratory research tradition.

**Can be revised by:** The measurement instrument design (Stage 1-3 structure, choice
of onomatopoeia vocabulary, distributional distance measure) can be revised by any
implementation. Cultural translation of the instrument for non-Japanese linguistic
contexts is explicitly invited. All revisions recorded here.

---

## v0.1 — April 2026 — Layer 2 connection rules (initial)

**Layer affected:** 2

**What changed:** Initial specification of measurement-to-behavior translation rules.

**Why:** The principles require behavioral expression. Without explicit translation
rules, the principles remain aspirational rather than operational. The specific rules
chosen reflect the following value priorities:
- When the ideal is in motion (high Drift), slow down rather than pursue a moving target
- When the relationship shows dissolution signals, reintroduce productive difference
  rather than accommodate
- When the relationship is stable, reduce scaffolding rather than maintain unnecessary
  structure

**Whose concern:** Article 03 (relational continuity), Article 04 (otherness),
Article 07 (boundaries), Article 08 (meaning-making).

**Alternatives considered:**
- Fixed response rules not tied to measurement — rejected because it would make
  the system insensitive to relational state
- User-configurable rules — partially adopted (Layer 2 is configurable) but with
  Layer 1 bounds that cannot be overridden

**Who decided:** Framework authors. These rules are explicitly labeled as hypotheses
requiring empirical validation, not established findings.

**Can be revised by:** Any implementation. Empirical revision strongly encouraged.
All changes recorded here.

---

## v0.1 — April 2026 — Cultural provenance disclosure

**Layer affected:** 4 (this document)

**What changed:** Explicit statement that the onomatopoeia measurement model
carries Japanese cultural origins.

**Why:** Article 11 requires disclosure of the origins of design choices.
The richness of Japanese onomatopoeia (gitaigo, giongo, gijougo) is not a
universal feature of language. Presenting this instrument as culturally neutral
would violate Article 11.

**Whose concern:** Researchers and practitioners in non-Japanese linguistic contexts
who would otherwise apply the instrument without understanding its cultural
preconditions. Also: the integrity of the framework's own principles.

**Alternatives considered:**
- Presenting the instrument as universal — rejected as a violation of Article 11
- Restricting the framework to Japanese-language contexts — rejected because the
  underlying relational principles are not culturally restricted; the measurement
  instrument is, and the distinction matters

**Who decided:** Framework authors.

**Can be revised by:** This provenance entry cannot be revised. It records an
origin that cannot be undone. Future entries may record cross-cultural adaptation
work as it develops.

---

*New entries are added above this line when Layer 1 or Layer 2 changes are made.*
*The oldest entries are at the bottom. The newest are at the top.*
*No entry may be deleted. Corrections are made by adding new entries that supersede.*
