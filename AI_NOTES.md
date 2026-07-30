# FacTora Project - AI Notes

## Project Overview
- **Type**: Flask web app for fake news detection using DistilBERT
- **Repo**: https://github.com/pranav-6944/Factora--Fake-News-Detector-
- **Live URL**: https://factora-lljj.onrender.com
- **Render Service ID**: `srv-d9llhtmgekts73c5i25g`
- **Main file**: `app.py`
- **Python version**: 3.13.2 (local), 3.11.9 (Render runtime)

## Key Files & Line References
- `app.py:1-4` – imports + dotenv load
- `app.py:21-50` – `ensure_bert_model()` HuggingFace auto-download
- `app.py:53` – Flask app init, SECRET_KEY from env
- `app.py:64` – NEWS_API_KEY from env
- `app.py:245-254` – Resilient BERT model loading (try/except)
- `app.py:272`, `1005`, `1058` – 503 fallback guards for missing model
- `config.py` – DB paths (database/, models/) with auto `os.makedirs`
- `credibility_engine.py` – Multi-factor scoring (BERT 50%, linguistic 30%, source 20%)
- `source_verifier.py` – Domain trust lists + Wikipedia enrichment
- `predict_bert.py` – Lazy-loaded BERT prediction utility

## Sensitive Items (DO NOT COMMIT)
- NEWS_API_KEY: stored in `.env` and Render env vars
- SECRET_KEY: stored in `.env` and Render env vars
- `database/*.db` – user auth data, predictions, feedback
- `bert_model/` – 268MB pytorch_model.bin + checkpoints (hosted on HF Hub)
- `bert_tokenizer/` – tokenizer files

## Deployment (Render.com)
- Status: **LIVE**
- Service URL: https://factora-lljj.onrender.com
- `render.yaml` – blueprint config
- `Procfile` – gunicorn with 120s timeout
- `runtime.txt` – python-3.11.9
- PyTorch: CPU-only build (`torch==2.2.2+cpu`)
- HF Hub: Model repo `pranavlamkhade/factora-fake-news-detector`

## Browser Extension
- Chrome Manifest V3 (`browser_extension/`)
- `popup.js:6` – `DEPLOYED_URL = 'https://factora-lljj.onrender.com'`
- `manifest.json:44` – includes `*.onrender.com` in host_permissions
