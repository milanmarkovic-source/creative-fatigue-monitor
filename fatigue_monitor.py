"""
Creative Fatigue & Algorithm Decay Monitor
==========================================
Detects fatigued active ads by comparing the most recent N-day window
against the immediately preceding N-day window.

Fatigue signature (ALL three must be true on the same ad):
    1. Frequency  ↑ by more than X%
    2. CTR        ↓ by more than Y%
    3. CPA        ↑ by more than Z%

Designed for: Acadia.io Morning Account Checks — AI agent sub-module.
The core function `detect_creative_fatigue()` is UI-agnostic and can be
imported directly into a Google Sheets / BigQuery / Airflow pipeline.
"""

from datetime import datetime, timedelta

import numpy as np
import pandas as pd
import streamlit as st


# =============================================================================
# UNIVERSAL CONFIGURATION
# =============================================================================
# Map canonical internal field names (LHS) → your CSV's column names (RHS).
# Override in the Streamlit sidebar, or edit here for a headless pipeline run.
DEFAULT_COLUMN_MAP = {
    "date":        "Date",
    "ad_id":       "Ad ID",
    "ad_name":     "Ad Name",
    "impressions": "Impressions",
    "reach":       "Reach",
    "clicks":      "Clicks",
    "spend":       "Spend",
    "conversions": "Conversions",
}
REQUIRED_COLS = list(DEFAULT_COLUMN_MAP.keys())


# =============================================================================
# CORE LOGIC  (UI-independent — safe to import from any pipeline)
# =============================================================================
def _apply_column_map(df: pd.DataFrame, column_map: dict) -> pd.DataFrame:
    """Rename incoming CSV columns to canonical internal names. Validates presence."""
    missing = [src for src in column_map.values() if src not in df.columns]
    if missing:
        raise ValueError(f"Missing mapped columns in input data: {missing}")
    inverse = {v: k for k, v in column_map.items()}
    return df.rename(columns=inverse)[REQUIRED_COLS].copy()


def _aggregate_window(df: pd.DataFrame, start: pd.Timestamp, end: pd.Timestamp) -> pd.DataFrame:
    """Sum metrics per ad across [start, end] and derive frequency, CTR, CPA."""
    mask = (df["date"] >= start) & (df["date"] <= end)
    agg = (
        df.loc[mask]
        .groupby(["ad_id", "ad_name"], as_index=False)
        .agg(
            impressions=("impressions", "sum"),
            reach=("reach", "sum"),
            clicks=("clicks", "sum"),
            spend=("spend", "sum"),
            conversions=("conversions", "sum"),
        )
    )
    # Safe divides — return NaN when the denominator is zero so the
    # downstream comparison (>, <) cleanly excludes the row.
    # NOTE: summing daily reach overstates true unique reach but is a
    # consistent approximation; the relative window-over-window delta
    # is what drives the fatigue signal.
    agg["frequency"] = np.where(agg["reach"] > 0, agg["impressions"] / agg["reach"], np.nan)
    agg["ctr"]       = np.where(agg["impressions"] > 0, agg["clicks"] / agg["impressions"], np.nan)
    agg["cpa"]       = np.where(agg["conversions"] > 0, agg["spend"] / agg["conversions"], np.nan)
    return agg


def detect_creative_fatigue(
    df: pd.DataFrame,
    window_days: int = 7,
    freq_increase_pct: float = 15.0,
    ctr_decrease_pct: float = 20.0,
    cpa_increase_pct: float = 25.0,
    min_impressions: int = 1000,
    column_map: dict | None = None,
    reference_date: pd.Timestamp | None = None,
) -> pd.DataFrame:
    """
    Return a DataFrame of ads matching the 3-part fatigue signature.

    Parameters
    ----------
    df                : raw input DataFrame, columns named per `column_map`.
    window_days       : length (in days) of EACH comparison window.
    freq_increase_pct : minimum frequency rise (%) required to flag.
    ctr_decrease_pct  : minimum CTR drop      (%) required to flag.
    cpa_increase_pct  : minimum CPA rise      (%) required to flag.
    min_impressions   : QC floor — current-window impressions must meet/exceed this.
    column_map        : mapping of canonical name → CSV column name.
    reference_date    : last day of the CURRENT window. Defaults to max(date).
    """
    column_map = column_map or DEFAULT_COLUMN_MAP
    df = _apply_column_map(df, column_map)
    df["date"] = pd.to_datetime(df["date"])

    # Define two equal-length windows, back-to-back.
    if reference_date is None:
        reference_date = df["date"].max()
    reference_date  = pd.to_datetime(reference_date)
    current_end     = reference_date
    current_start   = current_end   - timedelta(days=window_days - 1)
    previous_end    = current_start - timedelta(days=1)
    previous_start  = previous_end  - timedelta(days=window_days - 1)

    current  = _aggregate_window(df, current_start,  current_end)
    previous = _aggregate_window(df, previous_start, previous_end)

    # Fatigue requires the ad to exist in BOTH windows — inner join.
    merged = current.merge(previous, on=["ad_id", "ad_name"],
                           suffixes=("_curr", "_prev"), how="inner")

    # STRICT QC — drop low-volume ads to suppress noise-driven false positives.
    merged = merged[merged["impressions_curr"] >= min_impressions]

    # Period-over-period deltas (%).
    def pct_delta(curr, prev):
        return np.where(prev > 0, (curr - prev) / prev * 100.0, np.nan)

    merged["freq_delta_pct"] = pct_delta(merged["frequency_curr"], merged["frequency_prev"])
    merged["ctr_delta_pct"]  = pct_delta(merged["ctr_curr"],       merged["ctr_prev"])
    merged["cpa_delta_pct"]  = pct_delta(merged["cpa_curr"],       merged["cpa_prev"])

    # The 3-part fatigue signature.
    flagged = merged[
        (merged["freq_delta_pct"] >  freq_increase_pct) &
        (merged["ctr_delta_pct"]  < -ctr_decrease_pct)  &
        (merged["cpa_delta_pct"]  >  cpa_increase_pct)
    ].copy()

    return (
        flagged[[
            "ad_id", "ad_name",
            "impressions_curr", "impressions_prev",
            "frequency_curr", "frequency_prev", "freq_delta_pct",
            "ctr_curr", "ctr_prev", "ctr_delta_pct",
            "cpa_curr", "cpa_prev", "cpa_delta_pct",
            "spend_curr", "conversions_curr",
        ]]
        .sort_values("cpa_delta_pct", ascending=False)
        .reset_index(drop=True)
    )


# =============================================================================
# TEST DATA GENERATOR
# =============================================================================
def generate_mock_data(days: int = 60, seed: int = 42) -> pd.DataFrame:
    """
    60-day daily ad-level dataset containing three archetypes:
        Healthy_*  — stable across all windows (should NOT flag).
        LowVol_*   — sub-threshold impressions (must be filtered by QC).
        Fatigued_* — metrics decay sharply in the most recent 7 days.
    """
    rng = np.random.default_rng(seed)
    end_date = pd.Timestamp(datetime.utcnow().date())
    dates = pd.date_range(end=end_date, periods=days, freq="D")

    # (id, name, base_imp, base_ctr, base_freq, base_cpa, is_fatigued)
    archetypes = [
        ("AD_001", "Healthy_Carousel_A",    2500, 0.020, 1.5, 25.0, False),
        ("AD_002", "Healthy_Video_B",       3200, 0.025, 1.8, 22.0, False),
        ("AD_003", "Healthy_StaticImage_C", 2800, 0.018, 1.6, 28.0, False),
        ("AD_004", "LowVol_Test_D",           80, 0.022, 1.4, 30.0, False),
        ("AD_005", "LowVol_DarkPost_E",      120, 0.019, 1.3, 35.0, False),
        ("AD_006", "Fatigued_UGC_F",        3500, 0.028, 1.4, 18.0, True),
        ("AD_007", "Fatigued_Promo_G",      4200, 0.030, 1.5, 20.0, True),
    ]

    rows = []
    for ad_id, ad_name, base_imp, base_ctr, base_freq, base_cpa, is_fatigued in archetypes:
        for i, date in enumerate(dates):
            days_from_end = len(dates) - 1 - i
            in_current_window = days_from_end < 7

            # Fatigued ads degrade ONLY in the most recent 7 days.
            if is_fatigued and in_current_window:
                imp_mult, freq_mult, ctr_mult, cpa_mult = 1.20, 1.45, 0.65, 1.55
            else:
                imp_mult = freq_mult = ctr_mult = cpa_mult = 1.0

            noise = lambda s=0.05: rng.normal(1.0, s)
            impressions = max(0, int(base_imp * imp_mult * noise(0.08)))
            frequency   = max(0.1, base_freq * freq_mult * noise(0.05))
            reach       = max(1, int(impressions / frequency))
            ctr         = max(0.0001, base_ctr * ctr_mult * noise(0.10))
            clicks      = max(0, int(impressions * ctr))
            cpa         = max(0.01, base_cpa * cpa_mult * noise(0.10))
            conversions = max(0, int(clicks * rng.uniform(0.04, 0.10)))
            spend       = round(conversions * cpa if conversions > 0 else impressions * 0.005, 2)

            rows.append({
                "Date": date.date(), "Ad ID": ad_id, "Ad Name": ad_name,
                "Impressions": impressions, "Reach": reach, "Clicks": clicks,
                "Spend": spend, "Conversions": conversions,
            })
    return pd.DataFrame(rows)


# =============================================================================
# STREAMLIT UI
# =============================================================================
def run_app() -> None:
    st.set_page_config(page_title="Creative Fatigue Monitor", page_icon="📉", layout="wide")
    st.title("📉 Creative Fatigue & Algorithm Decay Monitor")
    st.caption(
        "Flags ads matching the 3-part fatigue signature: "
        "rising Frequency, falling CTR, rising CPA — current window vs. preceding window."
    )

    # ---------- SIDEBAR ----------
    with st.sidebar:
        st.header("⚙️ Configuration")
        window_days = st.selectbox("Comparison Window (days)", [7, 14, 30], index=0)

        st.subheader("Fatigue Thresholds")
        x = st.slider("Frequency increase > X%", 1, 100, 15)
        y = st.slider("CTR decrease > Y%",       1, 100, 20)
        z = st.slider("CPA increase > Z%",       1, 200, 25)

        st.subheader("Quality Control")
        min_impressions = st.number_input(
            "Min impressions in current window", min_value=0, value=1000, step=100,
            help="Hard floor to suppress false positives from low-volume noise."
        )

        st.subheader("Column Mapping")
        st.caption("Match canonical fields to your CSV's column names.")
        column_map = {
            k: st.text_input(k, value=v) for k, v in DEFAULT_COLUMN_MAP.items()
        }

    # ---------- DATA SOURCE ----------
    st.subheader("1. Load Data")
    c1, c2 = st.columns(2)
    with c1:
        uploaded = st.file_uploader("Upload CSV", type=["csv"])
    with c2:
        if st.button("🧪 Generate Mock Dataset (60 days)"):
            st.session_state["data"] = generate_mock_data(days=60)
            st.success("Mock dataset loaded.")

    if uploaded is not None:
        st.session_state["data"] = pd.read_csv(uploaded)

    if "data" not in st.session_state:
        st.info("Upload a CSV or click **Generate Mock Dataset** to begin.")
        st.stop()

    df = st.session_state["data"]
    st.write(f"**Rows loaded:** {len(df):,}")
    with st.expander("Preview raw data"):
        st.dataframe(df.head(20), use_container_width=True)

    # ---------- DETECTION ----------
    st.subheader("2. Fatigued Ads")
    try:
        fatigued = detect_creative_fatigue(
            df=df,
            window_days=window_days,
            freq_increase_pct=x,
            ctr_decrease_pct=y,
            cpa_increase_pct=z,
            min_impressions=min_impressions,
            column_map=column_map,
        )
    except ValueError as e:
        st.error(str(e)); st.stop()

    # Show the two windows being compared, for transparency.
    try:
        df_dates = pd.to_datetime(df[column_map["date"]])
        ref = df_dates.max()
        cs, ce = ref - timedelta(days=window_days - 1), ref
        ps, pe = cs - timedelta(days=window_days), cs - timedelta(days=1)
        st.caption(f"**Current window:** {cs.date()} → {ce.date()}   |   "
                   f"**Previous window:** {ps.date()} → {pe.date()}")
    except Exception:
        pass

    st.metric("Ads flagged as fatigued", len(fatigued))

    if fatigued.empty:
        st.success("✅ No fatigue signatures detected with the current thresholds.")
    else:
        display = fatigued.copy()
        for c in ["frequency_curr", "frequency_prev", "ctr_curr", "ctr_prev",
                  "cpa_curr", "cpa_prev", "freq_delta_pct", "ctr_delta_pct", "cpa_delta_pct"]:
            display[c] = display[c].round(2)
        st.dataframe(display, use_container_width=True)
        st.download_button(
            "⬇️ Download flagged ads (CSV)",
            data=display.to_csv(index=False).encode("utf-8"),
            file_name="fatigued_ads.csv", mime="text/csv",
        )


if __name__ == "__main__":
    run_app()