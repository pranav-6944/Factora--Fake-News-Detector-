import os
import requests
from credibility_engine import compute_credibility

# Lazy-loaded local model/tokenizer (used if running locally with PyTorch)
_model = None
_tokenizer = None


def _load_local_model():
    """Attempt to load local PyTorch BERT model if available."""
    global _model, _tokenizer
    if _model is None:
        try:
            from transformers import DistilBertTokenizerFast, DistilBertForSequenceClassification
            base = os.path.dirname(os.path.abspath(__file__))
            model_path = os.path.join(base, "bert_model")
            tokenizer_path = os.path.join(base, "bert_tokenizer")
            if os.path.isfile(os.path.join(model_path, "pytorch_model.bin")):
                _model = DistilBertForSequenceClassification.from_pretrained(model_path)
                _tokenizer = DistilBertTokenizerFast.from_pretrained(tokenizer_path)
                _model.eval()
                print("predict_bert: Local BERT model loaded successfully.")
        except Exception as e:
            print(f"predict_bert: Local model not loaded: {e}")
            _model = None
            _tokenizer = None
    return _model, _tokenizer


def predict_hf_api(text: str):
    """
    Query HuggingFace Serverless Inference API.
    Supports HF_API_KEY, HF_TOKEN, or HUGGINGFACE_TOKEN env variables.
    """
    token = os.environ.get("HF_API_KEY") or os.environ.get("HF_TOKEN") or os.environ.get("HUGGINGFACE_TOKEN")
    repo = os.environ.get("HF_MODEL_REPO", "pranavlamkhade/factora-fake-news-detector")
    
    urls = [
        f"https://router.huggingface.co/hf-inference/v1/models/{repo}",
        f"https://api-inference.huggingface.co/models/{repo}"
    ]
    
    headers = {"Content-Type": "application/json"}
    if token:
        headers["Authorization"] = f"Bearer {token}"

    for url in urls:
        try:
            r = requests.post(url, json={"inputs": text}, headers=headers, timeout=8)
            if r.status_code == 200:
                data = r.json()
                # Parse HF classification output format: [[{'label': 'LABEL_1', 'score': 0.95}, ...]]
                if isinstance(data, list) and len(data) > 0:
                    preds = data[0] if isinstance(data[0], list) else data
                    if isinstance(preds, list) and len(preds) > 0:
                        top = max(preds, key=lambda x: x.get("score", 0))
                        lbl = str(top.get("label", "")).upper()
                        score = float(top.get("score", 0.5)) * 100
                        
                        # Map labels: LABEL_1 / REAL -> REAL, LABEL_0 / FAKE -> FAKE
                        verdict = "REAL" if ("1" in lbl or "REAL" in lbl or "TRUE" in lbl) else "FAKE"
                        return verdict, round(score, 2)
        except Exception as e:
            print(f"HF API check error ({url}): {e}")

    return None


def predict_news(text: str):
    """
    Multi-tier news credibility prediction:
    1. HuggingFace Serverless Inference API (Fast, 0 MB server RAM)
    2. Local PyTorch Model (if model files exist locally)
    3. Credibility Engine Fallback (Linguistic + Clickbait + Source scoring)
    Returns: (verdict, confidence) e.g. ("REAL", 88.5)
    """
    text = (text or "").strip()
    if not text:
        return "FAKE", 50.0

    # Tier 1: Hugging Face Inference API
    hf_res = predict_hf_api(text)
    if hf_res is not None:
        verdict, confidence = hf_res
        return verdict, confidence

    # Tier 2: Local PyTorch Model
    model, tokenizer = _load_local_model()
    if model is not None and tokenizer is not None:
        try:
            import torch
            inputs = tokenizer(text, return_tensors="pt", padding=True, truncation=True, max_length=512)
            with torch.no_grad():
                outputs = model(**inputs)
            probs = torch.nn.functional.softmax(outputs.logits, dim=1)
            confidence = float(probs.max()) * 100
            prediction = torch.argmax(probs, dim=1).item()
            verdict = "REAL" if prediction == 1 else "FAKE"
            return verdict, round(confidence, 2)
        except Exception as e:
            print(f"Local inference error: {e}")

    # Tier 3: Credibility Engine Fallback
    cred = compute_credibility(text, bert_confidence=50.0, bert_prediction="REAL")
    verdict = cred.get("verdict", "REAL")
    confidence = cred.get("credibility_score", 50.0)
    return verdict, round(confidence, 2)


# 🧪 Test CLI
if __name__ == "__main__":
    t = input("Enter news headline: ")
    verdict, conf = predict_news(t)
    print(f"\nPrediction: {verdict}")
    print(f"Confidence: {conf}%")
