# LestariLens — Malaysia Tourism Intelligence Dashboard

LestariLens is an interactive Streamlit dashboard developed for the DOSM Datathon 2026. It combines official Malaysian tourism data, a structural machine-learning benchmark and an optional Gemini-powered assistant to support evidence-based tourism planning.

## Dashboard capabilities

- National and state-level domestic visitor indicators
- Visitor trends for the available observation years
- Tourism Opportunity Gap analysis comparing actual and model-expected visitor shares
- Infrastructure-capacity and economic-strength comparison
- Illustrative demand-redistribution scenarios
- Evidence, methodology and model limitations
- Optional page-grounded AI follow-up assistant (Ollie)

## Data coverage

Observed years:

```text
2017–2019 and 2023–2025
```

No observations are available for 2020–2022. Trend lines are intentionally disconnected across this period.

The 2024–2025 observations are treated as an untouched holdout period for model evaluation. The Tourism Opportunity Gap is a structural benchmark, not a forecast or causal estimate.

## Requirements

- Python 3.14 or a compatible Python 3 version
- Internet access only when using Ollie
- A Gemini API key only when using Ollie

## Local setup

From the project root:

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

Windows PowerShell setup:

```powershell
py -m venv .venv
.\.venv\Scripts\Activate.ps1
py -m pip install -r requirements.txt
```

## Optional Gemini configuration

The dashboard itself can run without a Gemini key. Ollie requires a valid key.

Create a local `.env` file in the project root:

```env
GEMINI_API_KEY=replace_with_your_own_key
GEMINI_MODEL=gemini-3.1-flash-lite
```

Do not commit or distribute `.env`. Use `.env.example` to document required variables without exposing credentials.

For Streamlit Community Cloud, add the key through the app's Secrets settings instead of uploading `.env`.

## Run the dashboard

```bash
streamlit run backend/app.py
```

Windows PowerShell:

```powershell
py -m streamlit run backend/app.py
```

Streamlit will print the local URL in the terminal, normally:

```text
http://localhost:8501
```

The interface is optimized for the Light theme.

## Expected project structure

```text
malaysia_tourism_app/
├── assets/
│   └── images/
│       └── tiger_sheet.png
├── backend/
│   ├── app.py
│   └── ai_service.py
├── ml/
│   └── handoff/
│       └── for_hongyik/
│           ├── sample_predictions.csv
│           └── state_features.csv
├── .env.example
├── .gitignore
├── README.md
└── requirements.txt
```

## Evaluation notes

- DOSM data remains the primary evidence source.
- AI responses are grounded in validated page context rather than screenshots.
- AI output is supplementary and does not replace the deterministic dashboard.
- Scenario Lab performs illustrative arithmetic redistribution only; it does not predict policy outcomes.
- Results for Perlis and W.P. Putrajaya require additional caution because of lower model reliability.

## Troubleshooting

### Ollie is unavailable

Confirm that `GEMINI_API_KEY` is present in the local `.env` file and restart Streamlit. The main dashboard remains usable when Ollie is unavailable.

### Changes do not appear

Stop Streamlit with `Ctrl+C`, then run:

```bash
streamlit cache clear
streamlit run backend/app.py
```

Refresh the browser without cache using `Command+Shift+R` on macOS or `Ctrl+F5` on Windows.

### Data file not found

Confirm that both CSV files exist under:

```text
ml/handoff/for_hongyik/
```

## Security and packaging

The submission ZIP must not contain:

- `.venv/`
- `.git/`
- `__pycache__/`

Include `requirements.txt` and `.env.example` so evaluators can reproduce the environment safely.
