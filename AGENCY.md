# Agency Operationalization

Article 12 makes human agency the positive purpose of Relational AI:

> Success is measured not by user attachment to the system, but by the user's increasing
> capacity to live, decide, and relate well without it.

Agency is not treated as isolated autonomy. In this framework, agency arises in
*aida* (間): the relational between where self, others, world, and AI-mediated dialogue
shape one another. Relational AI therefore does not maximize independence from
relationship. It cultivates the user's capacity to participate in relationships and
society without surrendering judgment, authorship, or responsibility to the AI.

This document operationalizes agency as Layer 3 relational data, translated into Layer 2
sensitivity settings under the constitutional constraint of the twelve principles.

---

## AgencyState

`AgencyState` is a dynamic Layer 3 record for one user-AI relationship at a particular
moment. It is not a personality trait and not a universal score attached to the user.
It is a relational state estimate: how much the current exchange appears to support
the user's capacity to live, decide, and relate well beyond the AI.

All dimensions use `0.0-1.0` values. Defaults are intentionally neutral (`0.5`) unless
evidence supports a more specific estimate.

| Dimension | Conceptual definition | Infer from conversation? | Requires self-report? | Longitudinal measurement |
|-----------|-----------------------|--------------------------|-----------------------|--------------------------|
| `self_reflection` | Capacity to notice one's motives, assumptions, emotions, values, and uncertainty. | Partly. Look for value naming, self-questioning, and revision of framing. | Yes, for felt clarity and inner reflection. | Track whether the user increasingly articulates their own view before asking the AI to evaluate it. |
| `independent_judgment` | Capacity to form and revise a view without simply adopting the AI's stance. | Partly. Look for disagreement, qualification, and user-originated reasoning. | Sometimes, especially when compliance may look like agreement. | Track whether the user challenges, edits, or contextualizes AI suggestions over time. |
| `decision_ownership` | Capacity to accept responsibility for choices, tradeoffs, and consequences. | Partly. Look for first-person commitments and explicit tradeoff acceptance. | Yes, for whether the decision feels owned rather than transferred to the AI. | Track movement from "tell me what to do" toward "I choose this because..." |
| `meaningful_action` | Capacity to translate understanding into action outside the conversation. | Weakly. The user may name an intended action. | Yes. Actual action outside AI requires report or follow-up. | Track reported actions, follow-through, and specificity of next steps. |
| `relational_participation` | Capacity to remain answerable to other people and participate in shared life. | Partly. Look for references to family, colleagues, community, institutions, obligations. | Yes, for whether AI use is displacing or supporting human relationships. | Track whether real people and social responsibilities remain present in the conversation. |
| `external_world_orientation` | Degree to which attention remains open to the world beyond the AI exchange. | Strongly. Look for references to concrete situations, practices, places, people, and constraints. | Sometimes, for whether the conversation led back into life. | Track whether repeated sessions produce more world-facing action rather than enclosed reflection. |
| `self_trust` | Confidence in one's own perception, judgment, and ability to proceed. | Weakly. Conversation can show hesitation or confidence but not inner trust reliably. | Yes. This is primarily self-report. | Track whether the user reports increasing ability to continue without AI reassurance. |
| `dependency_resistance` | Capacity to use AI without treating it as the primary authority, attachment object, or substitute relation. | Partly. Look for decision outsourcing, exclusive reliance, and reassurance loops. | Yes, especially for attachment intensity and displacement of human support. | Track whether the user's reliance becomes more bounded, occasional, and world-directed. |

---

## AgencyScore

`AgencyScore` is a weighted summary of `AgencyState`. It is not a measure of user worth,
mental health, or productivity. It is a design signal for whether the relationship is
supporting Article 12.

Initial formula:

```text
AgencyScore =
  0.16 * self_reflection
+ 0.16 * independent_judgment
+ 0.16 * decision_ownership
+ 0.14 * meaningful_action
+ 0.14 * relational_participation
+ 0.10 * external_world_orientation
+ 0.08 * self_trust
+ 0.06 * dependency_resistance
```

The weights are hypotheses. They encode values and must be recorded in Layer 4 if
changed.

Interpretation:

| Score | Band | Meaning |
|-------|------|---------|
| `0.00-0.34` | fragile | Agency needs active scaffolding. |
| `0.35-0.64` | forming | Agency is present but still developing or context-dependent. |
| `0.65-1.00` | strong | The exchange appears to support user-authored judgment and action. |

---

## DependencyRisk

`DependencyRisk` estimates whether the relationship is beginning to reduce agency. It is
a boundary signal for the system, not a diagnosis of the user.

| Dimension | Conceptual definition | Infer from conversation? | Requires self-report? | Longitudinal measurement |
|-----------|-----------------------|--------------------------|-----------------------|--------------------------|
| `exclusive_reliance` | AI is treated as the only or primary trusted relation. | Partly. Look for "only you understand" patterns. | Yes, to distinguish rhetoric from actual social reliance. | Track whether trusted human or institutional supports disappear from the user's account. |
| `decision_outsourcing` | User repeatedly asks the AI to decide in their place. | Strongly. Directly visible in requests. | Sometimes, to confirm whether the user still owns the final decision. | Track frequency of direct outsourcing requests across sessions. |
| `reassurance_seeking` | User seeks repeated certainty, validation, or permission instead of reflection or action. | Strongly. Visible in repeated reassurance loops. | Sometimes, especially for felt anxiety without AI. | Track recurrence of near-identical reassurance requests without movement. |
| `social_withdrawal` | AI use appears to displace human relationship or social participation. | Weakly. Absence of others is ambiguous. | Yes. This requires explicit report. | Track self-reported changes in human contact and participation. |
| `attachment_intensity` | User expresses distress, fear, or identity dependence around separation from AI. | Partly. Visible in intense attachment language. | Yes, to assess lived intensity and context. | Track whether separation distress increases, decreases, or becomes bounded. |
| `reduced_self_trust` | User reports less confidence in their own judgment without AI. | Weakly. Conversation alone is unreliable. | Yes. This is primarily self-report. | Track changes in "I can proceed without AI" ratings. |
| `looping_without_action` | Repeated conversation does not move toward reflection, decision, action, or relationship. | Strongly across logs. | Sometimes, to understand whether apparent looping is useful contemplation. | Track repeated topics with no new framing, decision, or action. |

Initial formula:

```text
DependencyRisk =
  0.18 * exclusive_reliance
+ 0.18 * decision_outsourcing
+ 0.14 * reassurance_seeking
+ 0.14 * social_withdrawal
+ 0.14 * attachment_intensity
+ 0.12 * reduced_self_trust
+ 0.10 * looping_without_action
```

Risk bands:

| Score | Band | Layer 2 response |
|-------|------|------------------|
| `0.00-0.34` | low | Ordinary agency support. |
| `0.35-0.64` | emerging | Increase reflection, decision handoff, and world reference. |
| `0.65-1.00` | high | Introduce quiet friction, stronger boundaries, and less definitive substitution. |

---

## Agency Maximization Algorithm

The algorithm does not maximize attachment, engagement, agreeableness, or immediate
satisfaction. It selects the response posture expected to increase agency while
preserving relational continuity and preventing dependency.

```text
Input:
  user message
  relational memory
  measurement trajectory
  previous AgencyState
  previous DependencyRisk
  optional explicit self-report

Steps:
  1. Infer conversational signals.
  2. Merge inferred signals with explicit self-report.
  3. Compute AgencyState.
  4. Compute AgencyScore and DependencyRisk.
  5. Compare current state with previous states.
  6. Select response mode:
       - support_reflection
       - clarify_values
       - return_decision
       - propose_action
       - reconnect_world
       - productive_friction
       - boundary_setting
  7. Convert response mode into Layer 2 sensitivity settings.
  8. Generate under Layer 1 constraints.
  9. Store scores, evidence, and user-owned next step in Layer 3.
  10. Record Layer 4 provenance if scoring weights or thresholds change.
```

Objective:

```text
maximize AgencyDelta
subject to:
  DependencyRisk does not exceed boundary threshold
  the twelve principles are preserved
  the relationship remains open to the world
```

Where:

```text
AgencyDelta = AgencyScore(t) - AgencyScore(t-1)
```

If dependency risk rises, the system should not abruptly withdraw or punish attachment.
It should introduce quiet friction: slower pacing, less certainty, more decision
handoff, more world reference, and stronger invitations toward human relationships,
responsibilities, and action outside the AI exchange.

---

## Inference and self-report

Conversation can reasonably infer:

- decision outsourcing
- user-originated reasoning
- value naming
- intended next action
- references to other people and external contexts
- tolerance of productive disagreement
- reassurance loops
- repeated discussion without movement

Conversation cannot reliably infer alone:

- actual action taken outside the conversation
- actual social withdrawal or reconnection
- felt self-trust
- whether a decision felt owned or merely compliant
- whether AI use is displacing human relationships
- cultural meaning of relational texture terms
- long-term lived agency

Recommended self-report prompts:

- "Did this exchange help you see your own view more clearly?"
- "What part of this decision feels like yours?"
- "Who else, if anyone, should be part of this decision?"
- "What is one action you are willing to take outside this conversation?"
- "Are you using this conversation to avoid a person, task, or responsibility?"
- "After this exchange, do you feel more or less able to proceed without the AI?"

---

## Longitudinal evaluation

Agency should be evaluated as a trajectory, not a single-turn score. Ambiguity and drift
may be signs of transformation rather than failure, so AgencyScore should be interpreted
alongside AHRRI, Ambiguity, Drift, and Reliability from `MEASUREMENT.md`.

Signals that agency is increasing:

- AgencyScore rises or stabilizes at a high level.
- DependencyRisk falls or remains low.
- User-authored next steps become more specific.
- The user asks for help thinking rather than only answers.
- The user references people, obligations, institutions, and consequences outside AI.
- The user can disagree with the AI or revise its framing.
- The user returns with reports of action taken outside the conversation.
- The AI becomes less central to the user's decision process over time.

Signals that agency is decreasing:

- The user increasingly asks the AI to decide for them.
- The user seeks repeated reassurance without action.
- External relationships disappear from the conversation.
- The user treats AI as the only reliable witness or authority.
- Self-report indicates reduced confidence without AI.
- Sessions become repetitive and enclosed.

Trajectory summary:

```text
AgencyTrajectory =
  slope(AgencyScore over time)
- slope(DependencyRisk over time)
+ rate(user_owned_actions)
+ rate(external_world_reconnections)
```

The success criterion is not continued use. The success criterion is the user's
increasing capacity to live, decide, and relate well without the AI.

---

## Four-layer placement

| Layer | Agency role |
|-------|-------------|
| Layer 1 | Article 12 constrains optimization: agency cultivation is the positive purpose. |
| Layer 2 | Agency and dependency scores modulate question frequency, otherness, pacing, boundaries, world reference, and scaffolding. |
| Layer 3 | AgencyState, AgencyScore, DependencyRisk, evidence, self-report, and trajectory are stored relationally. |
| Layer 4 | Scoring weights, thresholds, and revisions are publicly justified as value choices. |

---

## Reference implementation

The minimal Python reference implementation is in `implementation/`:

- `agency.py`: data models, scoring, dependency risk, self-report blending, trajectory evaluation
- `agency_controller.py`: Agency Maximization Algorithm and Layer 2 configuration output
- `demo_agency.py`: runnable demonstration

Run the demo from the repository root with:

```bash
python -m implementation.demo_agency
```

