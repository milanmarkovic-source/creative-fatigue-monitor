"""
Headless Google Sheets Pipeline
================================
Bypasses the Streamlit UI and runs the fatigue detection on a schedule,
writing results back to a Google Sheet.

Designed to be invoked by cron, GitHub Actions, Cloud Scheduler, or any
orchestrator. Stateless and idempotent — safe to re-run.

Requirements:
    pip install gspread gspread-dataframe google-auth pandas numpy
"""

import gspread
from gspread_dataframe import get_as_dataframe, set_with_dataframe

from fatigue_monitor import detect_creative_fatigue, DEFAULT_COLUMN_MAP


# ---------------------------------------------------------------------------
# CONFIGURATION — edit per-deployment
# ---------------------------------------------------------------------------
SERVICE_ACCOUNT_FILE = "service_account.json"     # path to GCP service-account JSON
SHEET_ID             = "YOUR_GOOGLE_SHEET_ID"     # the Sheet's ID from its URL
RAW_TAB_NAME         = "funnelio_export"          # input tab (Funnel.io dump)
OUTPUT_TAB_NAME      = "fatigue_alerts"           # output tab (results)

# Per-client column overrides. Start from DEFAULT_COLUMN_MAP and rename
# only what differs in this client's Funnel.io schema.
CLIENT_COLUMN_MAP = {
    **DEFAULT_COLUMN_MAP,
    # Examples (uncomment / edit as needed):
    # "spend":       "Cost",
    # "conversions": "Purchases",
}

# Fatigue thresholds. Match what the account manager calibrated in the UI.
THRESHOLDS = {
    "window_days":       7,
    "freq_increase_pct": 15,
    "ctr_decrease_pct":  20,
    "cpa_increase_pct":  25,
    "min_impressions":   1000,
}


def main() -> None:
    # 1. Authenticate
    gc = gspread.service_account(filename=SERVICE_ACCOUNT_FILE)
    sh = gc.open_by_key(SHEET_ID)

    # 2. Pull raw export
    raw_ws = sh.worksheet(RAW_TAB_NAME)
    df = get_as_dataframe(raw_ws, evaluate_formulas=True).dropna(how="all")

    # 3. Detect fatigue
    fatigued = detect_creative_fatigue(
        df=df,
        column_map=CLIENT_COLUMN_MAP,
        **THRESHOLDS,
    )

    # 4. Write results
    try:
        out_ws = sh.worksheet(OUTPUT_TAB_NAME)
    except gspread.WorksheetNotFound:
        out_ws = sh.add_worksheet(title=OUTPUT_TAB_NAME, rows=1000, cols=20)

    out_ws.clear()
    set_with_dataframe(out_ws, fatigued)
    print(f"✅ Wrote {len(fatigued)} fatigued ads to '{OUTPUT_TAB_NAME}'.")


if __name__ == "__main__":
    main()
