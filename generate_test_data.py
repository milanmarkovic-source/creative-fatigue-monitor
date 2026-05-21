"""
Test data generator for the Creative Fatigue Monitor.
Produces 65 days of ad-level data with carefully calibrated archetypes:

  HEALTHY_*       — stable across all windows (never flags)
  LOWVOL_*        — below QC floor (always excluded)
  FATIGUE_7D_*    — severe decay ONLY in last 7 days (flags at 7-day window)
  FATIGUE_14D_*   — severe decay sustained for 14 days (flags at 14-day window)
  FATIGUE_30D_*   — severe decay sustained for 30 days (flags at 30-day window)
  MILD_FATIGUE_*  — moderate decay (flags at defaults, stops at high sliders)

Severe ads are designed so frequency, CTR, and CPA all blow past extreme
slider values: freq +170%, CTR −95%, CPA +280% in their respective windows.

Reproducible — seeded RNG. Re-run anytime to regenerate.
"""

import csv
import random
from datetime import date, timedelta

# ----------------------------------------------------------------------------
# CONFIGURATION
# ----------------------------------------------------------------------------
SEED = 42
NUM_DAYS = 65                       # 65 days covers a 30-day window comparison
END_DATE = date(2026, 5, 21)        # last day in the dataset
OUTPUT_PATH = "test_data.csv"

random.seed(SEED)


def noisy(value: float, pct: float = 0.05) -> float:
    """Apply ±pct uniform noise to a value."""
    return value * (1 + random.uniform(-pct, pct))


# ----------------------------------------------------------------------------
# AD ARCHETYPES
# Each phase: (start_days_from_end inclusive, end_days_from_end exclusive,
#              daily metrics dict)
# day 0 = the most recent day in the dataset (END_DATE)
# ----------------------------------------------------------------------------
HEALTHY = {"impressions": 3000, "reach": 2000, "clicks": 75, "spend": 200, "conversions": 8}
# Healthy: freq=1.5, CTR=2.5%, CPA=$25

SEVERE  = {"impressions": 4500, "reach": 1100, "clicks": 5,  "spend": 95,  "conversions": 1}
# Severe: freq≈4.09, CTR≈0.11%, CPA=$95
# vs healthy: freq +173%, CTR −96%, CPA +280%

MILD    = {"impressions": 3500, "reach": 1750, "clicks": 52, "spend": 200, "conversions": 5}
# Mild: freq=2.0, CTR≈1.49%, CPA=$40
# vs healthy: freq +33%, CTR −40%, CPA +60%

LOWVOL  = {"impressions": 25,   "reach": 20,   "clicks": 1,  "spend": 5,   "conversions": 0}
# Sub-threshold volume — excluded by QC at every window size

ADS = [
    {"id": "AD_1001", "name": "HEALTHY_Video_A",
     "phases": [(0, 65, HEALTHY)]},

    {"id": "AD_1002", "name": "HEALTHY_Carousel_B",
     "phases": [(0, 65, {"impressions": 3500, "reach": 2300, "clicks": 90, "spend": 250, "conversions": 10})]},

    {"id": "AD_1003", "name": "HEALTHY_Static_C",
     "phases": [(0, 65, {"impressions": 2800, "reach": 1900, "clicks": 65, "spend": 180, "conversions": 7})]},

    {"id": "AD_1004", "name": "LOWVOL_Test_D",
     "phases": [(0, 65, LOWVOL)]},

    {"id": "AD_1005", "name": "FATIGUE_7D_PEAK_E",
     "phases": [(0, 7, SEVERE), (7, 65, HEALTHY)]},

    {"id": "AD_1006", "name": "FATIGUE_14D_SUSTAINED_F",
     "phases": [(0, 14, SEVERE), (14, 65, HEALTHY)]},

    {"id": "AD_1007", "name": "FATIGUE_30D_LONG_G",
     "phases": [(0, 30, SEVERE), (30, 65, HEALTHY)]},

    {"id": "AD_1008", "name": "MILD_FATIGUE_H",
     "phases": [(0, 30, MILD), (30, 65, HEALTHY)]},
]


# ----------------------------------------------------------------------------
# GENERATE
# ----------------------------------------------------------------------------
def find_phase(phases, days_from_end):
    for start, end, metrics in phases:
        if start <= days_from_end < end:
            return metrics
    return phases[-1][2]


def main():
    rows = []
    for ad in ADS:
        for days_from_end in range(NUM_DAYS):
            actual_date = END_DATE - timedelta(days=days_from_end)
            base = find_phase(ad["phases"], days_from_end)

            rows.append({
                "Date":        actual_date.isoformat(),
                "Ad ID":       ad["id"],
                "Ad Name":     ad["name"],
                "Impressions": max(0, int(noisy(base["impressions"], 0.08))),
                "Reach":       max(1, int(noisy(base["reach"], 0.05))),
                "Clicks":      max(0, int(noisy(base["clicks"], 0.10))),
                "Spend":       round(noisy(base["spend"], 0.05), 2),
                "Conversions": max(0, int(noisy(base["conversions"], 0.15))),
            })

    fields = ["Date", "Ad ID", "Ad Name", "Impressions", "Reach", "Clicks", "Spend", "Conversions"]
    with open(OUTPUT_PATH, "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fields)
        writer.writeheader()
        writer.writerows(rows)
    print(f"✅ Wrote {len(rows)} rows to {OUTPUT_PATH}")


if __name__ == "__main__":
    main()
