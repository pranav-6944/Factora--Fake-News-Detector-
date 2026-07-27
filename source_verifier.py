"""
FacTora Source Verifier
Cross-references article URLs/domains against trusted lists, Wikipedia, and heuristics.
"""

import re
import requests
from urllib.parse import urlparse
from credibility_engine import TRUSTED_DOMAINS, UNRELIABLE_DOMAINS, SATIRE_DOMAINS

WIKIPEDIA_API = "https://en.wikipedia.org/api/rest_v1/page/summary/"

# ─────────────────────────────────────────────────────────────────────────────
# PUBLICATION MAP: domain → Wikipedia article title
# ─────────────────────────────────────────────────────────────────────────────
WIKI_MAP = {
    "bbc.com": "BBC",
    "bbc.co.uk": "BBC",
    "reuters.com": "Reuters",
    "apnews.com": "Associated_Press",
    "nytimes.com": "The_New_York_Times",
    "theguardian.com": "The_Guardian",
    "washingtonpost.com": "The_Washington_Post",
    "npr.org": "NPR",
    "aljazeera.com": "Al_Jazeera_English",
    "bloomberg.com": "Bloomberg_News",
    "thehindu.com": "The_Hindu",
    "ndtv.com": "NDTV",
    "politifact.com": "PolitiFact",
    "snopes.com": "Snopes",
    "factcheck.org": "FactCheck.org",
    "infowars.com": "Infowars",
    "naturalnews.com": "Natural_News",
    "breitbart.com": "Breitbart_News",
    "theonion.com": "The_Onion",
    "thebabylonbee.com": "The_Babylon_Bee",
}


def extract_domain(url_or_domain: str) -> str:
    """Extract the bare domain from a URL or domain string."""
    text = url_or_domain.strip()
    if text.startswith(("http://", "https://")):
        parsed = urlparse(text)
        domain = parsed.netloc
    else:
        domain = text

    # Strip www.
    if domain.startswith("www."):
        domain = domain[4:]

    return domain.lower()


def _fetch_wikipedia(title: str) -> dict:
    """Fetch a brief Wikipedia summary for the given article title."""
    try:
        url = WIKIPEDIA_API + title.replace(" ", "_")
        resp = requests.get(url, timeout=5, headers={"User-Agent": "FacTora/1.0"})
        if resp.status_code == 200:
            data = resp.json()
            return {
                "found": True,
                "extract": data.get("extract", "")[:400] + "...",
                "url": data.get("content_urls", {}).get("desktop", {}).get("page", ""),
                "thumbnail": data.get("thumbnail", {}).get("source"),
            }
    except Exception:
        pass
    return {"found": False, "extract": None, "url": None, "thumbnail": None}


def verify_source(url_or_domain: str) -> dict:
    """
    Full source verification report for a given URL or domain.
    Returns trust level, reliability badge, Wikipedia info, and recommendations.
    """
    domain = extract_domain(url_or_domain)

    # Determine trust level from lists
    if domain in TRUSTED_DOMAINS:
        trust_level = "trusted"
        trust_score = 90
        badge = "✅ Trusted Source"
        badge_class = "badge-trusted"
        recommendations = [
            "This source is well-established and fact-checked.",
            "Content is generally reliable but always read critically.",
        ]
    elif domain in SATIRE_DOMAINS:
        trust_level = "satire"
        trust_score = 30
        badge = "🎭 Satire / Parody"
        badge_class = "badge-satire"
        recommendations = [
            "This is a satire or parody website.",
            "Content is intentionally fictional and should not be shared as news.",
        ]
    elif domain in UNRELIABLE_DOMAINS:
        trust_level = "unreliable"
        trust_score = 15
        badge = "🚨 Known Unreliable"
        badge_class = "badge-unreliable"
        recommendations = [
            "This source has a history of publishing misinformation.",
            "Cross-check any claims with trusted news outlets before sharing.",
            "Fact-check at Snopes.com or FactCheck.org.",
        ]
    else:
        trust_level = "unknown"
        trust_score = 55
        badge = "❓ Unverified Source"
        badge_class = "badge-unknown"
        recommendations = [
            "This source is not in our database. Verify it independently.",
            "Check if the domain was recently created or mimics a trusted outlet.",
            "Look for author credentials, citations, and editorial policies.",
        ]

    # Heuristic checks on domain name
    heuristics = []
    # Mimic indicators: domain contains well-known brand + extra suffix
    for trusted in ["bbc", "cnn", "nytimes", "reuters", "apnews", "abc", "nbc"]:
        if trusted in domain and domain not in TRUSTED_DOMAINS:
            heuristics.append(f"⚠️ Domain may be mimicking '{trusted}' – exercise caution")
            trust_score = min(trust_score, 20)
            if trust_level == "unknown":
                trust_level = "suspicious"
                badge = "⚠️ Possibly Deceptive"
                badge_class = "badge-suspicious"

    # TLD suspicion flags
    suspicious_tlds = [".info", ".click", ".xyz", ".top", ".club", ".link"]
    for tld in suspicious_tlds:
        if domain.endswith(tld):
            heuristics.append(f"ℹ️ Non-standard TLD '{tld}' – sometimes used by spam sites")
            trust_score = max(25, trust_score - 10)

    # Wikipedia lookup
    wiki_title = WIKI_MAP.get(domain)
    if wiki_title:
        wiki = _fetch_wikipedia(wiki_title)
    else:
        # Try the domain name itself capitalized
        wiki = _fetch_wikipedia(domain.split(".")[0].capitalize())

    return {
        "domain": domain,
        "original_input": url_or_domain,
        "trust_level": trust_level,
        "trust_score": trust_score,
        "badge": badge,
        "badge_class": badge_class,
        "heuristics": heuristics,
        "recommendations": recommendations,
        "wikipedia": wiki,
    }
