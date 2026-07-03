# Human Pilot Streamlit App

The human pilot app is a minimal Streamlit interface for testing whether Relational AI
can increase agency without increasing dependency risk.

It includes:

- consent;
- pre-agency questionnaire;
- scripted PoC scenario selection;
- chat interface;
- relational-agency response mode selection;
- post-agency questionnaire;
- AgencyState and DependencyRisk scoring;
- JSON data export.

Run:

```bash
streamlit run streamlit_app.py
```

The app uses:

- `implementation/agency.py` for AgencyState and DependencyRisk scoring;
- `implementation/agency_controller.py` for Layer 2 response-mode selection;
- `implementation/poc_experiment.py` for scripted pilot scenarios;
- `implementation/human_pilot.py` for questionnaire conversion, pilot evaluation, and export.

The app is intentionally not a production research tool. It is the first executable
human-pilot surface for the Article 12 success criterion: the user's increasing
capacity to live, decide, and relate well without the AI.

