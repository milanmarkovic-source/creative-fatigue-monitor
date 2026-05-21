# Adapting to Your Funnel.io Export

The tool ships with default column names (`Date`, `Ad ID`, `Impressions`, etc.) that probably don't match your Funnel.io export. Two ways to fix that: live in the UI, or permanently in code.

## Method 1: Edit field mapping live in the UI (no code change)

**Use this for:** one-off runs, demos, ad-hoc analyses, or testing a new client's export before committing to changes.

1. Launch the app: `streamlit run fatigue_monitor.py`
2. Open your Funnel.io CSV in Excel or a text editor — note the **exact** column headers (case-sensitive, including spaces)
3. In the app's left sidebar, scroll to **Column Mapping**
4. For each canonical field on the left, type your CSV's column name on the right

### Example: Funnel.io export uses different naming

Suppose your Funnel.io CSV has these headers:

```
Day, Creative Name, Creative ID, Impr., Unique Users, Link Clicks, Cost, Purchases
```

Map them in the sidebar like this:

| Canonical (left, fixed) | Your CSV column (right, editable) |
|---|---|
| `date` | `Day` |
| `ad_id` | `Creative ID` |
| `ad_name` | `Creative Name` |
| `impressions` | `Impr.` |
| `reach` | `Unique Users` |
| `clicks` | `Link Clicks` |
| `spend` | `Cost` |
| `conversions` | `Purchases` |

The app will rename your columns internally and run the detection without touching your file. If you typed a column name that doesn't exist in the CSV, the app shows a clear error message listing what's missing.

**Pros:** instant, no code changes, judge-friendly during demo
**Cons:** mapping resets when you restart the app — you have to retype it each session

---

## Method 2: Permanent mapping in code

**Use this for:** your own clients you analyze repeatedly, the headless pipeline, or to set sensible defaults across your team.

Open `fatigue_monitor.py` and find the `DEFAULT_COLUMN_MAP` near the top:

```python
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
```

Edit the **right-hand values** (the strings in quotes) to match your CSV. Do **not** change the left-hand keys — those are canonical internal names the detection logic depends on.

### Example: Your team always uses these Funnel.io columns

```python
DEFAULT_COLUMN_MAP = {
    "date":        "Day",
    "ad_id":       "Creative ID",
    "ad_name":     "Creative Name",
    "impressions": "Impr.",
    "reach":       "Unique Users",
    "clicks":      "Link Clicks",
    "spend":       "Cost",
    "conversions": "Purchases",
}
```

Save, restart the app. The sidebar now shows your column names as defaults, and you (or any teammate) can upload Funnel.io exports without re-mapping every time.

---

## Method 3: Per-client mapping in the headless pipeline

`pipeline_fatigue.py` has a dedicated `CLIENT_COLUMN_MAP` variable for this exact case. Copy the default, override only what differs:

```python
from fatigue_monitor import DEFAULT_COLUMN_MAP

# Client A: standard naming
CLIENT_A_MAP = {**DEFAULT_COLUMN_MAP}

# Client B: uses "Cost" instead of "Spend"
CLIENT_B_MAP = {
    **DEFAULT_COLUMN_MAP,
    "spend":       "Cost",
    "conversions": "Purchases",
}

# Client C: completely different naming
CLIENT_C_MAP = {
    "date":        "Day",
    "ad_id":       "Creative ID",
    "ad_name":     "Creative Name",
    "impressions": "Impr.",
    "reach":       "Unique Users",
    "clicks":      "Link Clicks",
    "spend":       "Cost",
    "conversions": "Purchases",
}
```

Then in the pipeline loop, route each client to its map. For scale, store these in a config table (a Sheet, a JSON file, or environment variables) keyed by `account_id`.

---

## Adding or renaming canonical fields

If you want to add a new metric to the detection logic (say, ROAS or hook rate), you need to change **three** places — but they're easy to find:

1. **`DEFAULT_COLUMN_MAP`** in `fatigue_monitor.py` — add your new canonical key → source column entry
2. **`_aggregate_window()`** in the same file — add a `.agg()` entry summing your new field, plus a derived metric calculation if needed
3. **`detect_creative_fatigue()`** filter expression — add your new condition to the AND chain, and include the column in the returned DataFrame

Everything else (the UI sidebar, the error messages, the CSV export) flows automatically from `DEFAULT_COLUMN_MAP`.

---

## Quick reference: canonical field meanings

The eight canonical fields the detection logic relies on:

| Canonical name | What it represents | Used to compute |
|---|---|---|
| `date` | Day of the metric row | Window membership |
| `ad_id` | Stable unique ad identifier | Grouping across days |
| `ad_name` | Human-readable label | Reporting only |
| `impressions` | Times ad was served | Frequency, CTR, QC floor |
| `reach` | Unique users reached | Frequency (impressions ÷ reach) |
| `clicks` | Clicks received | CTR (clicks ÷ impressions) |
| `spend` | Cost incurred | CPA (spend ÷ conversions) |
| `conversions` | Conversions attributed | CPA |

If your source has different definitions (e.g., "Link Clicks" vs "All Clicks", "Reach" vs "Estimated Unique Users", "Purchases" vs "Total Conversions"), pick whichever most closely matches the intended metric. Be consistent across the team — different definitions across clients break cross-client comparisons.
