import os
import requests
from credibility_engine import compute_credibility

# Lazy-loaded model & tokenizer
_model = None
_tokenizer = None


def _load_model():
    """Load DistilBERT model directly from Hugging Face repository or local folder."""
    global _model, _tokenizer
    if _model is None:
        base = os.path.dirname(os.path.abspath(__file__))
        local_model_path = os.path.join(base, "bert_model")
        local_tokenizer_path = os.path.join(base, "bert_tokenizer")

        # 1. Try local folder if exists
        if os.path.isfile(os.path.join(local_model_path, "pytorch_model.bin")):
            try:
                from transformers import DistilBertTokenizerFast, DistilBertForSequenceClassification
                _tokenizer = DistilBertTokenizerFast.from_pretrained(local_tokenizer_path)
                _model = DistilBertForSequenceClassification.from_pretrained(local_model_path)
                _model.eval()
                print("predict_bert: Loaded local model successfully.")
                return _model, _tokenizer
            except Exception as e:
                print(f"predict_bert: Local load error: {e}")

        # 2. Load directly from HuggingFace Hub repo
        try:
            from transformers import AutoTokenizer, AutoModelForSequenceClassification
            repo = os.environ.get("HF_MODEL_REPO", "pranavlamkhade/factora-fake-news-detector")
            print(f"predict_bert: Loading model from Hugging Face repo '{repo}'...")
            _tokenizer = AutoTokenizer.from_pretrained(repo)
            _model = AutoModelForSequenceClassification.from_pretrained(repo)
            _model.eval()
            print(f"predict_bert: Loaded Hugging Face model '{repo}' successfully.")
        except Exception as e:
            print(f"predict_bert: HF repo load error: {e}")
            _model = None
            _tokenizer = None

    return _model, _tokenizer


def predict_news(text: str):
    """
    Predict fake vs real news using DistilBERT model.
    Returns: (verdict, confidence) e.g. ("REAL", 94.2) or ("FAKE", 88.5)
    """
    text = (text or "").strip()
    if not text:
        return "FAKE", 50.0

    model, tokenizer = _load_model()
    if model is not None and tokenizer is not None:
        try:
            import torch
            inputs = tokenizer(text, return_tensors="pt", padding=True, truncation=True, max_length=512)
            with torch.no_grad():
                outputs = model(**inputs)
            probs = torch.nn.functional.softmax(outputs.logits, dim=1)
            predicted_class = torch.argmax(probs, dim=1).item()
            confidence = float(probs[0][predicted_class]) * 100
            
            verdict = "REAL" if predicted_class == 1 else "FAKE"
            return verdict, round(confidence, 2)
        except Exception as e:
            print(f"predict_bert: Inference error: {e}")

    # Fallback to credibility engine if model loading fails
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
