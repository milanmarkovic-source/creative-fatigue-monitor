# Gemini Handoff Brief

Paste the block below into Gemini to continue documentation work with full context.

---

## Context Brief (paste into Gemini)

```
ROLE: You are a technical writer and hackathon submission strategist helping
document an AI agent project for final submission.

PROJECT NAME: Creative Fatigue & Algorithm Decay Monitor

CONTEXT:
I am a Senior Paid Media Manager at Acadia.io. I am building a sub-agent
within a larger "Morning Account Checks" AI agent ecosystem. This specific
sub-agent automates the detection of creative fatigue across paid social ads
by analyzing window-over-window metric decay.

PROBLEM IT SOLVES:
Account managers manually scan ad-level reports every morning trying to spot
fatigued creatives. The signal is buried in noise — low-volume ads produce
false positives, and humans struggle to compare two time windows side-by-side
across dozens of ads per account. This sub-agent automates that scan with a
deterministic statistical signature.

WHAT WAS BUILT:
A Python + Streamlit application called fatigue_monitor.py with:

1. CORE DETECTION LOGIC — detect_creative_fatigue()
   A UI-agnostic function that flags an ad as fatigued only when ALL THREE
   conditions are true in the current window vs. the immediately preceding
   window of equal length:
     - Frequency increases by more than X% (default 15%)
     - CTR decreases by more than Y% (default 20%)
     - CPA increases by more than Z% (default 25%)

2. DYNAMIC TIME WINDOWS
   User picks 7, 14, or 30 days. The script auto-computes the current window
   (ending at the latest date in the dataset) and the preceding window of
   equal length, then aggregates metrics per ad in each.

3. QUALITY CONTROL FILTER
   Ads with fewer than MIN_IMPRESSIONS (default 1,000) in the current window
   are excluded before any threshold comparison. This is the single most
   important defense against false positives from low-volume noise.

4. UNIVERSAL COLUMN MAPPING
   A DEFAULT_COLUMN_MAP dictionary lets any account manager map their own
   CSV column names (typically a Funnel.io export) to the canonical internal
   field names: date, ad_id, ad_name, impressions, reach, clicks, spend,
   conversions. Editable from the Streamlit sidebar at runtime.

5. MOCK DATA GENERATOR — generate_mock_data()
   Produces 60 days of synthetic ad-level data with three archetypes:
     - Healthy ads (stable metrics — should NOT flag)
     - Low-volume ads (sub-threshold impressions — must be filtered by QC)
     - Fatigued ads (sharp metric decay in the most recent 7 days — should flag)
   Triggered by a button in the Streamlit UI for instant demo readiness.

6. STREAMLIT UI
   Sidebar contains: window-days dropdown (7/14/30), three threshold sliders
   (X/Y/Z), min-impressions number input, and editable column-mapping fields.
   Main pane shows: data preview, the two date ranges being compared, a
   count of flagged ads, the flagged dataframe with all delta percentages,
   and a CSV download button.

7. HEADLESS PIPELINE PATH
   The core function is importable with zero Streamlit dependencies, so it
   plugs directly into a Google Sheets / gspread pipeline for scheduled
   morning runs without any UI.

TECH STACK:
Python 3.10+, Streamlit, pandas, numpy. Optional for pipeline mode:
gspread, gspread-dataframe, google-auth.

VALIDATION:
Tested locally on macOS with the built-in mock dataset. With default
thresholds (15% / 20% / 25% / 1,000 min impressions), the two seeded
Fatigued_* ads correctly flag and the two LowVol_* ads are correctly
excluded by the QC filter. Healthy_* ads stay quiet. Logic is deterministic
and reproducible (seeded RNG).

SUBMISSION TARGET:
Acadia AI Track 2026 Hackathon. Form requires: team name, primary builder,
level shipped (Gem / agent / tool / no-code), artifact link, falsifiable
impact claim with specific X/Y/Z numbers. Optional: Bluedot demo URL,
I→A→A→F summary, how-to-run steps, reusability statement.

WHAT I NEED FROM YOU (Gemini):
Help me finalize hackathon submission documentation: a polished project
description, a technical architecture writeup, a demo script for judges,
and any other artifacts the judging panel will expect. I will share the
hackathon's specific submission form fields in my next message.
```

---

## Files to Share with Gemini (if it accepts uploads)

If your Gemini conversation supports file uploads, attach:
- `fatigue_monitor.py` — the actual code
- `docs/ARCHITECTURE.md` — design rationale
- `docs/HACKATHON_SUBMISSION.md` — current form answers
- `PROJECT_LOG.md` — development history

That gives Gemini everything it needs to produce polished, accurate documentation without making up details.
