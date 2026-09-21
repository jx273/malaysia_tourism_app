LESTARILENS - MALAYSIA TOURISM INTELLIGENCE DASHBOARD
DOSM DATATHON 2026
Team: 404 NOT FOUND

======================================================================
1. SOFTWARE AND VERSION
======================================================================

Dashboard framework: Streamlit 1.64.0
Programming language: Python 3.14.7
AI assistant model: Gemini 3.1 Flash Lite
Recommended browsers: Google Chrome, Microsoft Edge, or Safari
Supported operating systems: Windows and macOS
Display theme: Light theme only

The deterministic dashboard, local CSV data, charts, machine-learning
outputs, Scenario Lab, and Evidence page run locally. Internet access and
a valid Gemini API key are required only for the optional Ollie assistant.

======================================================================
2. DASHBOARD PURPOSE
======================================================================

LestariLens uses official Malaysian tourism and socioeconomic data to
compare observed domestic visitor patterns with a structural
machine-learning benchmark. It supports evidence-based tourism planning
through five sections:

1. Overview
2. Visitor flows
3. Sustainability
4. Scenario lab
5. Evidence

The Tourism Opportunity Gap compares actual visitor share with
model-expected visitor share. It is a structural benchmark, not a future
forecast and not a causal estimate.

======================================================================
3. REQUIRED PROJECT STRUCTURE
======================================================================

Dashboard/
|-- assets/
|   `-- images/
|       `-- tiger_sheet.png
|-- backend/
|   |-- app.py
|   `-- ai_service.py
|-- ml/
|   `-- handoff/
|       `-- for_hongyik/
|           |-- sample_predictions.csv
|           `-- state_features.csv
|-- .streamlit/
|   `-- config.toml
|-- .env
|-- .env.example
|-- .gitignore
|-- README.txt
`-- requirements.txt

Do not move the CSV or tiger sprite files. The dashboard loads them from
the relative paths shown above.

======================================================================
4. WINDOWS INSTALLATION AND STARTUP
======================================================================

1. Extract the submitted ZIP file.
2. Open PowerShell inside the Dashboard folder.
3. Run the following commands:

py -m venv .venv
.\.venv\Scripts\Activate.ps1
py -m pip install -r requirements.txt
py -m streamlit run backend/app.py

4. Open the Local URL printed in PowerShell. The usual address is:

http://localhost:8501

If PowerShell blocks virtual-environment activation, run this command for
the current PowerShell session and activate the environment again:

Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass

======================================================================
5. MACOS INSTALLATION AND STARTUP
======================================================================

1. Extract the submitted ZIP file.
2. Open Terminal inside the Dashboard folder.
3. Run the following commands:

python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
python -m streamlit run backend/app.py

4. Open the Local URL printed in Terminal. The usual address is:

http://localhost:8501

======================================================================
6. NAVIGATION GUIDE
======================================================================

Use the left sidebar to move between the five dashboard sections. Use the
Global Year Filter to select 2017, 2018, 2019, 2023, 2024, or 2025.

Overview:
- Select Malaysia or an individual state.
- Review visitor indicators, Tourism Opportunity Gap, evidence briefs,
  historical state trends, and the 2025 national spending mix.

Visitor flows:
- Compare state visitor trajectories across the available observation
  years.
- Lines are intentionally disconnected between 2019 and 2023 because
  observations for 2020-2022 are unavailable.

Sustainability:
- Compare economic strength, accommodation capacity, and visitor volume.
- Hover over a bubble to view the state represented by that point.

Scenario lab:
- Select different source and target states.
- Adjust the illustrative reallocation slider.
- The calculation preserves the national visitor total.
- The result is an arithmetic scenario, not a forecast or policy outcome.

Evidence:
- Review the methodology, limitations, historical data, and model output.
- 2017-2019 and 2023 are model-training years.
- 2024-2025 are untouched holdout years.

Ollie assistant:
- Type a question about the current page or select a suggested question.
- Select the microphone button for optional voice input.
- Stop recording, review the transcript, and use the send button.
- Ollie uses validated page data and does not analyse screenshots.
- The deterministic dashboard remains functional if Ollie is unavailable.

======================================================================
7. DATA COVERAGE AND SOURCES
======================================================================

Observed years: 2017-2019 and 2023-2025
Unavailable years: 2020-2022

Primary source: Department of Statistics Malaysia (DOSM)

The submitted CSV files are stored locally under:

ml/handoff/for_hongyik/

No external database or API is needed for the dashboard data, local ML
outputs, charts, Evidence page, or Scenario Lab.

======================================================================
8. OPTIONAL GEMINI CONFIGURATION
======================================================================

Ollie requires internet access and these variables in the project-root
.env file:

GEMINI_API_KEY=replace_with_a_valid_key
GEMINI_MODEL=gemini-3.1-flash-lite

The private judging package may contain a temporary evaluation key. The key
must not be committed to a public repository. If the key is missing, invalid,
rate-limited, or inaccessible, the main dashboard continues to operate and
only Ollie becomes unavailable.

Microphone input is optional. The browser asks for microphone permission
only after voice input is selected. Typed questions remain available when
permission is denied or the browser does not support recording.

======================================================================
9. LIMITATIONS AND SPECIAL CONSIDERATIONS
======================================================================

- The interface is designed and tested for the Light theme.
- No data is available for 2020-2022.
- The 2025 national spending-category breakdown is not applied to other
  years or individual states.
- Opportunity Gap is a structural benchmark, not a forecast.
- The model does not establish the cause of an observed gap.
- Results for Perlis and W.P. Putrajaya require additional reliability
  caution.
- Scenario Lab performs transparent arithmetic redistribution and does not
  estimate behaviour, cost, feasibility, or policy impact.
- Ollie is an optional network-connected assistant. Local ML outputs and all
  required analytical pages are available without Ollie.

======================================================================
10. TROUBLESHOOTING
======================================================================

Dashboard does not start:
- Confirm that the virtual environment is active.
- Run: python -m pip install -r requirements.txt
- Run: python -m py_compile backend/app.py backend/ai_service.py

Data-validation error:
- Confirm that both CSV files remain in ml/handoff/for_hongyik/.
- Do not rename or edit their required columns.

Ollie is unavailable:
- Confirm that the computer has internet access.
- Confirm that GEMINI_API_KEY is present and valid.
- Restart Streamlit after changing .env.

Recent changes do not appear:
- Stop Streamlit with Ctrl+C.
- Run: python -m streamlit cache clear
- Start the dashboard again.
- Refresh without browser cache using Ctrl+F5 on Windows or
  Command+Shift+R on macOS.

Microphone is unavailable:
- Allow microphone permission for localhost in the browser.
- Use typed input if microphone access is denied.

======================================================================
11. SUBMISSION PACKAGE
======================================================================

Recommended archive name:

404NOTFOUND_Datathon2026_Dashboard.zip

Recommended archive structure:

404NOTFOUND_Datathon2026_Dashboard.zip
|-- Dashboard.pdf
|-- Dashboard/
|   |-- backend/
|   |-- assets/
|   |-- ml/
|   |-- .streamlit/
|   |-- .env
|   |-- .env.example
|   |-- .gitignore
|   `-- requirements.txt
`-- README.txt

Dashboard.pdf is the static documentation version. The Dashboard folder is
the fully interactive Streamlit version.

The submission must not contain .venv, .git, __pycache__, .DS_Store,
temporary logs, editor settings, or old ZIP files.

