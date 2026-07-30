# FacTora Project - AI Notes

## Project Overview
- **Type**: Flask web app for fake news detection using DistilBERT
- **Repo**: https://github.com/pranav-6944/Factora--Fake-News-Detector-
- **Main file**: `app.py` (~1145 lines after edits)
- **Python version**: 3.13.2 (local), target 3.11.9 (Render)

## Key Files & Line References
- `app.py:1-4` – imports + dotenv load
- `app.py:19-50` – `ensure_bert_model()` HuggingFace auto-download
- `app.py:53` – Flask app init, SECRET_KEY from env
- `app.py:63` – NEWS_API_KEY from env
- `app.py:1138-1145` – `__main__` with PORT env variable
- `config.py` – DB paths (database/, models/)
- `credibility_engine.py` – Multi-factor scoring (BERT 50%, linguistic 30%, source 20%)
- `source_verifier.py` – Domain trust lists + Wikipedia enrichment
- `predict_bert.py` – Standalone BERT prediction utility

## Sensitive Items (DO NOT COMMIT)
- NEWS_API_KEY: stored in `.env` (gitignored)
- SECRET_KEY: stored in `.env` (gitignored)
- `database/*.db` – user auth data, predictions, feedback
- `bert_model/` – 268MB pytorch_model.bin + 2.4GB checkpoints
- `bert_tokenizer/` – tokenizer files

## Deployment (Render.com)
- `render.yaml` – blueprint config
- `Procfile` – gunicorn with 120s timeout
- BERT model: auto-downloads from HuggingFace Hub (`pranavlamkhade/factora-fake-news-detector`)
- HF Hub: Model + tokenizer + model card successfully pushed (2026-07-30)
- HF Username: `pranavlamkhade` (NOT pranavlamkhade21)
- `push_to_hub.py` – script to re-push model if needed

## Git Status
- Pushed: 2026-07-27, commit 690ca52
- 79 files committed
- Force pushed to main branch
- `.gitignore` directory issue fixed (was a dir, now proper file)

## Browser Extension
- Chrome Manifest V3
- `popup.js:6` – DEPLOYED_URL needs update after Render deploy
- `manifest.json:44` – includes `*.onrender.com` in host_permissions
