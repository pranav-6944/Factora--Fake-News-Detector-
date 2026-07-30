import os
import joblib
from credibility_engine import compute_credibility

# Lazy-loaded lightweight ML model & vectorizer
_local_model = None
_local_vectorizer = None


def _load_ml_model():
    """Load lightweight TF-IDF model and vectorizer trained on LIAR dataset."""
    global _local_model, _local_vectorizer
    if _local_model is None or _local_vectorizer is None:
        base = os.path.dirname(os.path.abspath(__file__))
        m_path = os.path.join(base, "models", "finalized_model.pkl")
        v_path = os.path.join(base, "models", "vectorizer.pkl")
        if os.path.isfile(m_path) and os.path.isfile(v_path):
            try:
                _local_model = joblib.load(m_path)
                _local_vectorizer = joblib.load(v_path)
                print("predict_bert: Loaded ML model & vectorizer successfully.")
            except Exception as e:
                print(f"predict_bert: ML load error: {e}")
    return _local_model, _local_vectorizer


def predict_news(text: str):
    """
    Predict fake vs real news using multi-tier intelligence:
    1. Fast ML Model (TF-IDF + Classifier trained on LIAR dataset - ultra fast, <10MB RAM)
    2. Multi-factor Credibility Engine (Linguistic + Clickbait + Conspiracy analysis)
    Returns: (verdict, confidence) e.g. ("REAL", 88.5) or ("FAKE", 92.1)
    """
    text = (text or "").strip()
    if not text:
        return "FAKE", 50.0

    # Tier 1: Fast ML Classifier
    model, vectorizer = _load_ml_model()
    if model is not None and vectorizer is not None:
        try:
            vec_text = vectorizer.transform([text])
            probs = model.predict_proba(vec_text)[0]
            pred_class = int(model.predict(vec_text)[0])
            confidence = float(probs[pred_class]) * 100
            verdict = "REAL" if pred_class == 1 else "FAKE"
            return verdict, round(confidence, 2)
        except Exception as e:
            print(f"predict_bert: ML predict error: {e}")

    # Tier 2: Credibility Engine Fallback
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
