JejakLestari Intelligence

DOSM Datathon 2026 | Team 404 NOT FOUND

JejakLestari Intelligence is an interactive Malaysia tourism decision-support dashboard. It combines local DOSM tourism and socioeconomic data with transparent model evidence, capacity comparison, and an illustrative scenario tool. Its purpose is to help users move beyond headline visitor counts and examine potential, readiness, trade-offs, and evidence gaps.

Software and requirements

Python 3.12 (tested for the dashboard; see ml/README.md for ML reproduction)
Streamlit 1.64 or newer
Local web browser (Chrome, Edge, Firefox, or Safari)
Dependencies listed in ml/requirements.txt
Internet access is only required for the optional Ollie AI assistant. All dashboard data, charts, filters, model outputs, and scenario calculations run from files included in this package.

Package layout

Keep the following project structure unchanged. The dashboard uses relative paths to load its local files.

Dashboard/
├── backend/
│   ├── app.py
│   └── ai_service.py
├── assets/
│   └── images/
│       └── tiger_sheet.png
├── ml/
│   ├── requirements.txt
│   └── handoff/
│       └── for_hongyik/
│           ├── state_features.csv
│           └── sample_predictions.csv
├── .env.example
└── README.md

The final submission archive should also include a static visual document, for example Dashboard.pdf, containing high-resolution screenshots of the final interactive dashboard. The PDF is for documentation and is not interactive.

Installation and launch

Open a terminal in the Dashboard folder.

Windows (PowerShell)

py -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
pip install -r ml/requirements.txt
streamlit run backend/app.py

If PowerShell blocks activation, run the following once in the same terminal and then activate the environment again:

Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass

macOS / Linux

python3 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
pip install -r ml/requirements.txt
streamlit run backend/app.py

Streamlit will display a local URL, normally http://localhost:8501. Open that URL in a browser. Stop the dashboard with Ctrl+C in the terminal.

Navigation and interactive features

Use the left sidebar to select a page and choose a single global year. The selected year is applied consistently across dashboard pages.

Page	What to explore
Overview	National or selected-state KPIs, actual versus model-expected visitor share, opportunity-gap evidence, and the 2025 national tourism spending mix.
Visitor flows	State visitor trajectories. Hover over lines to inspect values. The lines deliberately break between 2019 and 2023 because no observations are available for 2020–2022.
Sustainability	Bubble comparison of visitor volume, accommodation capacity, and economic strength. Hover over a bubble for state evidence; reference lines are median benchmarks.
Scenario lab	Select different source and target states, then adjust the percentage slider. The national total is preserved. This is an illustrative arithmetic scenario, not a forecast or predicted policy outcome.
Evidence	Historical data, model output, methodology, validation framing, sources, and limitations.
	Ollie assistant (optional)

Ollie is a page-grounded assistant that answers follow-up questions using the validated context of the current page, selected year, and selected state. Type a question in the sidebar, select a suggested follow-up, or use voice input where the browser supports it. Voice transcripts can be edited before sending.

To enable Ollie, create a .env file in the Dashboard folder:

GEMINI_API_KEY=your_api_key_here
GEMINI_MODEL=gemini-3.1-flash-lite

If no key, network connection, or AI quota is available, Ollie will show an availability message. The rest of the dashboard remains fully usable.

Data, method, and interpretation notes

Data sources are local DOSM Malaysian tourism and socioeconomic datasets supplied with this submission.
The analysis covers 16 states and federal territories for observed years 2017–2019 and 2023–2025. There are no observations for 2020–2022; the dashboard does not interpolate or connect across this gap.
The model compares a state's actual visitor share with its model-expected structural visitor share. The resulting Tourism Opportunity Gap is a structural benchmark.
A positive gap is not proof of unmet demand, a marketing problem, causation, or a future forecast. It should trigger further investigation before intervention.
Model training years are 2017–2019 and 2023. The untouched holdout period is 2024–2025.
Perlis and W.P. Putrajaya have lower predictive reliability and should be interpreted with added caution.
The 2025 national spending-category breakdown is a national view and does not change with the selected state.

Troubleshooting

Issue	Check
ModuleNotFoundError	Activate .venv and rerun pip install -r ml/requirements.txt.
Data validation error	Confirm both CSV files are present under ml/handoff/for_hongyik/ and that the package layout has not changed.
Ollie unavailable	Confirm .env is in the Dashboard folder, GEMINI_API_KEY is valid, and the internet/API quota is available. The dashboard itself can still be assessed without Ollie.
Browser does not start	Copy the Streamlit local URL from the terminal into a browser.
Submission notes

The written report is available in docs/report/ as an editable DOCX and a PDF.
Submit the runnable dashboard folder, local data files, README.md, and the required static Dashboard.pdf in the competition archive.
Do not include virtual environments (.venv/venv), Python cache folders, editor settings, or prior ZIP files.
If a temporary Gemini key is supplied for judging, use a restricted temporary key only. Do not commit it to a public repository; revoke or replace it after judging.
