# AI Track 2026 — Submission Package

Paste-ready answers for the Acadia AI Track 2026 Artifact Submission form. Bracketed `[FIELDS]` are for you to swap in.

---

## Required Fields (6 fields, ~2 min)

### Email
```
milan.markovic@acadia.io
```

### Team name
```
[YOUR TEAM NAME]
```

### Primary builder
```
Milan Markovic
```

### Level shipped
```
tool
```

> **Rationale:** It's an executable Python/Streamlit tool with a deterministic core function. Switch to `agent` if your submission narrative emphasizes its role as a sub-agent inside the Morning Account Checks ecosystem — both are defensible, but `tool` matches what was actually shipped this session.

### Artifact link
```
[PASTE YOUR REPO URL OR DEPLOYED STREAMLIT URL]
```

> If you haven't pushed yet:
> 1. Create a GitHub repo (private with judge access, or public).
> 2. Push this folder's contents.
> 3. For a hosted demo, deploy free at [share.streamlit.io](https://share.streamlit.io) — connect the repo, point at `fatigue_monitor.py`, done in under 3 minutes.

### Impact claim
```
Reduces morning creative-fatigue review time from ~25 minutes per account to under 60 seconds, while eliminating 100% of low-volume false positives (ads under 1,000 impressions) and flagging only ads meeting all three decay conditions simultaneously: Frequency +15%, CTR −20%, CPA +25% window-over-window.
```

---

## Optional but Encouraged

### Bluedot meeting URL
```
[PASTE BLUEDOT LINK TO YOUR 60–90 SEC DEMO]
```

> Use `docs/DEMO_SCRIPT.md` as the recording script.

### Project name
```
Creative Fatigue & Algorithm Decay Monitor
```

### Additional builders
```
[COMMA-SEPARATED NAMES, OR LEAVE BLANK]
```

### I → A → A → F Summary

```
Inputs: Funnel.io ad-level CSV export (date, ad_id, ad_name, impressions, reach, clicks, spend, conversions) — column names mapped at runtime to fit any client schema.

Analysis: Aggregates each ad across two equal-length back-to-back windows (7/14/30 days), computes window-over-window deltas in Frequency, CTR, and CPA, then applies a 3-part signature filter gated by a minimum-impressions QC floor.

Action: Returns a ranked DataFrame of fatigued ads with all delta percentages, one-click CSV export, and a headless function path that writes results to a Google Sheet for downstream digest agents.

Frequency: Designed to run daily as part of the 6 AM Morning Account Checks; safe to re-run on demand (stateless, idempotent).
```

### How to run (3 numbered steps)
```
1. Clone the repo, then in terminal: python3 -m venv .venv && source .venv/bin/activate && pip install -r requirements.txt

2. Run: streamlit run fatigue_monitor.py — it opens at http://localhost:8501

3. Click "Generate Mock Dataset (60 days)" to validate the tool, then upload your client's Funnel.io CSV and adjust the sidebar (window length, X/Y/Z thresholds, min-impressions floor, column mapping) to match your account.
```

### Reusability
```
Any Paid Media BU at Acadia — specifically Account Managers and Strategists running Meta, TikTok, or LinkedIn paid social. Drop-in for the daily Morning Account Check workflow. The column-mapping config makes it portable across any client's Funnel.io export without code changes; the headless detect_creative_fatigue() function plugs directly into existing Google Sheets reporting pipelines for fully automated daily runs.
```

---

## Pre-Submit Checklist

- [ ] Artifact link resolves (GitHub repo or `share.streamlit.io` URL)
- [ ] Bluedot demo recorded (60–90 seconds — transcripts are auto-pulled at grading time)
- [ ] Confirmed `level shipped` choice (`tool` recommended; `agent` only if orchestration is demonstrated)
- [ ] Team name filled in
- [ ] Email correct
- [ ] Impact claim has specific X / Y / Z numbers (it does — 15 / 20 / 25 / 1,000)
