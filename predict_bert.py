from transformers import DistilBertTokenizerFast, DistilBertForSequenceClassification
import torch
import os

# Lazy-loaded model/tokenizer (avoids crash when files don't exist yet)
_model = None
_tokenizer = None


def _load_model():
    """Load BERT model and tokenizer on first use."""
    global _model, _tokenizer
    if _model is None:
        base = os.path.dirname(os.path.abspath(__file__))
        model_path = os.path.join(base, "bert_model")
        tokenizer_path = os.path.join(base, "bert_tokenizer")
        _model = DistilBertForSequenceClassification.from_pretrained(model_path)
        _tokenizer = DistilBertTokenizerFast.from_pretrained(tokenizer_path)
        _model.eval()
        print("✅ predict_bert: Model and tokenizer loaded.")
    return _model, _tokenizer


# FUNCTION to predict news
def predict_news(text):
    model, tokenizer = _load_model()
    inputs = tokenizer(text, return_tensors="pt", padding=True, truncation=True, max_length=512)
    with torch.no_grad():
        outputs = model(**inputs)
    probs = torch.nn.functional.softmax(outputs.logits, dim=1)
    confidence = float(probs.max()) * 100
    prediction = torch.argmax(probs, dim=1).item()
    label = "REAL ✅" if prediction == 1 else "FAKE ❌"
    return label, round(confidence, 2)


# 🧪 Test
if __name__ == "__main__":
    text = input("📰 Enter a news headline: ")
    label, confidence = predict_news(text)
    print(f"\nPrediction: {label}")
    print(f"Confidence: {confidence}%")
