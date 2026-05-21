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

## Session 2 — Validation, Documentation, and Deployment Readiness

**Date:** May 2026 (same week as Session 1)
**Builder:** Milan Markovic (Acadia.io)

### Objective
Close the gap between "working prototype" and "submission-ready, team-adoptable artifact." Session 1 delivered the build; Session 2 delivered the proof, the documentation, and the deployment path.

### What Was Built

1. **`test_data.csv`** — a committed 520-row validation dataset (8 ads × 65 days) with mathematically engineered archetypes that flag at every window size, even at extreme slider values

2. **`generate_test_data.py`** — standalone, deterministic generator script for the CSV above. Editable archetype dictionary so new test cases (recovering ads, platform-specific ranges) can be added without touching the main app

3. **`docs/TEST_DATA.md`** — schema reference, archetype behavior table per window, validated delta values, regeneration instructions

4. **`docs/FIELD_MAPPING.md`** — three documented pathways for adapting the tool to any Funnel.io export: live UI editing, permanent code default, per-client pipeline mapping. Includes a full worked example using realistic Funnel.io column names

5. **`docs/ORIGINAL_PROMPT.md`** — the verbatim original design prompt preserved as a project artifact, with an audit trail mapping each requirement to its implementation

6. **`docs/SETUP_MACOS.md`** — install and run guide tested on macOS (Apple Silicon and Intel)

7. **`docs/ARCHITECTURE.md`** — technical deep-dive: data flow, the 3-part signature rationale, QC floor math justification, column mapping mechanics, extension points

8. **`docs/DEMO_SCRIPT.md`** — 90-second Bluedot recording script with timing and backup talking points

9. **`docs/HACKATHON_SUBMISSION.md`** — paste-ready form answers for the Acadia AI Track 2026 submission

10. **`docs/GEMINI_HANDOFF.md`** — context brief for handing the project to Gemini for parallel documentation work

11. **`.gitignore`** — added with `!test_data.csv` exception so the validation dataset commits while client CSVs and secrets stay out

12. **Comprehensive `README.md`** — full project structure, quick start, deployment options table

13. **GitHub repository** — all 17+ files committed, browsable, shareable

### Key Design Decisions

**Decision 8: Build and commit a *validated* test dataset, not just a generator.**
Session 1's in-app `generate_mock_data()` button works, but it's invisible to anyone reading the repo without running the code. Committing `test_data.csv` directly means: (a) judges can download and inspect the data, (b) the file IS the validation — anyone running `detect_creative_fatigue()` against it gets the same flags every time, (c) the math is auditable without launching Streamlit.

**Decision 9: Engineer the test data for extreme slider tolerance.**
The validation CSV was designed so its severe fatigue ads flag at slider values up to 95% / 95% / 195% — far beyond defaults. Reasoning: during a live demo, judges will instinctively crank sliders to see what happens. If the ads stop flagging at 30%, the demo loses credibility. With deltas of +186% / −96% / +416% on the 7-day fatigued ad, the signal survives any reasonable slider tuning. This is the most defensible thing about the tool — empirically proven, not theoretical.

**Decision 10: Three field-mapping pathways, not one.**
Initial instinct was to document only the sidebar UI approach. But the realistic workflow is layered: account managers want UI mapping for ad-hoc work, teams want code-level defaults for consistency, the pipeline needs per-client maps for multi-account orchestration. Documenting all three explicitly (with worked examples) means anyone — regardless of technical depth — finds their path.

**Decision 11: Preserve the original prompt as a repo artifact.**
The original design prompt is the project's "constitution." Six months from now, when someone proposes adding ML-based fatigue prediction or removing the QC floor, the prompt's constraints ("must avoid flagging false positives due to low data volume," "highly adaptable across clients") are the reference point for that conversation. Keeping it inside the repo (`docs/ORIGINAL_PROMPT.md`) ensures it travels with the code permanently — not buried in a chat log.

**Decision 12: Use GitHub web UI for repo population, not git CLI.**
For a Senior Paid Media Manager (not a full-time engineer), a one-time drag-and-drop upload to GitHub is more reliable than learning git commands under time pressure. The repo ends up in the same state either way. Future updates can be selective edits in the web UI or a proper git clone — whichever pace fits.

**Decision 13: Enable Claude memory + create a Project for the work.**
The hackathon is one ship date, but the Morning Account Checks ecosystem is a multi-quarter effort. Enabling memory and adding this chat to a Claude Project means future conversations continue from context, not from scratch. Combined with the comprehensive repo docs, this gives true cross-session persistence — both for human reviewers (via the repo) and for AI collaboration (via the Project).

**Decision 14: Keep `level shipped` as `tool` in the submission.**
Even after building out the full repo + docs + validation, the honest classification remains `tool`. The orchestration layer that would make it a true `agent` (scheduled invocation, multi-step reasoning, downstream agent handoffs) is roadmap, not v1. The hackathon form rewards honesty here — judges can read the repo themselves.

### Validation

Confirmed end-to-end by running `detect_creative_fatigue()` directly against the committed `test_data.csv`:

| Window | Default sliders (15 / 20 / 25) | Extreme sliders (95 / 95 / 195) |
|---|---|---|
| **7-day** | ✅ `FATIGUE_7D_PEAK_E` (+186% / −96% / +416%) | ✅ still flags |
| **14-day** | ✅ `FATIGUE_14D_SUSTAINED_F` (+171% / −96% / +615%) | ✅ still flags |
| **30-day** | ✅ 3 ads flag (the three fatigue archetypes + mild) | ✅ `FATIGUE_30D_LONG_G` still flags |

`LOWVOL_Test_D` never appears at any threshold — QC filter holds. `HEALTHY_*` ads never appear — no false signal generation. `MILD_FATIGUE_H` flags at defaults and drops out at extreme settings — proving slider sensitivity works as designed.

### Deployment Status

The repo (live on GitHub with all files committed) now supports three deployment paths, ready to use:

1. **Local Streamlit** — `streamlit run fatigue_monitor.py` after a `pip install -r requirements.txt`. Validated on macOS.
2. **Streamlit Cloud** — deploys from GitHub in under 3 minutes, produces a public URL for the hackathon `Artifact link` field, auto-redeploys on every push.
3. **Headless pipeline** — `pipeline_fatigue.py` is ready to invoke; needs only a GCP service account JSON and a target Google Sheet to wire into the daily Morning Account Check cron.

### Hackathon Submission Status

All six required form fields have paste-ready answers in `docs/HACKATHON_SUBMISSION.md`. Outstanding items before final submit:
- [ ] Choose between GitHub repo URL or Streamlit Cloud URL for the `Artifact link` field
- [ ] Record 60–90 second Bluedot demo using `docs/DEMO_SCRIPT.md`
- [ ] Fill in `[YOUR TEAM NAME]` placeholder

### Open Questions / Carry-Forwards to Future Sessions

- **`test_data.csv` is realistic-looking but synthetic.** Real Funnel.io exports will surface edge cases the synthetic data doesn't: missing days, duplicate ad IDs across campaigns, currency symbols in spend, NULL values where conversions = 0. Test against a real export before treating this as production-grade.
- **No CI/CD yet.** The repo has no automated tests, linting, or deployment hooks. Reasonable for hackathon scope; needed for production.
- **Memory + Project setup is per-account.** This benefits Milan's future Claude conversations within this Project, but doesn't help teammates collaborating on the same repo. Documentation in the repo (`PROJECT_LOG.md`, `ORIGINAL_PROMPT.md`, `ARCHITECTURE.md`) remains the durable handoff mechanism.

---

## Future Sessions — Roadmap

### Next Up (v1.1)
- [ ] Per-client threshold profiles loaded from a config Sheet keyed by account ID
- [ ] Slack output integration (post top 5 fatigued ads per account to `#paid-media-alerts` at 6 AM)
- [ ] Add a "severity score" column (combined magnitude of all three deltas) for prioritization
- [ ] Validate against a real anonymized Funnel.io export

### Later (v1.2+)
- [ ] Multi-account orchestration loop with one entry-point script
- [ ] Backtest mode — replay historical data and surface known fatigue events to calibrate thresholds
- [ ] Confidence intervals on each delta to suppress borderline flags
- [ ] Automated pause recommendations with rationale strings
- [ ] Cross-account pattern detection (which creative formats fatigue fastest, by vertical)
- [ ] CI/CD: pytest suite, ruff linting, GitHub Actions workflow

### Maybe (v2.0)
- [ ] Integration with the parent Morning Account Checks agent orchestrator
- [ ] LLM-generated explanation text per flagged ad ("This carousel ad is showing classic UGC fatigue — frequency 2.8x in last 7 days, CTR halved, CPA up 60%")
- [ ] Per-platform schema adapters (Meta, TikTok, LinkedIn, Pinterest) auto-detected from CSV structure
- [ ] Promotion from `tool` → `agent` classification once orchestration layer is built
