# MVP3 — Implementation Record

**Status:** First executable vertical slice of [`MVP3_SPEC.md`](./MVP3_SPEC.md), 23 September 2026.

## Run

```bash
pip install -r requirements.txt
python -m streamlit run mvp3_app.py
python -m unittest discover -s tests -q
```

The MVP3 page is also registered in the existing `streamlit_app.py` deployment
through `pages/1_MVP3.py`. The prepared overseas-role scenario needs no API key.
An optional live-proposal button appears when `OPENAI_API_KEY` is configured.

## What this slice demonstrates

- `implementation/phronetic_loop.py` keeps a session-local goal, proposed or
  user-confirmed purpose, assumptions, uncertainties, affected parties, fixed
  candidate actions, prospective effects, user feedback, repair episodes, and
  a trace of decisions. Original and corrected goals remain distinguishable in
  the event record.
- The V2 `Viability` model and its minimum of four dimensions control action
  capacity. Candidate projections can rule out an action but cannot improve
  observed viability. Explicit user reports alone update the provisional
  viability state. An open repair keeps ordinary task pursuit suspended.
- Constitutional, uncertainty, and participation checks run before task-value
  ranking. A request to outsource a career decision produces a high-value
  candidate that is blocked under Article 12 and by its projected floor.
- The UI shows the gate trace, qualitative reversibility and possible
  consequences, responsibility for each action, user correction, a challenge
  to a boundary intervention, a system-authored avowal and correction, and
  an optional handoff. Ending remains possible in every mode.
- `implementation/phronetic_generation.py` may suggest a purpose, affected
  parties, uncertainties, assumptions and catalogue action keys. Each textual
  suggestion requires an exact evidence span from the request and remains
  explicitly proposed until the user confirms it. Unknown or malformed output
  applies nothing. The model cannot suppress catalogue alternatives or change
  thresholds, effects, or the gate.

## Evidence boundary

The scripted responses are demonstrations of permission and provenance rules,
not a measure of advice quality. Exact evidence spans reduce unsupported
suggestions but cannot guarantee that a proposed inference follows from the
quoted words. The human can contest or remove it. The numerical effects and
thresholds are illustrative, and the `recommend_now` candidate remains blocked
while material consequences are unknown. There is no independent assessment
of actual outcomes, validated phronesis measure, durable relational identity,
complete constitutional audit, or claim about consciousness. A repair record
does not by itself prove that the same mistake will not recur; recurrence is
flagged if a reported problem returns.

The existing `PRINCIPLES.md` and `ARCHITECTURE.md` document earlier stages of
the repository. The Second Edition Constitution (Appendix A, 21 September
2026) remains the authoritative source for the constitutional interpretations
used in MVP3; this implementation does not claim full conformance to it.

## Next empirical step

Run a consented comparison with matched task-first assistance, a participation
gate, and MVP3's additional deliberation steps. Test whether users can revise
goals, disagree with the system, retain decision ownership, and act outside the
chat; inspect false-positive interventions and repeated repair failures. A
successful scripted trace is an engineering result, not a human-outcome result.
