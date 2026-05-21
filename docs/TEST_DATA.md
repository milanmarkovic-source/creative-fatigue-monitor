# Test Dataset Guide

## What's in `test_data.csv`

520 rows = **8 ads × 65 days**, covering May 21, 2026 backwards. Designed so every window size (7 / 14 / 30 days) produces meaningful results, and so that fatigued ads keep flagging even when the sliders are pushed to extreme values.

### The 8 ads

| Ad ID | Ad Name | Behavior | Should flag at... |
|---|---|---|---|
| AD_1001 | `HEALTHY_Video_A` | Stable across all 65 days | **Never** |
| AD_1002 | `HEALTHY_Carousel_B` | Stable across all 65 days | **Never** |
| AD_1003 | `HEALTHY_Static_C` | Stable across all 65 days | **Never** |
| AD_1004 | `LOWVOL_Test_D` | ~25 impressions/day | **Never** (QC excludes) |
| AD_1005 | `FATIGUE_7D_PEAK_E` | Severe decay only in last 7 days | **7-day** window |
| AD_1006 | `FATIGUE_14D_SUSTAINED_F` | Severe decay sustained last 14 days | **7-day** (partially), **14-day**, **30-day** (mildly) |
| AD_1007 | `FATIGUE_30D_LONG_G` | Severe decay sustained last 30 days | **30-day** window |
| AD_1008 | `MILD_FATIGUE_H` | Moderate decay last 30 days | **30-day** at defaults, NOT at high sliders |

### Validated detection results

Confirmed by running `detect_creative_fatigue()` directly against the CSV:

| Window | Default sliders (15 / 20 / 25) | Extreme sliders (95 / 95 / 195) |
|---|---|---|
| **7-day** | ✅ `FATIGUE_7D_PEAK_E` (+186% / −96% / +416%) | ✅ `FATIGUE_7D_PEAK_E` still flags |
| **14-day** | ✅ `FATIGUE_14D_SUSTAINED_F` (+171% / −96% / +615%) | ✅ `FATIGUE_14D_SUSTAINED_F` still flags |
| **30-day** | ✅ 3 ads flag (the three fatigue archetypes) | ✅ `FATIGUE_30D_LONG_G` still flags |

The extreme-slider behavior is the key test: this proves the data has ads with truly severe decay, not just borderline noise.

---

## How to use it in the app

1. Launch the app: `streamlit run fatigue_monitor.py`
2. Click **Upload CSV** in the main panel and select `test_data.csv`
3. Try every combination:
   - Switch the **Comparison Window** dropdown between 7, 14, and 30 days
   - Drag the three threshold sliders from low to high
   - Adjust the **Min impressions** input — drop it to 100 and watch nothing change (the LOWVOL ad still won't flag because its other metrics are stable)
4. Click **⬇️ Download flagged ads (CSV)** to confirm the export path works

---

## Regenerating the data

The CSV is deterministic (seeded). To regenerate (or modify archetypes for new test cases):

```bash
python3 generate_test_data.py
```

Edit `generate_test_data.py` to add new archetypes, change baseline metrics, or extend the time range. Each ad's `phases` list defines daily metrics for ranges of days-from-end, so you can model any decay curve.

---

## CSV Schema (what the app expects)

The CSV must contain these eight columns. The values shown are what `test_data.csv` uses — yours may differ (see **Adapting to Your Funnel.io Export** below).

| Column | Type | Description | Example |
|---|---|---|---|
| `Date` | ISO date | One row per ad per day | `2026-05-21` |
| `Ad ID` | string | Unique identifier (must be stable across days) | `AD_1001` |
| `Ad Name` | string | Display name | `HEALTHY_Video_A` |
| `Impressions` | int | Daily impressions | `3066` |
| `Reach` | int | Daily reach (used for frequency calculation) | `1905` |
| `Clicks` | int | Daily clicks (used for CTR calculation) | `71` |
| `Spend` | float | Daily spend (used for CPA calculation) | `194.46` |
| `Conversions` | int | Daily conversions (used for CPA calculation) | `8` |

**Row granularity:** one row per ad per day. The app aggregates daily rows into window totals before computing window-over-window deltas.
