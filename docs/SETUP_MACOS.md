# macOS Setup Guide

Tested on macOS 14+ (Apple Silicon and Intel). Should also work on Linux with the same steps.

---

## 1. Install Python 3.10+

macOS ships with an outdated system Python. Install a current version via Homebrew:

```bash
# Install Homebrew if you don't have it
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"

# Install Python
brew install python

# Verify
python3 --version    # should be 3.10 or newer
```

Alternative: download the official installer from [python.org](https://python.org/downloads).

---

## 2. Set Up the Project

```bash
# Navigate to the project folder
cd path/to/creative-fatigue-monitor

# Create an isolated virtual environment
python3 -m venv .venv
source .venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

The venv keeps these packages out of your system Python. You'll see `(.venv)` in your prompt when it's active.

---

## 3. Launch

```bash
streamlit run fatigue_monitor.py
```

Streamlit will:
- Start a local server on port 8501
- Auto-open your default browser to `http://localhost:8501`
- Print the URL in the terminal in case it doesn't auto-open

Any modern browser works — Safari, Chrome, Arc, Firefox, Edge. No browser config or extensions needed.

---

## 4. Stopping and Re-running

- **Stop the server:** `Ctrl + C` in the terminal.
- **Restart later:**
  ```bash
  cd path/to/creative-fatigue-monitor
  source .venv/bin/activate
  streamlit run fatigue_monitor.py
  ```
- **Edit the script while running:** Streamlit auto-detects file changes. Click "Rerun" in the top-right of the browser, or set it to auto-rerun in Settings.

---

## Common Gotchas

| Symptom | Fix |
|---|---|
| `command not found: streamlit` | Your venv isn't active. Run `source .venv/bin/activate` again. The prompt should show `(.venv)`. |
| `Port 8501 already in use` | Another Streamlit instance is running. Either kill it (`lsof -ti:8501 \| xargs kill`) or launch on a different port: `streamlit run fatigue_monitor.py --server.port 8502`. |
| First-run email prompt | Streamlit asks for an email on first launch. Press Enter to skip; it's optional telemetry. |
| Apple Silicon (M1/M2/M3/M4) | No special steps — Homebrew's Python and all three dependencies have native arm64 wheels. |
| `ModuleNotFoundError` | Either the venv isn't active, or you skipped `pip install -r requirements.txt`. Re-run both. |
