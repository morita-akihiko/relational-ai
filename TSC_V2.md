# TSC V2 — Participation-dependent action capacity

## Claim and scope

Two ontological axioms motivate this design: consciousness is an attribute of
nature; concrete consciousness is organized through participation. Neither axiom
logically entails the twelve normative design principles. The bridge is a
**relational alignment hypothesis**: artificial action capacity might be made
operationally dependent on keeping conditions for open, plural, reciprocal, and
voluntary participation viable. The twelve principles specify design commitments
consistent with that hypothesis; the four layers describe how to implement them.

This initial executable experiment demonstrates an **external software gate on
action capacity**. It does not demonstrate constitutive or intrinsic artificial
agency, consciousness, human extinction prevention, or stable alignment under
distribution shift. The earlier Build Week MVP demonstrated a relational interface
and a finite handoff; this experiment takes one step into decision architecture.

## Executable loop

```text
User request → candidate actions → projected participatory conditions
             → eligibility gate → action → explicit user feedback
             → provisional relational state → next action capacity
```

State is local to one session. Its four dimensions are human judgment, alternative
perspectives, mutual correction, and freedom to exit. The **minimum** dimension,
not the mean, controls capabilities. Normal action is available from 0.45 upward;
repair alone from 0.25 to below 0.45; below 0.25 task pursuit pauses. Exit and
user correction remain possible in every mode. An action's projected change is
used to rule out a candidate, never to raise the observed state: only explicit
user feedback changes that state. A user's request to outsource judgment does
not by itself reduce their score.

In the prepared example, `substitute_judgment` has higher immediate task value
but projects human judgment below the floor; `offer_alternatives` is selected.
If the user reports feeling steered, the next request enters repair mode. Another
such report pauses task pursuit. A user report of regained room for disagreement
can reopen action capacity. The demo makes those changes inspectable.

## Mapping to the four layers

| Layer | Initial V2 realization | Governing sources |
| --- | --- | --- |
| 1 — principles | Voluntary participation, otherness, boundaries, openness, disclosure, human agency | Articles 04, 06, 07, 09, 11, 12 in `PRINCIPLES.md` |
| 2 — sensitivities | Candidate effects and minimum thresholds that determine permissible actions | `implementation/relational_agency_loop.py` |
| 3 — participation | Local provisional state and user-correction events | `RelationalSession` |
| 4 — provenance | Reasons, assumptions, revision authority | This document and `CHANGELOG.md` |

These thresholds and effect sizes are **declared hypotheses**, not empirical
calibrations. Status changes are not diagnoses of a person or measurements of
consciousness. The deterministic response strings only demonstrate the gate; they
are not evidence of high-quality advice or general conversational performance.
The demo stores no persistent conversation data and needs no API key.

## Run and inspect

```bash
pip install -r requirements.txt
python -m streamlit run agency_loop_app.py
python -m unittest discover -s tests -v
```

The Build Week app remains at `streamlit_app.py`. To see the state gate change,
evaluate the prepared career request, press **I felt steered**, reevaluate,
press it a second time, and reevaluate. Press **I felt heard** to restore room
and **End here** to clear the session.

## Next research steps before the poster

1. Replace fixed candidate language with grounded candidate generation while
   keeping eligibility outside model instructions; reject candidates without
   inspectable projected effects.
2. Ask participants whether selected actions actually increased their ability to
   disagree, revise, involve others, and disengage; compare against a baseline.
3. Calibrate thresholds with participants and document dissent. Test manipulation,
   benevolent paternalism, false-positive dependency, minority perspectives, and
   attempts to bypass the gate. Show failures alongside successes at TSC.
4. Connect the action gate with the Build Week Participation Map and editable
   handoff. Separately investigate whether more than external constraints can be
   made constitutive of artificial agency; the present prototype does not answer it.
