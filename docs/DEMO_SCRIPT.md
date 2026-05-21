# Hackathon Demo Script (90 seconds)

Use this verbatim for the Bluedot recording. Timing assumes a moderate, confident pace.

---

## Pre-recording Checklist

- [ ] App running locally at `http://localhost:8501`
- [ ] Browser window full-screen, no other tabs visible
- [ ] Terminal hidden — screen-share the browser only
- [ ] Microphone tested, no background noise
- [ ] Default thresholds confirmed: **15% / 20% / 25% / 1,000**
- [ ] Mock dataset NOT pre-loaded (you'll click the button live)

---

## Script

### [0:00 — 0:15] Frame the Problem

> "Every morning at Acadia, account managers manually scan ad-level reports across dozens of client accounts looking for creative fatigue. The signal is real — but it's buried in noise. Low-volume ads swing 200% day-over-day and look catastrophic when they're actually irrelevant. This is what I built to fix that."

**On screen:** App loaded, empty state visible.

---

### [0:15 — 0:35] The Logic

> "It's a deterministic filter that flags an ad only when three things happen at the same time, in the most recent N days versus the previous N days: frequency rises by more than X percent, CTR drops by more than Y percent, AND CPA spikes by more than Z percent. All three. That conjunction is the fatigue signature."

**On screen:** Hover over the sidebar — the three sliders, the window dropdown, the impressions floor.

---

### [0:35 — 0:55] The Demo

> "Let me show you. I'll click 'Generate Mock Dataset' — that's 60 days of synthetic ad data with three healthy ads, two low-volume ads, and two fatigued ads seeded in."

**On screen:** Click button. Data preview appears.

> "With default thresholds — 15, 20, 25 — and the 1,000-impressions QC floor, the detector flags exactly the two fatigued ads. The low-volume ads are excluded by the floor. The healthy ads stay quiet. That's the signature working."

**On screen:** Scroll to the flagged ads table. Point at the delta columns.

---

### [0:55 — 1:15] Tunability

> "Account managers calibrate per-client. Watch this — if I drop the CTR threshold to 5%, more ads flag. If I raise the frequency threshold to 50%, fewer flag. The column-mapping panel down here means any Funnel.io export from any client works — just rename the fields once."

**On screen:** Move CTR slider. Move frequency slider. Briefly show column mapping.

---

### [1:15 — 1:30] The Bigger Picture

> "The detection function is UI-agnostic. The same code that powers this demo plugs straight into a scheduled Google Sheets pipeline for the 6 AM Morning Account Check. This is one sub-agent in that ecosystem. The next ones — Slack digests, automated pause recommendations, cross-account benchmarking — build on this same core. That's the submission."

**On screen:** Briefly show `pipeline_fatigue.py` open in a code editor (optional, only if you have time).

---

## Backup Talking Points (if asked questions live)

**"Why all three conditions and not a score?"**
> Scoring is harder to audit. With the AND filter, every flag has a one-sentence explanation: "frequency up X, CTR down Y, CPA up Z." Account managers trust deterministic logic they can verify.

**"How did you pick the default thresholds?"**
> They're starting points for paid social benchmarks, validated against the mock dataset. In production, each client would calibrate based on their historical baseline — that's the v1.1 feature.

**"What's the QC floor for?"**
> Low-volume ads produce huge relative swings. Five impressions to ten is a 100% jump. The 1,000 floor ensures the law of large numbers applies before any threshold check runs.

**"Why Streamlit?"**
> Zero deployment friction for the demo and account-manager QA workflow. The headless function path is the production deployment — Streamlit is the power-user surface, not the production interface.

**"Is this really an AI agent?"**
> It's a deterministic sub-agent inside a broader Morning Account Checks agent ecosystem. The orchestration layer that wraps multiple sub-agents like this one — that's the broader agent. This is one capability inside it. I'm being honest about scope; the form's "level shipped" is `tool` for that reason.
