"""
FacTora Credibility Engine
Multi-factor scoring: BERT confidence + Linguistic signals + Source reliability → 0–100 score
"""

import re
from typing import Optional

# ─────────────────────────────────────────────────────────────────────────────
# TRUSTED / UNRELIABLE DOMAIN LISTS
# ─────────────────────────────────────────────────────────────────────────────
TRUSTED_DOMAINS = {
    "bbc.com", "bbc.co.uk", "reuters.com", "apnews.com", "nytimes.com",
    "theguardian.com", "washingtonpost.com", "npr.org", "pbs.org",
    "aljazeera.com", "bloomberg.com", "economist.com", "ft.com",
    "politico.com", "theatlantic.com", "time.com", "nature.com",
    "sciencemag.org", "newscientist.com", "scientificamerican.com",
    "who.int", "cdc.gov", "nih.gov", "nasa.gov", "snopes.com",
    "factcheck.org", "politifact.com", "thehindu.com", "hindustantimes.com",
    "ndtv.com", "theprint.in", "scroll.in", "thewire.in", "livemint.com",
    "cnbc.com", "cnn.com", "abc.net.au", "cbsnews.com", "nbcnews.com",
    "usatoday.com", "latimes.com", "chicagotribune.com", "sfchronicle.com",
    "vox.com", "fivethirtyeight.com", "propublica.org",
}

UNRELIABLE_DOMAINS = {
    "infowars.com", "naturalnews.com", "beforeitsnews.com",
    "worldnewsdailyreport.com", "theonion.com", "clickhole.com",
    "empirenews.net", "newslo.com", "abcnews.com.co", "usatoday.com.co",
    "nationalreport.net", "huzlers.com", "civic.io", "politicot.com",
    "breitbart.com", "dailybuzz.ch", "now8news.com", "newsexaminer.net",
    "thefreepatriot.org", "cnn.com.de", "bbc.com.de",
    "redflagnews.com", "eutimes.net", "newswatch33.com",
}

SATIRE_DOMAINS = {
    "theonion.com", "clickhole.com", "thebabylonbee.com",
    "reductress.com", "satirewire.com", "theshovel.com.au",
    "newyorker.com/humor",  # partial, handled separately
}

# ─────────────────────────────────────────────────────────────────────────────
# LINGUISTIC SIGNAL PATTERNS
# ─────────────────────────────────────────────────────────────────────────────
CLICKBAIT_PATTERNS = [
    r"\byou won['']t believe\b",
    r"\bshocking\b",
    r"\bbreaking\b",
    r"\bmust.?see\b",
    r"\bwhat (they|he|she|the media) (won['']t|don['']t|doesn['']t) want you to know\b",
    r"\bthis will (shock|surprise|amaze)\b",
    r"\bsecret(s)?\b",
    r"\bmiracl(e|ulous)\b",
    r"\bexplosive\b",
    r"\bgame.?changer\b",
    r"\bthey['']re hiding\b",
    r"\bthe truth about\b",
    r"\bwake up\b",
    r"\bsee what happened\b",
    r"\bwhat really happened\b",
]

CONSPIRACY_PATTERNS = [
    r"\bdeep state\b",
    r"\bnew world order\b",
    r"\bfalse flag\b",
    r"\bhoax\b",
    r"\bglobalist\b",
    r"\billuminati\b",
    r"\bsoros\b",
    r"\bvaccine (kill|death|harm|danger|poison)\b",
    r"\b5g (kill|harm|spread|cause)\b",
    r"\bcovid.?(fake|hoax|lie|plandemic)\b",
    r"\balien(s)?\b",
    r"\bufo(s)?\b",
    r"\bflat earth\b",
    r"\bchemtrail(s)?\b",
    r"\blizard people\b",
]

# ─────────────────────────────────────────────────────────────────────────────
# SCORING UTILITIES
# ─────────────────────────────────────────────────────────────────────────────

def _clamp(value: float, lo: float = 0.0, hi: float = 100.0) -> float:
    return max(lo, min(hi, value))


def score_linguistic(headline: str) -> dict:
    """
    Returns a linguistic credibility score (0–100) and signals found.
    Higher = more credible (fewer red flags).
    """
    signals = []
    penalty = 0.0
    text = headline.strip()

    # ALL-CAPS words (excluding short words ≤3 chars)
    words = text.split()
    caps_words = [w for w in words if w.isupper() and len(w) > 3]
    if len(caps_words) >= 3:
        penalty += 20
        signals.append(f"Excessive ALL-CAPS ({len(caps_words)} words)")
    elif len(caps_words) >= 1:
        penalty += 8
        signals.append(f"ALL-CAPS words detected")

    # Excessive exclamation marks
    exclamations = text.count('!')
    if exclamations >= 3:
        penalty += 20
        signals.append(f"Excessive exclamation marks ({exclamations})")
    elif exclamations >= 1:
        penalty += 8
        signals.append("Exclamation mark usage")

    # Excessive question marks
    question_marks = text.count('?')
    if question_marks >= 2:
        penalty += 10
        signals.append("Multiple question marks")

    # Clickbait patterns
    text_lower = text.lower()
    found_clickbait = []
    for pattern in CLICKBAIT_PATTERNS:
        if re.search(pattern, text_lower):
            found_clickbait.append(pattern.replace(r'\b', '').strip('()'))
    if found_clickbait:
        penalty += min(30, len(found_clickbait) * 10)
        signals.append(f"Clickbait language detected")

    # Conspiracy patterns
    found_conspiracy = []
    for pattern in CONSPIRACY_PATTERNS:
        if re.search(pattern, text_lower):
            found_conspiracy.append(pattern)
    if found_conspiracy:
        penalty += min(40, len(found_conspiracy) * 15)
        signals.append(f"Conspiracy language detected")

    # Length check (very short or very long headlines suspicious)
    word_count = len(words)
    if word_count < 3:
        penalty += 10
        signals.append("Headline too short")
    elif word_count > 25:
        penalty += 5
        signals.append("Unusually long headline")

    score = _clamp(100 - penalty)
    return {
        "score": round(score, 1),
        "signals": signals,
        "clickbait_detected": len(found_clickbait) > 0,
        "conspiracy_detected": len(found_conspiracy) > 0,
    }


def score_source(domain: Optional[str]) -> dict:
    """
    Returns source credibility score (0–100) based on domain reputation.
    """
    if not domain:
        return {"score": 50.0, "trust_level": "unknown", "badge": "❓ Unknown Source"}

    domain = domain.lower().strip()
    # Strip www.
    if domain.startswith("www."):
        domain = domain[4:]

    if domain in TRUSTED_DOMAINS:
        return {
            "score": 90.0,
            "trust_level": "trusted",
            "badge": "✅ Trusted Source",
            "domain": domain,
        }
    elif domain in UNRELIABLE_DOMAINS:
        # Check satire first
        if domain in SATIRE_DOMAINS:
            return {
                "score": 30.0,
                "trust_level": "satire",
                "badge": "🎭 Satire / Parody",
                "domain": domain,
            }
        return {
            "score": 15.0,
            "trust_level": "unreliable",
            "badge": "🚨 Known Unreliable",
            "domain": domain,
        }
    else:
        # Unknown domain → neutral score
        return {
            "score": 55.0,
            "trust_level": "unknown",
            "badge": "❓ Unverified Source",
            "domain": domain,
        }


def get_credibility_grade(score: float) -> dict:
    """Maps numeric score to a letter grade and color."""
    if score >= 80:
        return {"grade": "A", "label": "Highly Credible", "color": "#22c55e"}
    elif score >= 65:
        return {"grade": "B", "label": "Likely Credible", "color": "#84cc16"}
    elif score >= 50:
        return {"grade": "C", "label": "Uncertain", "color": "#eab308"}
    elif score >= 35:
        return {"grade": "D", "label": "Questionable", "color": "#f97316"}
    else:
        return {"grade": "F", "label": "Likely Fake / Misleading", "color": "#ef4444"}


# ─────────────────────────────────────────────────────────────────────────────
# MAIN SCORING FUNCTION
# ─────────────────────────────────────────────────────────────────────────────

def compute_credibility(
    headline: str,
    bert_confidence: float,   # 0–100, where high confidence for REAL = positive signal
    bert_prediction: str,     # "REAL" or "FAKE"
    domain: Optional[str] = None,
) -> dict:
    """
    Compute a composite credibility score 0–100 from three factors.

    Weights:
      - BERT Model Score : 50%
      - Linguistic Score : 30%
      - Source Score     : 20%
    """

    # 1. BERT score: if REAL → confidence is credibility, if FAKE → penalize
    if bert_prediction == "REAL":
        bert_score = bert_confidence  # High confidence REAL → high credibility
    else:
        # High confidence FAKE → low credibility
        bert_score = 100.0 - bert_confidence

    bert_score = _clamp(bert_score)

    # 2. Linguistic signals
    linguistic = score_linguistic(headline)
    linguistic_score = linguistic["score"]

    # 3. Source score
    source = score_source(domain)
    source_score = source["score"]

    # 4. Composite (weighted)
    composite = (
        bert_score * 0.50 +
        linguistic_score * 0.30 +
        source_score * 0.20
    )
    composite = _clamp(composite)

    grade_info = get_credibility_grade(composite)

    return {
        "credibility_score": round(composite, 1),
        "grade": grade_info["grade"],
        "label": grade_info["label"],
        "color": grade_info["color"],
        "verdict": bert_prediction,
        "factors": {
            "bert": {
                "score": round(bert_score, 1),
                "weight": "50%",
                "label": f"AI Model ({bert_prediction}, {bert_confidence:.1f}% conf.)",
            },
            "linguistic": {
                "score": round(linguistic_score, 1),
                "weight": "30%",
                "label": "Linguistic Analysis",
                "signals": linguistic["signals"],
                "clickbait": linguistic["clickbait_detected"],
                "conspiracy": linguistic["conspiracy_detected"],
            },
            "source": {
                "score": round(source_score, 1),
                "weight": "20%",
                "label": "Source Reliability",
                "trust_level": source["trust_level"],
                "badge": source["badge"],
                "domain": source.get("domain"),
            },
        },
    }
