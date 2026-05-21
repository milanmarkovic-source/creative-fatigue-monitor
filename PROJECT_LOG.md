# Project Development Log

A chronological record of what was built, decisions made, and why. Useful for future development, onboarding teammates, and post-hackathon iteration.

---

## Session 1 — Initial Build

**Date:** May 2026
**Builder:** Milan Markovic (Acadia.io)

### Objective
Build a deterministic AI sub-agent for the Morning Account Checks ecosystem that automates creative fatigue detection across paid social ads. Must be portable across clients, demo-ready for hackathon judges, and pipeline-ready for production.

### What Was Built

1. **`fatigue_monitor.py`** — single-file Streamlit app containing:
   - `detect_creative_fatigue()` — core UI-agnostic detection function
   - `generate_mock_data()` — 60-day synthetic dataset with three ad archetypes
   - `run_app()` — Streamlit UI wrapper
   - `_apply_column_map()` and `_aggregate_window()` — internal helpers

2. **`pipeline_fatigue.py`** — headless Google Sheets integration example

3. **macOS setup validated** — app runs locally on `http://localhost:8501`, mock dataset flags exactly the seeded fatigued ads with default thresholds.

### Key Design Decisions

**Decision 1: Triple-condition AND filter (not OR, not scoring).**
A scoring system or any single-condition trigger would produce too many false positives. The fatigue *signature* is the simultaneity — frequency, CTR, and CPA all moving wrong at the same time. A simple `AND` filter is deterministic, explainable to account managers, and resistant to gaming.

**Decision 2: Back-to-back equal-length windows.**
Comparing "last 7 days vs. previous 7 days" (rather than "last 7 days vs. last 30 days") isolates the change signal. Mismatched windows introduce confounding seasonality and weekday effects.

**Decision 3: Minimum-impressions hard floor (1,000 default).**
Low-volume ads produce massive relative swings — a 5-impression jump from 100 to 105 is a 5% move; from 5 to 10 is 100%. Without a floor, the detector becomes a noise generator. The 1,000 default is a defensible starting point and a knob the user can tune.

**Decision 4: Column mapping at runtime, not hard-coded.**
Different agencies and even different clients within one agency export Funnel.io data with different column names. Forcing a fixed schema would block portability. The `DEFAULT_COLUMN_MAP` dictionary + editable sidebar fields lets any account manager adapt the tool in seconds.

**Decision 5: UI-agnostic core function.**
`detect_creative_fatigue()` takes a DataFrame in, returns a DataFrame out, and has zero Streamlit imports inside it. This means the same logic powers both the demo UI and the production headless pipeline. One source of truth.

**Decision 6: Seeded mock data generator with explicit archetypes.**
The mock data isn't random — it has three named ad types (`Healthy_*`, `LowVol_*`, `Fatigued_*`) with deliberately engineered metric patterns. This makes the demo reproducible (judges see the same result every time) and acts as a built-in regression test.

**Decision 7: `tool` level shipped, not `agent`.**
The hackathon form asks what "level" you shipped. I picked `tool` because that's what was honestly delivered — an executable Python tool with a UI. The narrative positions it as a *future sub-agent* in the Morning Checks ecosystem, but the orchestration layer isn't built yet. Better to under-claim and over-deliver in the demo.

### Validation

Default thresholds (15% / 20% / 25% / 1,000 min impressions) against the seeded mock dataset:
- ✅ `Fatigued_UGC_F` and `Fatigued_Promo_G` flag correctly
- ✅ `LowVol_Test_D` and `LowVol_DarkPost_E` are excluded by QC floor
- ✅ `Healthy_Carousel_A`, `Healthy_Video_B`, `Healthy_StaticImage_C` stay quiet

### Open Questions / Known Limitations

- **Reach summing.** Aggregating daily reach across a window overstates true unique reach. The frequency calculation is therefore an approximation. For the *window-over-window relative delta*, this is acceptable — both windows use the same approximation. For absolute frequency reporting, this would need to be addressed (use platform-native frequency or unique reach if available in the export).
- **No statistical significance test.** The thresholds are deterministic, not probabilistic. A future iteration could layer a confidence interval check on top.
- **Single platform assumption.** The schema assumes a flat ad-level export. Multi-platform aggregation (Meta + TikTok + LinkedIn under one ad name) is out of scope for v1.

---

## Future Sessions — Roadmap

### Next Up (v1.1)
- [ ] Per-client threshold profiles loaded from a config Sheet keyed by account ID
- [ ] Slack output integration (post top 5 fatigued ads per account to `#paid-media-alerts` at 6 AM)
- [ ] Add a "severity score" column (combined magnitude of all three deltas) for prioritization

### Later (v1.2+)
- [ ] Multi-account orchestration loop with one entry-point script
- [ ] Backtest mode — replay historical data and surface known fatigue events to calibrate thresholds
- [ ] Confidence intervals on each delta to suppress borderline flags
- [ ] Automated pause recommendations with rationale strings
- [ ] Cross-account pattern detection (which creative formats fatigue fastest, by vertical)

### Maybe (v2.0)
- [ ] Integration with the parent Morning Account Checks agent orchestrator
- [ ] LLM-generated explanation text per flagged ad ("This carousel ad is showing classic UGC fatigue — frequency 2.8x in last 7 days, CTR halved, CPA up 60%")
- [ ] Per-platform schema adapters (Meta, TikTok, LinkedIn, Pinterest) auto-detected from CSV structure
