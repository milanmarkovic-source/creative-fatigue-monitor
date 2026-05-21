# Technical Architecture

## Overview

The Creative Fatigue & Algorithm Decay Monitor is a single-file Python application with three logical layers:

```
┌──────────────────────────────────────────────────────┐
│  Streamlit UI Layer  (run_app)                       │
│  ─ Sidebar config + data loader + results display    │
└────────────────────┬─────────────────────────────────┘
                     │ DataFrame in / DataFrame out
                     ▼
┌──────────────────────────────────────────────────────┐
│  Detection Layer  (detect_creative_fatigue)          │
│  ─ Column mapping → window aggregation → 3-part      │
│    signature filter → ranked output                  │
└────────────────────┬─────────────────────────────────┘
                     │ Pure pandas operations
                     ▼
┌──────────────────────────────────────────────────────┐
│  Data Helpers  (_apply_column_map, _aggregate_window)│
│  ─ Schema validation + windowed aggregation          │
└──────────────────────────────────────────────────────┘
```

The detection layer has zero UI dependencies, which is what enables the same function to power both the demo app and the production pipeline.

---

## Data Flow

```
Raw CSV (Funnel.io export)
   │
   ▼
DataFrame loaded into memory (Streamlit or pipeline)
   │
   ▼
_apply_column_map()      ← Renames client-specific columns to canonical names
   │
   ▼
Date parsing + window definition
   │   current_window  = [reference_date - N + 1 ... reference_date]
   │   previous_window = [reference_date - 2N + 1 ... reference_date - N]
   ▼
_aggregate_window() × 2  ← Sum metrics per ad in each window, derive freq/CTR/CPA
   │
   ▼
Inner join on (ad_id, ad_name)
   │
   ▼
QC filter: drop ads with impressions_curr < MIN_IMPRESSIONS
   │
   ▼
Compute pct deltas: freq, CTR, CPA
   │
   ▼
3-part signature filter (AND):
   freq_delta > +X%  AND  ctr_delta < -Y%  AND  cpa_delta > +Z%
   │
   ▼
Sort by CPA delta descending → return DataFrame
```

---

## The 3-Part Fatigue Signature

The signature is intentionally narrow. Each leg captures a different facet of decay:

| Signal | What it means | Default threshold |
|---|---|---|
| **Frequency ↑** | Audience saturation — same users seeing the ad repeatedly | > +15% |
| **CTR ↓** | Audience disengagement — fewer clicks per impression | < −20% |
| **CPA ↑** | Algorithmic penalty — platform charging more per conversion | > +25% |

**Why all three (AND), not any (OR), and not a score?**

- *OR* would over-flag. Any single metric can move for unrelated reasons (a campaign budget change, a landing-page update, a seasonal shift).
- *Score* (weighted sum) would be harder to explain to account managers and harder to audit. "Why did this ad flag?" needs a one-sentence answer.
- *AND* requires the *pattern* of fatigue to be present. If only frequency rose, that's a budget event, not fatigue. If only CTR fell, that's a creative/audience issue but not necessarily saturation. The conjunction is the signal.

---

## Quality Control Filter

The `min_impressions` floor (default 1,000) is the single most important defense against false positives.

**The math problem:** percent-change deltas are unbounded when denominators are small. An ad going from 100 to 105 impressions is +5%. An ad going from 5 to 10 is +100%. The *information content* of those two moves is wildly different, but a naive filter treats them equally.

**The fix:** require both windows to contain enough volume that the law of large numbers applies. 1,000 impressions in a 7-day window is a defensible floor for most paid social platforms — that's roughly 140/day, enough that random variance shouldn't dominate the signal. Account managers can raise it for high-spend clients or lower it for niche audiences.

---

## Column Mapping

`DEFAULT_COLUMN_MAP` is a dictionary from canonical internal names (used by the detection logic) to source CSV column names (what the export actually contains):

```python
{
    "date":        "Date",
    "ad_id":       "Ad ID",
    "ad_name":     "Ad Name",
    "impressions": "Impressions",
    "reach":       "Reach",
    "clicks":      "Clicks",
    "spend":       "Spend",
    "conversions": "Conversions",
}
```

`_apply_column_map()` validates that every mapped source column exists in the input DataFrame (raising `ValueError` with a clear message if not), then renames them. This means the detection logic only ever sees canonical names — it never has to care that Client A calls it "Spend" and Client B calls it "Cost".

The Streamlit UI exposes every entry of this map as an editable text input in the sidebar, so an account manager can match their specific Funnel.io export at runtime without touching code.

---

## Window Calculation

Given a `reference_date` (defaults to the latest date in the data) and `window_days = N`:

- **Current window:**  `[reference_date − (N − 1), reference_date]` (inclusive, N days)
- **Previous window:** `[reference_date − (2N − 1), reference_date − N]` (inclusive, N days)

The two windows are immediately adjacent — no gap, no overlap. This is the standard window-over-window comparison and isolates the change signal without introducing extra confounding from non-adjacent periods.

---

## Mock Data Generator Design

`generate_mock_data()` is deliberately constructed, not random. It uses a seeded RNG (`seed=42`) so demo output is reproducible. Three archetypes are baked in:

| Archetype | Behavior | Expected outcome |
|---|---|---|
| `Healthy_*` (×3) | Stable metrics across all 60 days with light noise | Should NOT flag |
| `LowVol_*` (×2) | Sub-1,000 impressions in current window | Should be EXCLUDED by QC |
| `Fatigued_*` (×2) | Frequency +45%, CTR −35%, CPA +55% in last 7 days only | Should FLAG |

The fatigued ads' metric shifts intentionally exceed the default thresholds (15% / 20% / 25%) so the demo always works with out-of-the-box settings. They're also intentionally close enough to the thresholds that adjusting the sliders during a demo produces visible state changes (good for live tuning demos).

---

## Why Streamlit (Specifically)

- **Zero deployment friction.** `streamlit run fatigue_monitor.py` is the entire deploy step for local demos. `share.streamlit.io` deploys from a GitHub repo in under a minute for cloud hosting.
- **No frontend code.** The sidebar widgets are one line each. Account managers — not engineers — should be able to clone, modify thresholds, and ship variants.
- **DataFrame-native.** `st.dataframe()` renders pandas tables with sortable columns and CSV export for free.
- **Auto-rerun on file change.** Tight feedback loop during development.

The tradeoff: Streamlit isn't a production user-facing app framework. For broad rollout across the agency, the headless pipeline (`pipeline_fatigue.py`) writing to Sheets and Slack is the production path — Streamlit is the QA / power-user surface.

---

## Extension Points

If you're extending this, the cleanest insertion points:

| Where | What to add |
|---|---|
| **`detect_creative_fatigue()` signature** | New thresholds (e.g., minimum spend floor, ROAS check) — add as kwargs with defaults to preserve backward compatibility |
| **`_aggregate_window()` agg dict** | New derived metrics (e.g., CPM, hook rate) — compute alongside frequency/CTR/CPA |
| **Filter expression** | Add a fourth signal to the AND chain, or add an OR-of-AND group for multiple fatigue patterns |
| **Output columns** | The return DataFrame's column list is explicit at the bottom of `detect_creative_fatigue()` — append new columns there |
| **UI sidebar** | Add new widgets inside `with st.sidebar:` block — pass their values into the function call |
| **Pipeline orchestration** | `pipeline_fatigue.py` is the template — duplicate for multi-client loops, swap output sinks (Slack, BigQuery, etc.) |
