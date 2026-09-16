# 00 — Competition Brief Digest: DOSM Datathon 2026

**Phase:** 0 (repo check + brief)
**Author:** Data & AI track
**Digest date:** 2026-09-11 (team decisions recorded 2026-09-13)

> **⚠️ Read this first.** The briefing slides and the official booklet **disagree about the
> submission deadline**, and the booklet is right. The real deadline is
> **22 September 2026, 5:00 PM** — not 5 October. See §2.

## Source documents and precedence

| # | Source | Location | Language |
|---|---|---|---|
| S | `DOSM Datathon 2026 Briefing Slides.pdf` (18 pp.) | one level above the repo root | Bahasa Melayu |
| B | `DOSM-Datathon-2026-Booklet.pdf` (23 pp., the official handbook) | one level above the repo root | English |
| RA | `RUBRIK PERMARKAHAN DOSM DATATHON 2026 - PUSINGAN AWAL.docx` (preliminary round rubric) | one level above the repo root | Bahasa Melayu |
| RF | `RUBRIK PERMARKAHAN DOSM DATATHON 2026 - PUSINGAN AKHIR.docx` (final round rubric) | one level above the repo root | Bahasa Melayu |
| W | <https://datathon.dosm.gov.my/> — official site, fetched 2026-09-11 | — | English |

**Precedence used in this digest:** where B and W agree against S, B/W wins — the booklet is
the official handbook, the website is live, and the two corroborate each other. Every such
conflict is listed explicitly in §10 rather than silently resolved. Citations below are
`[B p.14]`, `[S p.8/s9]` (PDF page 8, printed slide number 9), `[RA]`, `[RF]`, `[W]`.

**Extraction method.** `pdftoppm`/poppler is not installed on this machine and no
third-party Python package was installed (that would have needed approval), so both PDFs and
both DOCX files were parsed with stdlib-only scripts written to the session scratchpad
(`pdftext5.py`: inflates content streams, expands `/ObjStm` containers, recurses into Form
XObjects — the booklet places all of its text there — and applies each font's `/ToUnicode`
CMap; `docxtext.py`: reads `word/document.xml` from the zip and preserves table structure).
These are scratchpad utilities and are deliberately **not** part of the `ml/` deliverable.
Passages from S and the two rubrics are my translation from Bahasa Melayu; B and W are
already English and are quoted directly.

---

## 1. Theme, challenge and dimensions — the domain is fixed

- **Theme:** "Transforming Society Through Data, Machine learning and Artificial
  Intelligence" `[S p.6/s7]`
- **Challenge:** "Leveraging ML and AI to develop innovative solutions for sustainable
  tourism industry in Malaysia" `[S p.6/s7, B p.6, W]`

**This settles the open question in our team scope: the domain is sustainable tourism in
Malaysia.** It is not a free choice of topic, and the repository name `malaysia_tourism_app`
is consistent with it. What remains open — and what Phases 1–4 exist to decide — is *which*
tourism question we attack and with which DOSM series.

The booklet frames it as transforming "official statistics into impactful solutions that
address real-world issues across the economic, social, environmental, and governance
dimensions of sustainable tourism" `[B p.3]`. The four dimensions a team may explore
`[S p.6/s7, W]`:

| Dimension | Slide description (translated) |
|---|---|
| **Economic** | Tourism's contribution to the local economy through tourist spending, accommodation occupancy rates, and local enterprise activity. |
| **Social** | Tourism's effect on communities — employment, resident satisfaction, cultural preservation. |
| **Environmental** | Tourism's environmental impact — pollution, waste, conservation of natural areas. |
| **Technology & Governance** | Use of technology and data for smarter, more efficient, more responsive tourism management. |

Competition objectives `[S p.3/s4]`: apply ML and AI to produce innovative solutions in
sustainable tourism; translate official DOSM statistics into strategic insight across the
four dimensions; foster critical thinking, collaboration and data-driven decision-making
among Malaysian students.

**SDGs** `[S p.7/s8]` — the slide shows four tiles by name and icon; **it does not print SDG
numbers**, so the numbers below are inferred from the standard SDG titles:

- Decent Work & Economic Growth (SDG 8) — inclusive, sustainable tourism economic growth.
- Industry, Innovation & Infrastructure (SDG 9) — data analytics and AI driving tourism infrastructure innovation.
- Sustainable Consumption & Marine Ecosystems (SDG 12 / 14) — prudent resource management, marine tourism environment protection.
- Responsible Consumption and Production (SDG 12) — sustainable consumption and production patterns.

Relevance to an SDG is a scored criterion in both rounds (`KDH4` in `[RA]`, `IMP5` in
`[RF]`), so whichever problem we pick in Phase 4 must have a named SDG attached to it.

---

## 2. Timeline — deadline is 22 September 2026, 5:00 PM

Confirmed identically by `[B p.4, p.5, p.8, p.14]` and `[W]`:

| Milestone | Date |
|---|---|
| Promotion begins | 3 August 2026 |
| Participation registration period | 10–28 August 2026 (closes 5:00 PM, 28 Aug) `[W]` |
| Opening Ceremony & Competition Briefing | 8 September 2026 |
| **Project development & submission period** | **8–22 September 2026** |
| **Hard deadline — upload to Google Drive** | **22 September 2026, 5:00 PM** `[B p.14]` |
| **Hard deadline — confirmation Google Form** | **22 September 2026, 11:59 PM** `[B p.14]` |
| Shortlisting / evaluation phase | 23 September – 2 October 2026 |
| Top 10 finalists announced | 5 October 2026 |
| Top 10 live pitching, Auditorium TAZA, Precinct 3, Putrajaya | 19 October 2026 |
| Closing ceremony & winners announced, Auditorium TAZA | 20 October 2026 |

> **The briefing slides are wrong here.** `[S p.5/s6]` labels 8–22 September as the
> *registration* period and 23 September – 5 October as the *development and submission*
> period. The booklet and the live website both contradict this, and the booklet states the
> submission window three separate times (`p.5` workflow, `p.8` "The submission period is
> from 8 to 22 September 2026", `p.14` with the 5:00 PM cut-off). My Phase-0 digest
> originally carried the slide version; it is corrected here.

**What this means for us.** Today is 11 September 2026. **There are 11 days left**, and the
whole team — model, dashboard, report, video — shares them. Late submissions "will not be
accepted or evaluated" `[B p.11]` and late or incomplete submissions "will result in
automatic disqualification" `[B p.8]`.

Submission mechanics `[B p.14]`: each team receives an email giving access to a specific
Google Drive folder for uploading all mandatory documents, available from 8 September to 22
September 2026. A Google Form must also be completed to confirm the upload. Contact for
access problems: `jkpenjuriandatathon@gmail.com`. General enquiries: `datathon@dosm.gov.my`
`[B p.23]`.

---

## 3. Required deliverables — three, not two

"Each team must develop and submit **three mandatory documents: a written report, a
dashboard, and a video presentation**" `[B p.14]`; restated at `[B p.5, p.8, p.11]`.

`[B p.11]` gives the formal list:

> a) A dashboard in PDF format, accompanied by the source file (e.g., `.pbix`, `.xlsm`, etc.)
> b) A recorded presentation video
> c) A project report using the template provided by the organisers

Once submitted, **no changes or resubmissions are allowed**; the final version is evaluated
as-is `[B p.12, S p.8/s9]`.

### 3.1 Dashboard `[B pp.16–18]`

- **Mandatory: a fully functional (workable) dashboard** the judges can open, explore and
  interact with. Free of technical errors; all filters, links and interactive features fully
  operational.
- Content: charts, graphs, **maps**, and key insights supporting the analysis and
  storytelling; visualisation clear, accurate, easy to interpret.
- Accepted formats, "including but not limited to": Power BI `.pbix`; interactive Excel
  `.xlsm`/`.xlsx` (formulas, macros and interactivity intact); Tableau `.twbx`; **"other
  interactive formats approved by the organizers"**.
- Screenshots in the report must be high-resolution and accurately reflect the real
  dashboard; they cannot replace the dashboard file.
- **Submission package** — one ZIP, `TeamName_Datathon2026_Dashboard.zip`, containing:
  1. `Dashboard.pdf` — static version, the final layout, for documentation
  2. `Dashboard.pbix` / `Dashboard.xlsx` / `Dashboard.twbx` — the interactive version
  3. `Data.csv` / `Data.xlsx` — clean/raw data used in the analysis, if applicable
  4. `README.txt` — must state the software name and version used, step-by-step instructions
     to open and navigate the dashboard, any plugins/add-ons required, and notes on
     limitations, assumptions or special considerations.
- **"Ensure that the submitted dashboard works as intended without external dependencies
  that cannot be accessed by the judges."** Incomplete or non-functional submissions may be
  disqualified or penalised `[B p.18]`.

### 3.2 Written report `[B p.15, S p.12/s13]`

Contents, in order: 1 Front Page (organiser's template, edited) · 2 Table of Contents ·
3 Introduction (background of the study, problem statement, objectives) · 4 Literature
Review · 5 Methodology (method of data analysis) · 6 Findings (results, including
information architecture / solution approach, visually appealing aids) · 7 Output
(dashboard) · 8 Conclusion · 9 References.

Times New Roman 12 · 1.5 spacing · justified · **maximum 25 pages, excluding front page,
table of contents and references** `[B p.15]` — *but the team follows the stricter slide
reading, 25 pages including them; see §10 #3* · PDF · `TeamName_Datathon2026_Report.pdf` ·
organiser's template required.

### 3.3 Video presentation `[B pp.19–20, S p.11/s12]`

MP4, **≤ 10 minutes**, named `TeamName_Datathon2026_Video.mp4`. Required flow: team and
project title (within 1 minute) · problem statement and objectives · data sources and
methodology · key findings and insights · **live demonstration of the interactive dashboard**
showing how it works and its key features · conclusion and potential impact or scalability.
Dashboard shown must be fully functional with interactive features demonstrated. Visuals,
text and audio clear and professional; avoid background noise; optimise compression.

---

## 4. Data rules

From `[B p.11]` and `[S p.8/s9]`:

- Participants **must use open and publicly accessible datasets**. Use of **fabricated,
  simulated or fictional data is strictly prohibited**. All data must be authentic, reliable
  and sourced from credible platforms.
- Recommended sources, "including but not limited to": **OpenDOSM**, **eStatistik**,
  **data.gov.my**, World Bank Open Data, Monthly Highlights and Statistics (Bank Negara
  Malaysia), UN Data.
- "**Extra mark(s) will be awarded for using Malaysian official data** (e.g. OpenDOSM,
  eStatistik, **StatsDW**), subject to judging criteria."

### 4.1 The rule the slides never mention

> "The raw data used must **originate exclusively from within Malaysia**. Data acquired from
> other countries may only be employed **to support a statement**." `[B p.14]`

This is a hard constraint and it is not in the briefing slides at all. Consequence for
Phase 1: **World Bank and UN Data cannot be a primary source for our model** — at most they
can back a sentence in the report. Our raw feature data has to be Malaysian: OpenDOSM first,
then data.gov.my / eStatistik / StatsDW. `[B p.14]` also names
`https://open.dosm.gov.my` explicitly as the dataset website.

### 4.2 Originality and third-party material `[B p.11, S p.8/s9]`

All submitted work must be the team's own. Third-party libraries, frameworks, pre-trained
models and openly licensed datasets **are allowed**, provided the team "clearly cite and list
each external resource in the Project Report **and reproducibility package**, and also
document how those resources were used and integrated". Copying, plagiarism or use of
proprietary IP without licence or attribution → disqualification.

The phrase "reproducibility package" matters to my track: `ml/data/raw/SOURCES.md`,
`ml/requirements.txt` and `ml/README.md` are exactly that, and they are also the raw material
for the report's References section.

### 4.3 Ethics `[B p.12, S p.9/s10]`

No personally identifiable or confidential data without proper authorisation; misuse of
sensitive information → disqualification. Personal data shared with organisers is stored
securely and used only per competition rules.

---

## 5. Judging rubrics — full criteria and weights

Both rounds total 100%. Each criterion is scored 0–10 on the scale:
**0–2 Weak · 3–4 Adequate · 5–6 Good · 7–8 Very Good · 9–10 Excellent** `[RA, RF]`.
Each component's 5 sub-criteria are scored /10, giving /50 overall, then weighted to /100.

### 5.1 Preliminary round (online) `[RA]`

| Component | Weight | Sub-criteria (translated) |
|---|---|---|
| **C1. Method / Methodology** | **15%** | KDH1 problem statement clear, relevant and significant · KDH2 scope focused and aligned with the competition objectives · KDH3 analysis method appropriate to the problem and the data · KDH4 project relevant to the related SDG · KDH5 analysis explanation logical, easy to follow, evidence-based |
| **C2. Data Quality & Analysis** | **25%** | QLT1 data from official and valid sources · QLT2 data accurate, current and relevant to the problem statement · **QLT3 ability to combine multiple types of dataset (structured, unstructured, geospatial, etc.)** · **QLT4 data integration produces new and valuable insight** · QLT5 data handled carefully without manipulation that compromises the integrity of the results |
| **C3. Dashboard / Final Output Presentation** | **20%** | PRS1 structure clear, organised, user-friendly · PRS2 product works well without technical issues (interactive, responsive) · PRS3 data displayed accurately and relevantly, supporting the key findings · PRS4 design neat, professional, visually attractive · PRS5 product is original work with creative and innovative elements |
| **C4. Impact & Commercial Potential** | **25%** | KOM1 potential real-world application (industry, government, society) · KOM2 commercial added value or marketability · KOM3 benefits society, solves a real social or economic issue · KOM4 potential for future development · **KOM5 team can clearly explain how the product would be implemented (implementation model)** |
| **C5. Creativity** | **15%** | KRE1 creativity in the use of tools and analytical approach · **KRE2 innovation in the application of technology, data science, AI or geospatial** · KRE3 ideas and concepts clear, structured and unique · KRE4 project presentation engaging, effective, impactful · KRE5 contains additional elements giving a "wow factor" |

Outcome recorded as: Qualified for Final / Reserve / Not Qualified.

### 5.2 Final round (live pitching) `[RF]`

| Component | Weight | Notes |
|---|---|---|
| **C1. Presentation & Command of the Project** | **20%** | PJT1–PJT5; PJT4 feeds the *Pitching Excellence Award*, **PJT5 (answering the panel accurately, convincingly, evidence-based) is the sole criterion for the *Critical Thinking & Defence Award*** |
| **C2. Product / Dashboard Demonstration** | **25%** | DEM1–DEM5: runs smoothly live, navigation/interactivity/UX clear and intuitive, visualisation supports the key findings, layout professional and fit for real use, demonstrates relevant functionality adding value for the target user |
| **C3. Quality of Analysis & Justification** | **20%** | ANL1 analysis accurate and aligned with the problem statement · **ANL2 appropriate choice of analysis method and statistical model** · ANL3 key findings supported by data, evidence and strong argument · ANL4 team can clearly explain the rationale of its analytical decisions · ANL5 analysis shows critical thinking and produces meaningful insight |
| **C4. Impact, Effectiveness & Feasibility** | **25%** | IMP1–IMP5: real-environment application potential, solves a real social/economic/operational issue, implementation proposal + target users + organisational benefit well explained, scalable/integrable, aligned with the theme and the relevant SDG |
| **C5. Creativity & Innovation** | **10%** | INV1–INV4 plus **INV5 "use of technology such as AI, machine learning, geospatial or automation that is innovative and relevant" — the sole criterion for the *AI-Driven Innovation Award*** |

### 5.3 What the rubric tells the Data & AI track

Reading the weights rather than the vibe:

1. **C2 Data Quality & Analysis (25%) is the single biggest preliminary component, and two
   of its five sub-criteria reward dataset *integration* — explicitly naming geospatial
   data and "new and valuable insight" from combining sources.** This is the strongest
   steer I have for Phase 1: shortlist datasets that genuinely join (state × month, say),
   and prefer a shortlist that includes a geospatial/state-level dimension over one deep
   national time series.
2. **C4 Impact & Commercial Potential (25%) turns on KOM5 — being able to explain the
   implementation model.** That is a documentation deliverable, not a modelling one: the
   Phase 10 `API_CONTRACT.md` and the "who acts on this" field in each Phase 4 candidate are
   what earn those marks.
3. **The model's own accuracy is scored only indirectly** — via ANL2 ("appropriate choice of
   analysis method and statistical model") and KDH3/KDH5 in the preliminary round. There are
   no marks for squeezing out another 2% RMSE. There *are* marks for the method being
   appropriate, the reasoning being followable, and the results being honestly evidenced.
   That validates the Phase 6→7→9 structure (baseline → comparison → untouched holdout):
   it is the cheapest way to be able to defend every number under Q&A (PJT5, ANL3, ANL4).
4. **`INV5` is the entire AI-Driven Innovation Award**, and C5 is only 10% of the final
   score. So the AI work wins a special award and supports C2/C3, but it will not carry the
   main score by itself. A strong model attached to a weak dashboard scores badly; a decent
   model attached to a dashboard with a clear implementation story scores well.
5. **Nothing in either rubric rewards model complexity.** Given 11 days, the right call is a
   defensible model on well-integrated data, delivered early enough for HongYik to build
   around it.

---

## 6. Eligibility and team rules `[B p.10, S p.7/s8]`

- Diploma and undergraduate students from Malaysian IPTA/IPTS; all participants must be
  Malaysian citizens, actively enrolled at the time of the competition.
- **Each team = 4 students from the same university + 1 academic advisor.** Our team is 4, so
  an academic advisor is required.
- The advisor provides guidance and advisory support only, and must not be directly involved
  in product development.
- No team changes after the registration deadline except with organiser approval; the Top 10
  must keep identical membership between rounds `[B p.6]`.
- Registration via the official DOSM Datathon 2026 website; **no entry fee** `[B p.10]`.
- Mandatory participation in the official WhatsApp community "Participants DOSM Datathon
  2026" — all official announcements go through it `[B p.10]`.
- Mandatory attendance and active involvement in every organised session.

---

## 7. Technical constraints

- Participants may use **any hardware and software of their choice**, but must provide and
  use their own ICT equipment `[B p.11, S p.8/s9]`. → **No restriction on Python or
  open-source tooling**; our Python-only, free/open-source-only constraint costs us nothing.
- Submissions must be free of viruses, trojans, spyware, or any code that could damage or
  disrupt systems `[B p.12]`.
- The dashboard must remain accessible until evaluation is complete, and must work without
  external dependencies the judges cannot access `[B p.12, p.18]`.
- IP remains with the team; organisers hold non-exclusive rights to showcase, publish or
  exhibit the project with proper credit `[B p.12]`.
- Judges' decisions are final and cannot be appealed `[B p.13]`.
- E-certificates only for participants who submit on time `[B p.13]`.
- Live pitching `[B p.21]`: own device, fully charged, HDMI-compatible; 5 minutes' prep;
  **maximum 2 presenters per team**; 10-minute pitch (bell at 8 minutes, double bell at 10)
  + 5-minute Q&A.

## 8. Prizes `[B p.22]`

1st RM3,500 · 2nd RM2,500 · 3rd RM1,500 · 4th–10th RM300 per team.
Special awards: **Pitching Excellence** (individual), **Critical Thinking & Defence** (team),
**AI-Driven Innovation** (team).

---

## 9. What this means for the Data & AI track

My own analysis, not statements from the brief:

1. **Domain fixed, question open.** Phase 1's shortlist must be Malaysian tourism data
   mapping onto at least one of the four dimensions, and Phase 4's three candidates should
   ideally not all sit in the same dimension.
2. **Malaysian raw data only** (§4.1). OpenDOSM is both the highest-scoring source (extra
   marks) and the safest one. Any non-Malaysian series is confined to a supporting sentence
   in YiHui's report, never a model feature.
3. **Favour integration over depth.** C2's QLT3/QLT4 (25% component) reward combining
   dataset types including geospatial. A shortlist that joins, say, tourism demand × state ×
   accommodation × employment beats one long national series, even if the latter models more
   cleanly.
4. **11 days, shared.** My Phases 1–10 have to finish early enough for HongYik to build the
   dashboard around the model and for YiHui to write 25 pages from `FINDINGS.md`. This
   argues for a small number of clean DOSM series and a deliberately unambitious modelling
   plan.
5. **Deliver the model as data, not just as a service.** `[B p.18]`'s "no external
   dependencies that cannot be accessed by the judges" plus the ZIP structure at `[B p.17]`
   (which expects `Data.csv` inside the package) means `sample_predictions.csv` is not a
   nice-to-have for mocking — it may be the form in which my model actually reaches the
   judges. I will size and document it accordingly in Phase 10.
6. **Dashboard format is a team-level risk I should flag, not solve.** `[B pp.16–17]` names
   Power BI, Tableau and interactive Excel, with anything else needing organiser approval,
   and requires a `Dashboard.pdf` plus a source file in a ZIP. A Flutter app or a custom web
   dashboard is "other interactive formats approved by the organizers" — it is not
   automatically accepted. This is HongYik's and JiaXuan's call, not mine, but they should
   confirm it with the organisers early rather than discover it on 22 September.
7. **`README.txt` for the dashboard ZIP** `[B p.17]` overlaps heavily with my `ml/README.md`
   and `API_CONTRACT.md`. I can hand HongYik most of its content.

---

## 10. Conflicts between sources, and open questions

| # | Item | Status |
|---|---|---|
| 1 | **Submission deadline** | **Resolved against the slides.** S says the development/submission window is 23 Sep – 5 Oct; B (three times) and W both say 8–22 Sep with a 5:00 PM cut-off on 22 September 2026. **Using 22 September 2026.** |
| 2 | **Is the video mandatory?** | **Resolved: yes.** S's mandatory list `[S p.8/s9]` names only the dashboard and report, but B states "three mandatory documents" in four places. |
| 3 | **Report page limit: 25 pages including or excluding front matter?** | S says "including Front page, Table of contents and References"; B says "excluding the front page, table of contents, and references". **Decided 2026-09-13: the team follows the stricter reading — 25 pages *including* front page, table of contents and references.** |
| 4 | **Preliminary rubric mentions a "poster infografik"** | `[RA]`'s preamble says assessment is based on "poster infografik, dashboard, project presentation and implementation potential", where `[S p.14/s15]` says "project report, dashboard, …". No infographic poster appears in any deliverable list in B or S. Most likely a leftover from a reused rubric template — **but worth one email to the organisers**, because if a poster is genuinely required, nobody on the team is building one. **OPEN — YiYu to confirm with the team.** |
| 5 | **Entry fee** | `[B p.6]` refers to "completion of the registration and payment process"; `[B p.10]` says "No entry fee required", as does `[S p.7/s8]`. Assume no fee. |
| 6 | **Is DOSM data mandatory?** | **No** — recommended and bonus-scoring `[B p.11]`. But §4.1's Malaysia-only rule makes OpenDOSM the obvious primary source regardless. |
| 7 | **Report template** | Three OneDrive links appear in the slides; two were the rubrics (now downloaded). The third is the written-report template `[B p.15]` and has **not** been downloaded. YiHui needs it. **OPEN — YiYu to confirm with the team.** |
| 8 | **Opening-ceremony decks** | `[W]` lists three further decks — on OpenDOSM, Portal DOSM, and **Tourism Statistics** — not yet downloaded. The Tourism Statistics one is likely to be directly useful for the Phase 1 dataset shortlist. |
| 9 | **SDG numbers** | Inferred, not printed `[S p.7/s8]`. |
| 10 | **Repo / PDF location** | Not a brief issue: the team scope describes the PDF as being in the project root, but the four source documents actually sit one directory *above* the git repository root. Noting it so nobody tries to commit them. |

---

## 11. Provenance

Every statement in §§1–8 is a quotation or translation of the source cited beside it. No
date, weight, rule or figure in this document was inferred; anything not present in a source
is marked as such in §10. §9 is explicitly my own analysis and is labelled as such. The
rubric weights in §5 are transcribed from the two `RINGKASAN PEMARKAHAN` summary tables and
cross-checked against the per-component `Pemberat` headings, which agree.
