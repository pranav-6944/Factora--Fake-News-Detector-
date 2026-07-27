# FacTora – AI-Powered Fake News Detection System 🧠📰

![Python](https://img.shields.io/badge/Python-3.9+-blue?logo=python&logoColor=white)
![Flask](https://img.shields.io/badge/Flask-2.3-green?logo=flask)
![PyTorch](https://img.shields.io/badge/PyTorch-2.2-red?logo=pytorch)
![License](https://img.shields.io/badge/License-MIT-yellow)

**FacTora** is an AI-powered full-stack fake news detection web application built with Python Flask and a fine-tuned DistilBERT NLP model. It provides real-time prediction, multi-factor credibility scoring, source verification, analytics, and a browser extension for detecting misinformation.

Developed during a virtual internship at **Pinnacle Labs**.

---

## 🚀 Key Features

- 🤖 **AI-Powered Prediction** – Fine-tuned DistilBERT model trained on the LIAR dataset for binary classification (FAKE or REAL)
- 🎯 **Multi-Factor Credibility Engine** – Composite score from BERT confidence (50%), linguistic analysis (30%), and source reliability (20%)
- 🔍 **Source Verification** – Cross-references domains against trusted/unreliable lists with Wikipedia enrichment
- 🔐 **User Authentication** – Secure login/signup with hashed passwords using Flask-Login
- 📈 **Analytics Dashboard** – View total predictions, feedback accuracy, and interactive charts (Chart.js)
- 📂 **Prediction History** – Per-user history with search, filter, sort, and pagination
- 📰 **Live News Headlines** – Integrates with News API for real-time headline analysis
- 👍 **Feedback System** – Rate each prediction to help improve accuracy tracking
- 🧩 **Browser Extension** – Chrome extension to analyze any headline on the web
- 💾 **CSV Export** – Download prediction history in CSV format
- 🎨 **Modern UI** – Fully responsive with animated transitions and dark/light support

---

## 🧰 Tech Stack

| Layer | Technologies |
|-------|-------------|
| **Backend** | Python, Flask, Flask-Login, SQLite3, Gunicorn |
| **ML/AI** | HuggingFace Transformers, DistilBERT, PyTorch, scikit-learn |
| **Frontend** | HTML5, CSS3, JavaScript, Chart.js, Font Awesome |
| **Extension** | Chrome Manifest V3, Content Scripts |
| **Deployment** | Render.com, Gunicorn |

---

## 📁 Folder Structure

```
FacTora/
├── app.py                  # Flask backend (main application)
├── config.py               # Config file (DB paths, model locations)
├── credibility_engine.py   # Multi-factor credibility scoring
├── source_verifier.py      # Domain trust verification + Wikipedia
├── predict_bert.py         # BERT prediction utility
├── train_bert_liar.py      # BERT training script
├── requirements.txt        # Python dependencies
├── Procfile                # Gunicorn start command for Render
├── render.yaml             # Render.com deployment blueprint
├── .env.example            # Environment variable template
├── .gitignore              # Git exclusions
├── README.md               # This file
│
├── bert_model/             # Fine-tuned DistilBERT model (excluded from git)
├── bert_tokenizer/         # Tokenizer for DistilBERT (excluded from git)
├── database/               # SQLite DBs – auto-created on startup
├── liar_dataset/           # LIAR dataset (train.tsv, test.tsv, valid.tsv)
│
├── static/                 # CSS, JS, Images, Manifest
│   ├── css/
│   ├── js/
│   └── images/
│
├── templates/              # Jinja2 HTML templates
│   ├── base.html
│   ├── index.html
│   ├── dashboard.html
│   ├── history.html
│   ├── live_news.html
│   ├── settings.html
│   ├── help.html
│   └── ...
│
├── browser_extension/      # Chrome extension (Manifest V3)
│   ├── manifest.json
│   ├── popup.html / .js / .css
│   ├── content.js
│   ├── background.js
│   └── icons/
│
├── train/                  # Alternative training scripts
└── favicon_io/             # Favicon assets
```

---

## ⚙️ Setup Instructions

### 1️⃣ Clone the Repo
```bash
git clone https://github.com/pranav-6944/Factora--Fake-News-Detector-.git
cd Factora--Fake-News-Detector-
```

### 2️⃣ Create Virtual Environment
```bash
python -m venv venv

# Windows:
venv\Scripts\activate

# Mac/Linux:
source venv/bin/activate
```

### 3️⃣ Install Dependencies
```bash
pip install -r requirements.txt
```

### 4️⃣ Set Environment Variables
```bash
# Copy the example env file
cp .env.example .env

# Edit .env and add your keys:
# SECRET_KEY=your-random-secret-key
# NEWS_API_KEY=your-newsapi-org-key
```

### 5️⃣ Download / Train BERT Model

**Option A – Auto-download (Recommended):**
The app automatically downloads the model from HuggingFace Hub on first run.

**Option B – Train from scratch:**
```bash
# Download LIAR dataset if not present
# https://www.cs.ucsb.edu/~william/data/liar_dataset.zip
python train_bert_liar.py
```

### 6️⃣ Run the Web App
```bash
python app.py
```
Then open **http://localhost:5000**

---

## 🌐 Deploy on Render.com

1. Push code to GitHub (already done ✅)
2. Go to [render.com](https://render.com) → **New Web Service**
3. Connect your GitHub repository
4. Render auto-detects `render.yaml` – just add env variables:
   - `NEWS_API_KEY` → Your NewsAPI key
   - `SECRET_KEY` → Auto-generated
   - `HF_MODEL_REPO` → `pranav6944/factora-bert`
5. Deploy! 🚀

---

## 🧩 Browser Extension

1. Navigate to **chrome://extensions/**
2. Enable **Developer Mode**
3. Click **Load unpacked** → select the `browser_extension/` folder
4. Pin the FacTora extension to your toolbar
5. Click the extension icon on any news page to analyze headlines

> After deploying to Render, update `DEPLOYED_URL` in `browser_extension/popup.js` with your Render URL.

---

## 🔒 Security Notes

- ❌ Never commit `.env` files or hardcode API keys
- ✅ Use environment variables for all secrets
- ✅ Use HTTPS in production (Render provides this automatically)
- ✅ Use Gunicorn (not Flask dev server) in production
- ✅ Set `FLASK_DEBUG=false` in production

---

## 🧠 ML Model Details

| Property | Value |
|----------|-------|
| **Architecture** | DistilBERT (distilbert-base-uncased) |
| **Task** | Binary classification (FAKE / REAL) |
| **Dataset** | [LIAR dataset](https://www.cs.ucsb.edu/~william/data/liar_dataset.zip) |
| **Label Mapping** | FAKE = [pants-fire, false, barely-true], REAL = [half-true, mostly-true, true] |
| **Training** | 3 epochs, batch size 16, AdamW optimizer |

---

## 🗺️ Future Plans

- [x] Integrate BERT model
- [x] Browser extension
- [x] Multi-factor credibility engine
- [x] Source verification with Wikipedia
- [ ] Host on Render ← **You are here**
- [ ] Admin panel for feedback review
- [ ] Continuous retraining pipeline
- [ ] Mobile app (React Native)

---

## 👨‍💻 Developer

Built with 💪 by **Pranav** (CS Student, MIT Academy of Engineering)

🏢 Internship: **Pinnacle Labs**

📌 From frontend → backend → ML training → deployment — this is a solo build project.

Let's connect on [LinkedIn](https://linkedin.com) 🔗 and work on more cool stuff together! 🚀

---

## 📄 License

MIT License — open source for learning and non-commercial use.
PRs and contributions welcome!