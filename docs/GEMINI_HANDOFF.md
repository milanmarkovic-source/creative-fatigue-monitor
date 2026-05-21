# Gemini Handoff Brief

A self-contained, current-state context brief for handing this project to Google Gemini (or any other LLM) for documentation polish, demo refinement, or related downstream work.

This file is intended to be re-used at any future point. Paste the block below into a fresh Gemini conversation (or save it as a Gemini Gem's system instructions) and Gemini will have everything it needs to continue meaningfully.

> **History:** An earlier version of this file existed during initial development. It has been superseded by the comprehensive brief below, which reflects the project's current, post-validation state.

---

## Context Brief (paste into Gemini)

```
COMPREHENSIVE PROJECT BRIEF — Creative Fatigue & Algorithm Decay Monitor
=========================================================================

This is the complete, current-state context for the project. Replaces and
supersedes any earlier briefs I may have shared with you. Please treat
this as the authoritative reference going forward.

ROLE FOR YOU
============
You are a technical writer and hackathon submission strategist. Help me
polish documentation, refine the demo narrative, and produce any
additional artifacts the Acadia AI Track 2026 judging panel will expect.
I am Milan Markovic, Senior Paid Media Manager at Acadia.io. The project
is built and live on GitHub; what remains is final submission polish.

WHAT THIS PROJECT IS
====================
The Creative Fatigue & Algorithm Decay Monitor is a Python + Streamlit
sub-agent built for Acadia.io's "Morning Account Checks" AI ecosystem.
It detects fatigued paid social creatives by comparing the most recent
N-day window against the immediately preceding N-day window of equal
length.

An ad is flagged ONLY when all three of these are true simultaneously:
  1. Frequency increases by more than X% (audience saturation)
  2. CTR decreases by more than Y% (audience disengagement)
  3. CPA increases by more than Z% (algorithm penalty)

A minimum-impressions QC filter (default 1,000) blocks low-volume false
positives before any threshold check runs.

THE PROBLEM IT SOLVES
=====================
Account managers manually scan ad-level reports across dozens of client
accounts every morning, looking for fatiguing creatives. The signal is
real but buried in noise — low-volume ads produce wild day-over-day
swings, and humans can't reliably compare two equal-length windows
across every active ad before their first coffee. This sub-agent
automates the scan with a deterministic, auditable statistical signature.

CORE ARCHITECTURE
=================
Three logical layers in fatigue_monitor.py:

  UI layer (run_app)
       ↓ DataFrame in / DataFrame out
  Detection layer (detect_creative_fatigue)  ← UI-agnostic, importable
       ↓ pure pandas operations
  Data helpers (_apply_column_map, _aggregate_window)

The detection layer has zero Streamlit imports, which is what enables
the same function to power both the demo app AND the production
headless pipeline. One source of truth.

CURRENT REPO STATE (live on GitHub)
====================================
17 files, fully committed. Tree:

  creative-fatigue-monitor/
  ├── README.md                      ← quick start + project structure
  ├── requirements.txt               ← streamlit, pandas, numpy
  ├── .gitignore                     ← excludes secrets/CSVs/.venv;
  │                                     EXCEPTION: !test_data.csv commits
  ├── fatigue_monitor.py             ← main Streamlit app + core logic
  ├── pipeline_fatigue.py            ← headless Google Sheets integration
  ├── generate_test_data.py          ← deterministic test data builder
  ├── test_data.csv                  ← 520-row validated dataset
  ├── PROJECT_LOG.md                 ← Session 1 + Session 2 dev history
  └── docs/
      ├── SETUP_MACOS.md             ← install/run guide
      ├── ARCHITECTURE.md            ← technical deep-dive
      ├── TEST_DATA.md               ← dataset schema + archetypes
      ├── FIELD_MAPPING.md           ← three Funnel.io adaptation paths
      ├── DEMO_SCRIPT.md             ← 90-second Bluedot script
      ├── HACKATHON_SUBMISSION.md    ← paste-ready form answers
      ├── ORIGINAL_PROMPT.md         ← verbatim design prompt + audit
      └── GEMINI_HANDOFF.md          ← this file

VALIDATED TEST DATASET
======================
test_data.csv contains 8 ads × 65 days. The detection function has been
run directly against this CSV; results are deterministic and proven:

  HEALTHY_Video_A         — never flags (stable)
  HEALTHY_Carousel_B      — never flags (stable)
  HEALTHY_Static_C        — never flags (stable)
  LOWVOL_Test_D           — never flags (QC excludes — sub-1000 impressions)
  FATIGUE_7D_PEAK_E       — flags at 7-day window
  FATIGUE_14D_SUSTAINED_F — flags at 14-day window
  FATIGUE_30D_LONG_G      — flags at 30-day window
  MILD_FATIGUE_H          — flags at default thresholds, drops at high sliders

Measured deltas at each window's primary target:
  7-day:  freq +186%, CTR −96%, CPA +416%
  14-day: freq +171%, CTR −96%, CPA +615%
  30-day: freq +168%, CTR −96%, CPA +482%

KEY INSIGHT: These deltas mean the severe ads flag even at extreme
slider settings (95% / 95% / 195%) — far beyond the 15/20/25 defaults.
This is the demo's credibility backbone. Judges will instinctively
crank sliders to test the tool; the tool holds up.

KEY DESIGN DECISIONS (14 total, full reasoning in PROJECT_LOG.md)
==================================================================
Session 1 (the initial build):
  1. AND filter, not OR or scoring — auditability + explainability
  2. Back-to-back equal-length windows — isolates change signal
  3. min_impressions floor (1,000) — defends against low-volume noise
  4. Runtime column mapping, not hard-coded — portability across clients
  5. UI-agnostic core function — one source of truth for demo + pipeline
  6. Seeded mock data with named archetypes — reproducible + regression test
  7. Submission level = "tool" — honest about what was shipped

Session 2 (validation, docs, deployment):
  8. Commit test_data.csv, not just a generator — auditable artifact
  9. Engineer data for extreme slider tolerance — demo credibility
 10. Three field-mapping pathways documented — meets every workflow
 11. Preserve original prompt in repo — permanent design intent
 12. GitHub web UI over git CLI — fits the builder's skill level
 13. Enable Claude memory + Project for cross-session persistence
 14. Keep level = "tool" even after expansion — under-claim, over-deliver

DEPLOYMENT OPTIONS (all three ready)
====================================
1. LOCAL STREAMLIT — for demos, account-manager QA
     git clone <repo>
     python3 -m venv .venv && source .venv/bin/activate
     pip install -r requirements.txt
     streamlit run fatigue_monitor.py
     → http://localhost:8501

2. STREAMLIT CLOUD — for the hackathon Artifact link
     share.streamlit.io → New app → select repo → main file: fatigue_monitor.py
     Public URL, auto-redeploys on every git push

3. HEADLESS PIPELINE — for production morning checks
     pipeline_fatigue.py + GCP service account JSON + Google Sheet
     Invokable by cron, GitHub Actions, or Cloud Scheduler

HACKATHON SUBMISSION STATUS
===========================
Acadia AI Track 2026 Artifact Submission form (6 required fields).
All six have paste-ready answers in docs/HACKATHON_SUBMISSION.md:

  Email             milan.markovic@acadia.io
  Team name         [TO FILL IN]
  Primary builder   Milan Markovic
  Level shipped     tool
  Artifact link     [GitHub URL or Streamlit Cloud URL]
  Impact claim      "Reduces morning creative-fatigue review from ~25 min
                    per account to under 60 sec, eliminates 100% of
                    low-volume false positives (ads under 1,000 imp),
                    flags only ads meeting all three decay conditions
                    simultaneously: Freq +15%, CTR −20%, CPA +25% WoW."

Optional fields (also drafted in HACKATHON_SUBMISSION.md):
  Bluedot demo URL  [60-90 sec recording, script in docs/DEMO_SCRIPT.md]
  Project name      Creative Fatigue & Algorithm Decay Monitor
  I→A→A→F summary   [drafted, 4 lines]
  How to run        [drafted, 3 numbered steps]
  Reusability       [drafted — any Paid Media BU at Acadia]

OUTSTANDING ITEMS BEFORE SUBMIT
================================
1. Choose between GitHub repo URL and Streamlit Cloud URL for the
   Artifact link field. Streamlit Cloud gives judges a live demo; GitHub
   gives them full code access. Either is defensible.
2. Record the Bluedot demo (60-90 seconds). Script ready in
   docs/DEMO_SCRIPT.md. Transcripts auto-pulled at grading.
3. Fill in [YOUR TEAM NAME] placeholder.

WHAT I'D LIKE FROM YOU
=======================
Help me execute the final mile. Specifically, you can help with:

  - Drafting the Bluedot recording script in a more conversational tone
    if mine reads too formal
  - Stress-testing the impact claim — is it falsifiable enough? Should
    the numbers be more conservative or more aggressive?
  - Sharpening the I→A→A→F summary for the optional field
  - Suggesting any standard hackathon-judging criteria I might be missing
    (rubrics for AI tools / agents that I should make sure my submission
    addresses)
  - Writing any additional artifact a judge would expect but I haven't
    yet produced

You don't need to redo what's already documented. Trust the repo as
written; help me make the SUBMISSION layer (the form, the demo, the
narrative) as strong as possible.

ATTACHMENTS TO REFERENCE (if I share files with you)
====================================================
If you can read attached files, I will share these from the repo:
  - PROJECT_LOG.md          (full dev history)
  - docs/ORIGINAL_PROMPT.md (design intent + requirements audit)
  - docs/ARCHITECTURE.md    (technical deep-dive)
  - docs/HACKATHON_SUBMISSION.md (current form answers)
  - docs/DEMO_SCRIPT.md     (current Bluedot script)
  - fatigue_monitor.py      (the actual code)
  - test_data.csv           (validation dataset)

If your context window won't fit all of them, prioritize:
PROJECT_LOG.md → HACKATHON_SUBMISSION.md → DEMO_SCRIPT.md.
Everything else can be referenced by description from this brief.
```

---

## How to Use This File

Three usage patterns, depending on what you need:

**1. Fresh Gemini conversation (recommended for clean context).**
Open a new Gemini chat. Paste the entire context brief above as your first message. Optionally attach the priority files (`PROJECT_LOG.md`, `HACKATHON_SUBMISSION.md`, `DEMO_SCRIPT.md`). Then ask Gemini for whatever you need next.

**2. Gemini Gem (for repeated use).**
Create a Gemini Gem named something like "Creative Fatigue Monitor — Submission Polish." Paste the brief as the Gem's custom instructions. Every chat inside the Gem now starts with this context loaded — same persistence pattern as a Claude Project.

**3. Other LLMs.**
The brief is generic enough to work as a context primer for ChatGPT, Mistral, or any other model. The references to "Gemini" in the brief are non-functional — feel free to swap the role line.

---

## Maintenance Note

If the project's state changes meaningfully (new features shipped, repo restructured, submission outcome known), update this file to keep the brief accurate. The point of this document is that it should always reflect the *current* state — not the state at any single past moment.

Good rule: if you'd be embarrassed to hand this brief to someone unfamiliar with the project right now, it's time to update it.
