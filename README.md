# 📉 Creative Fatigue & Algorithm Decay Monitor

An AI sub-agent for Acadia.io's Morning Account Checks ecosystem. Detects fatigued paid social creatives by comparing the most recent N-day window against the immediately preceding N-day window of equal length.

An ad is flagged **only when all three** of these conditions are true simultaneously:

1. **Frequency** increases by more than X% (audience saturation)
2. **CTR** decreases by more than Y% (audience disengagement)
3. **CPA** increases by more than Z% (algorithm penalty)

A minimum-impressions QC filter (default 1,000) eliminates false positives from low-volume noise.

---

## Quick Start (macOS)

```bash
# 1. Create and activate a virtual environment
python3 -m venv .venv
source .venv/bin/activate

# 2. Install dependencies
pip install -r requirements.txt

# 3. Run the app
streamlit run fatigue_monitor.py
```

Open `http://localhost:8501`, click **Generate Mock Dataset (60 days)**, and the two seeded fatigued ads will flag with default thresholds. Detailed setup notes for macOS are in [`docs/SETUP_MACOS.md`](docs/SETUP_MACOS.md).

---

## Project Structure

```
creative-fatigue-monitor/
├── README.md                      # You are here
├── requirements.txt               # Python dependencies
├── .gitignore                     # Standard Python gitignore (excludes secrets, data)
├── fatigue_monitor.py             # ⭐ Main Streamlit app + core detection logic
├── pipeline_fatigue.py            # Headless Google Sheets integration
├── generate_test_data.py          # Regenerable test data builder
├── test_data.csv                  # Ready-to-upload validation dataset (520 rows)
├── PROJECT_LOG.md                 # Development history and key decisions
└── docs/
    ├── SETUP_MACOS.md             # macOS install & run guide
    ├── ARCHITECTURE.md            # Technical architecture & design rationale
    ├── TEST_DATA.md               # Test dataset guide and CSV schema
    ├── FIELD_MAPPING.md           # How to adapt to your Funnel.io export
    ├── DEMO_SCRIPT.md             # 2-minute hackathon demo walkthrough
    ├── HACKATHON_SUBMISSION.md    # AI Track 2026 form answers (paste-ready)
    └── GEMINI_HANDOFF.md          # Context brief for Gemini to continue docs
```

---

## What's in the Core

The detection logic lives in `detect_creative_fatigue()` inside `fatigue_monitor.py`. It is **UI-agnostic** — you can import it directly into any pipeline:

```python
from fatigue_monitor import detect_creative_fatigue

flagged_df = detect_creative_fatigue(
    df=your_dataframe,
    window_days=7,
    freq_increase_pct=15,
    ctr_decrease_pct=20,
    cpa_increase_pct=25,
    min_impressions=1000,
    column_map=your_column_map,
)
```

Returns a pandas DataFrame of flagged ads with all delta percentages, sorted by CPA spike severity.

---

## Deployment Options

| Mode | Use Case | Entry Point |
|---|---|---|
| **Local Streamlit** | Demo, interactive QA, account-manager workflow | `streamlit run fatigue_monitor.py` |
| **Streamlit Cloud** | Shared link for the team | Deploy at [share.streamlit.io](https://share.streamlit.io) |
| **Headless pipeline** | Scheduled 6 AM Morning Check, Sheets output | `python pipeline_fatigue.py` (cron / Cloud Scheduler) |
| **Embedded in agent** | Sub-agent inside Morning Account Checks orchestrator | Import `detect_creative_fatigue()` |

---

## Roadmap

See [`PROJECT_LOG.md`](PROJECT_LOG.md) for full development history and [`docs/ARCHITECTURE.md`](docs/ARCHITECTURE.md) for technical rationale. Planned extensions:

- Per-client threshold profiles stored in a config Sheet
- Slack digest output: top 5 fatigued ads per account, posted at 6 AM
- Automated pause recommendations with confidence scores
- Cross-account benchmarking
- Backtest mode against historical fatigue events

---

## Built For

**Acadia.io — AI Track 2026 Hackathon.** See [`docs/HACKATHON_SUBMISSION.md`](docs/HACKATHON_SUBMISSION.md) for the submission package.
