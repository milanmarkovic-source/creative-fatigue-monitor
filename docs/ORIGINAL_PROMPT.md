# Original Design Prompt

This is the verbatim prompt that initiated the Creative Fatigue & Algorithm Decay Monitor project. It captures the original design intent, scope, and constraints that shaped every subsequent decision in the codebase.

Preserved here so that future contributors — human or AI — can understand the *why* behind the architecture without having to reverse-engineer it from the code.

---

## Context

- **Date issued:** May 2026
- **Author:** Milan Markovic, Senior Paid Media Manager at Acadia.io
- **Issued to:** Claude (Anthropic), acting as Expert Python Developer + Streamlit UI Designer
- **Purpose:** Hackathon submission (Acadia AI Track 2026) and production-bound sub-agent for the Morning Account Checks ecosystem

---

## The Prompt (verbatim)

```
ROLE: You are an Expert Python Developer, Paid Media Automation Specialist,
and Streamlit UI Designer specializing in algorithmic data analysis and
API-to-Google-Sheets pipelines.

CONTEXT:
* Audience: Senior Paid Media Manager at an agency (Acadia.io) and an AI
  Hackathon judging panel.
* Situation: We are building an automated AI agent data pipeline to
  streamline our Morning Account Checks. A critical sub-agent in this
  ecosystem is the "Creative Fatigue & Algorithm Decay Monitor."
* Goal: Create a reliable, automated Python script that scans ad-level
  and asset-level metrics to pinpoint exact moments of creative fatigue.
  It must be highly adaptable so any account manager can use it across
  different clients, and it needs a simple Streamlit UI so hackathon
  judges can interact with it during the demo.
* Constraints: Must avoid flagging false positives due to low data volume
  and execute efficiently.

TASK: Generate a multi-variable Python filtering script, wrapped in a
Streamlit web app, that identifies fatigued active ads by comparing a
current time window against the immediately preceding time window of the
same length (e.g., Last 7 Days vs. Previous 7 Days).

Must include:

1. The 3-Part Statistical Signature: The logic must flag ads where:
   Ad Frequency increases by > `X`%, AND CTR decreases by > `Y`%,
   AND CPA spikes by > `Z`%.

2. Dynamic Time Windows: The script must handle data across selected
   timeframes. Users must be able to define `WINDOW_DAYS` (typically 7,
   14, or 30). The math will calculate the trend matrix by comparing the
   current `WINDOW_DAYS` period against the previous `WINDOW_DAYS` period.

3. Strict Quality Control (QC): Hard-code a filter that ignores any ads
   with fewer than `MIN_IMPRESSIONS` (default to 1,000) in the current
   period. Analyzing fatigue on low-volume ads leads to inaccurate swings.

4. Universal Configuration & Mapping: Include a configuration dictionary
   so users can map their specific input CSV column names (e.g., mapping
   'Cost Per Action' to 'CPA' based on their specific Funnel.io export).

5. Test Data Generator: Include a separate helper function (accessible
   via a button in the UI) that generates a mock dataset spanning at
   least 60 days. It should contain a mix of healthy ads, low-volume ads,
   and fatigued ads to test the logic immediately.

6. Streamlit UI: Wrap the tool in a clean Streamlit interface. Include
   an interactive sidebar with:
   * A dropdown to select `WINDOW_DAYS` (7, 14, or 30).
   * Sliders or number inputs for the `X`, `Y`, `Z` percentage thresholds.
   * A number input for the `MIN_IMPRESSIONS` limit.
   * A main display area showing the flagged "Fatigued Ads" in a clean
     dataframe.

FORMAT:
* Length: Concise, clean, heavily commented code block + a brief
  implementation guide.
* Structure:
   * Section 1: The Python/Streamlit Code (all in one executable file).
   * Section 2: Instructions on how to install requirements and run the
     Streamlit app locally.
   * Section 3: Integration instructions for bypassing the UI and
     plugging the core logic directly into a Google Sheets pipeline in
     the future.
* Tone: Highly technical, precise, and structured.
* Output type: Code snippet and Implementation Document.
```

---

## How the Final Build Maps to the Prompt

Every requirement in the prompt has a corresponding artifact in the repo. This table is the audit trail.

| Prompt Requirement | Where It Lives | Notes |
|---|---|---|
| 3-Part Statistical Signature | `detect_creative_fatigue()` in `fatigue_monitor.py` — the AND filter at the end of the function | Implemented as a strict conjunction, not a score, for explainability |
| Dynamic Time Windows (7/14/30) | Sidebar `st.selectbox` + `window_days` parameter | Reference date defaults to `max(date)` in the input data |
| Strict QC (`MIN_IMPRESSIONS` ≥ 1,000) | `merged[merged["impressions_curr"] >= min_impressions]` filter | Applied *before* threshold checks to suppress low-volume noise |
| Universal Configuration & Mapping | `DEFAULT_COLUMN_MAP` dictionary + editable sidebar fields | Three usage pathways documented in `docs/FIELD_MAPPING.md` |
| Test Data Generator | `generate_mock_data()` in `fatigue_monitor.py` (button-triggered) + standalone `generate_test_data.py` + committed `test_data.csv` | Validation expanded beyond prompt minimum: 65 days, 8 archetypes, mathematically proven to flag at extreme slider values |
| Streamlit UI | `run_app()` in `fatigue_monitor.py` | Sidebar contains all four required controls; main pane shows window dates, flag count, ranked dataframe, CSV download |
| Section 1 (code) | `fatigue_monitor.py` | All-in-one executable file |
| Section 2 (local install/run) | `docs/SETUP_MACOS.md` | macOS-specific, tested |
| Section 3 (Sheets pipeline integration) | `pipeline_fatigue.py` | UI-agnostic core function is importable with zero Streamlit dependency |

---

## Design Decisions That Went Beyond the Prompt

The prompt set the requirements; these decisions filled in the spaces between them. Each is rationalized in `PROJECT_LOG.md`:

- **AND conjunction over scoring** — chosen for auditability and account-manager trust
- **Back-to-back equal-length windows** — chosen to isolate the change signal from seasonality
- **UI-agnostic core function** — chosen so the same code powers both the demo and the production pipeline
- **Seeded mock data with named archetypes** — chosen so the demo is reproducible and acts as a regression test
- **Committed `test_data.csv` validated end-to-end** — added post-hackathon-submission planning to give judges and teammates a concrete artifact to verify the math against

---

## For Future Iterations

When extending this tool, the prompt's constraints still apply:
- **Adaptability across clients** — any new feature must work with the column mapping system
- **False positive resistance** — any new signal must come with a corresponding QC mechanism
- **Account-manager friendly** — non-technical users must be able to operate it without code changes
- **Pipeline-compatible** — the core logic stays UI-agnostic

If you're reading this as you plan v1.1 or beyond, hold new features to these standards.
