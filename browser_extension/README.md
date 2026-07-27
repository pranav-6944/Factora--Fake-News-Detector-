# FacTora Browser Extension

> **Real-time AI fake news detection** right in your browser — powered by the FacTora Flask backend.

---

## Features

| Feature | Description |
|---|---|
| 🔍 **Popup Analyzer** | Type or paste any headline and get an instant credibility score |
| ✨ **Grab from Page** | One-click to extract the `<h1>` headline from the current tab |
| 🏷️ **Auto-badge Headlines** | Automatically adds FacTora badges next to every headline on the page |
| 📊 **Factor Breakdown** | See AI model score, linguistic signal score, and source reliability |
| 🌐 **Source Panel** | Inline Wikipedia excerpt and trust badge for the article's domain |
| 💾 **Result Cache** | Analyzed headlines are cached per-session to avoid duplicate calls |

---

## Prerequisites

- **Google Chrome** (or any Chromium-based browser)
- **FacTora Flask app** running locally on port 5000

  ```powershell
  # In the FacTora project folder, activate venv first:
  cd "c:\Users\prana_b2roblq\Downloads\Main Projects\FacTora"
  venv\Scripts\Activate.ps1
  python app.py
  ```

---

## Installation

### Step 1 – Open Extensions Page

Open Chrome and navigate to:
```
chrome://extensions/
```

### Step 2 – Enable Developer Mode

Toggle **"Developer mode"** in the top-right corner of the extensions page.

### Step 3 – Load the Extension

Click **"Load unpacked"** and select the `browser_extension` folder:

```
c:\Users\prana_b2roblq\Downloads\Main Projects\FacTora\browser_extension\
```

### Step 4 – Start Using It

- Visit any news site (BBC, CNN, Reuters, etc.)
- FacTora **🔍 FacTora** badges will appear next to headlines automatically
- **Click a badge** → see the full credibility breakdown tooltip
- **Click the extension icon** → use the popup to analyze any custom headline

---

## How It Works

```
Browser Extension
      │
      ▼  POST /api/credibility-score  (no auth needed)
FacTora Flask Backend (localhost:5000)
      │
      ├─ DistilBERT → REAL/FAKE + confidence
      ├─ Linguistic Engine → clickbait / conspiracy signals
      └─ Source Engine → trust level, Wikipedia, heuristics
      │
      ▼  JSON result
Extension renders:
  • Credibility score (0–100) with letter grade (A–F)
  • Factor bars (AI Model 50% · Language 30% · Source 20%)
  • Trust badge + linguistic signal pills
```

---

## API Endpoints Used

| Endpoint | Auth | Purpose |
|---|---|---|
| `POST /api/credibility-score` | None | Public score for extension |
| `POST /api/verify-source` | None | Domain trust lookup |
| `POST /api/analyze` | Login required | Full analysis (web app) |

---

## Permissions

| Permission | Reason |
|---|---|
| `activeTab` | Read the URL and title of the current tab |
| `scripting` | Inject content script to badge headlines |
| `storage` | Save user settings (API base URL, enable/disable) |
| `host_permissions: localhost:5000` | Communicate with local FacTora server |

---

## Known Limitations

- **Requires local server**: The extension calls `http://localhost:5000`. The FacTora app must be running.  
- **No persistent login**: The public `/api/credibility-score` endpoint requires no auth, so extension results are not saved to your FacTora history.
- **Dynamic pages**: MutationObserver watches for new content, but very aggressive SPAs may need a page refresh.

---

## Files

```
browser_extension/
├── manifest.json     ← Chrome Manifest V3 config
├── popup.html        ← Extension popup UI
├── popup.css         ← Popup styles (FacTora dark theme)
├── popup.js          ← Popup logic + API calls
├── content.js        ← Page headline scanner + tooltips
├── background.js     ← Service worker (Manifest V3)
└── icons/
    ├── icon16.png
    ├── icon48.png
    └── icon128.png
```
