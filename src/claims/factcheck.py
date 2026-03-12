import json
import re
import urllib.parse
import urllib.request
from typing import Dict, List, Optional
# Still

RATING_TO_SIGNAL = {
    "true": 1.00,
    "mostly true": 0.70,
    "partly true": 0.30,
    "half true": 0.20,
    "mixture": 0.00,
    "mixed": 0.00,
    "needs context": -0.20,
    "out of context": -0.40,
    "misleading": -0.60,
    "distorts the facts": -0.70,
    "incorrect": -0.80,
    "mostly false": -0.70,
    "false": -0.90,
    "pants on fire": -1.00,
    "unsupported": -0.70,
    "no evidence": -0.80,
    "exaggerates": -0.50,
    "satire": 0.00,
    "flawed paper": -0.70,
    "flawed": -0.60,
}

NEG_WORDS = {
    "not", "no", "never", "none", "cannot", "can't",
    "dont", "don't", "doesnt", "doesn't", "isnt", "isn't"
}

STOPLIKE = {
    "the", "a", "an", "is", "are", "was", "were", "be", "been", "being",
    "of", "in", "on", "at", "to", "for", "from", "by", "with", "about",
    "that", "this", "these", "those", "it", "its", "as", "and", "or",
    "if", "then", "than", "but"
}


def _tokens(text: str) -> List[str]:
    return re.findall(r"[a-z']+", (text or "").lower())


def _content_tokens(text: str) -> set[str]:
    return {t for t in _tokens(text) if t not in STOPLIKE}


def _has_negation(text: str) -> bool:
    return any(t in NEG_WORDS for t in _tokens(text))


def _rating_to_signal(textual_rating: Optional[str]) -> float:
    if not textual_rating:
        return 0.0

    r = textual_rating.strip().lower()

    ordered = sorted(RATING_TO_SIGNAL.items(), key=lambda x: len(x[0]), reverse=True)
    for key, score in ordered:
        if key in r:
            return score

    negative_patterns = [
        "abundant evidence",
        "incorrect",
        "no evidence",
        "misinterprets",
        "misleading",
        "not true",
        "false claim",
        "wrong",
        "debunked",
        "spherical",
        "roughly spherical",
    ]
    positive_patterns = [
        "supported by evidence",
        "confirmed",
        "accurate",
        "correct",
    ]

    if any(p in r for p in negative_patterns):
        return -0.8

    if any(p in r for p in positive_patterns):
        return 0.8

    return 0.0


def _relevance_score(query: str, claim_text: str) -> float:
    q = _content_tokens(query)
    c = _content_tokens(claim_text)

    if not q or not c:
        return 0.0

    inter = len(q & c)
    base = inter / max(1, len(q))

    if base >= 0.25 and (_has_negation(query) != _has_negation(claim_text)):
        base *= 0.85

    return min(1.0, base)


def _classify_external_stance(query: str, claim_text: str) -> tuple[str, float]:
    q_tokens = _content_tokens(query)
    c_tokens = _content_tokens(claim_text)

    if not q_tokens or not c_tokens:
        return "unrelated", 0.2

    overlap = len(q_tokens & c_tokens) / max(1, len(q_tokens | c_tokens))

    if overlap < 0.18:
        return "unrelated", 0.2

    if _has_negation(query) != _has_negation(claim_text):
        return "refutes", min(0.95, 0.60 + overlap)

    return "supports", min(0.95, 0.55 + overlap)


def search_google_factcheck(query: str, api_key: str, page_size: int = 5) -> Dict:
    params = {
        "query": query,
        "pageSize": page_size,
        "key": api_key,
    }

    url = "https://factchecktools.googleapis.com/v1alpha1/claims:search?" + urllib.parse.urlencode(params)

    with urllib.request.urlopen(url, timeout=20) as resp:
        data = json.loads(resp.read().decode("utf-8"))

    raw_claims = data.get("claims", [])
    normalized: List[Dict] = []

    signal_sum = 0.0
    abs_signal_sum = 0.0
    weight_total = 0.0

    for claim in raw_claims:
        claim_text = claim.get("text", "") or ""
        relevance = _relevance_score(query, claim_text)
        stance, stance_score = _classify_external_stance(query, claim_text)

        # drop weak / unrelated fact-check claims
        if relevance < 0.30:
            continue

        if stance == "unrelated":
            continue

        if stance_score < 0.60:
            continue

        claim_reviews = claim.get("claimReview", []) or []

        for review in claim_reviews:
            publisher = review.get("publisher", {}) or {}

            publisher_name = publisher.get("name")
            review_url = review.get("url")
            textual_rating = review.get("textualRating")
            review_date = review.get("reviewDate")

            signal = _rating_to_signal(textual_rating)

            # remove neutral reviews
            if abs(signal) < 0.15:
                continue

            if stance == "refutes":
                signal = -signal

            weight = relevance * stance_score

            signal_sum += signal * weight
            abs_signal_sum += abs(signal * weight)
            weight_total += weight

            normalized.append(
                {
                    "claim_text": claim_text,
                    "publisher_name": publisher_name,
                    "url": review_url,
                    "textual_rating": textual_rating,
                    "review_date": review_date,
                    "signal": round(signal, 3),
                    "relevance": round(relevance, 3),
                    "stance_score": round(stance_score, 3),
                }
            )

    normalized.sort(
        key=lambda x: (x["relevance"], x["stance_score"], abs(x["signal"])),
        reverse=True
    )

    top_fact_checks = normalized[:3]

    if weight_total > 0:
        external_signal = signal_sum / weight_total
        external_signal = max(-1.0, min(1.0, external_signal))
        external_cred = (external_signal + 1.0) / 2.0

        avg_relevance = (
            sum(item["relevance"] for item in top_fact_checks) / len(top_fact_checks)
            if top_fact_checks else 0.0
        )
        count_factor = min(1.0, len(top_fact_checks) / 3.0)
        agreement = abs(signal_sum) / abs_signal_sum if abs_signal_sum > 0 else 0.0

        confidence = min(1.0, 0.35 * avg_relevance + 0.35 * count_factor + 0.30 * agreement)
    else:
        external_cred = 0.5
        confidence = 0.0

    return {
        "external_credibility_score": round(external_cred, 3),
        "external_risk_score": int(round((1.0 - external_cred) * 100)),
        "external_confidence": round(confidence, 3),
        "fact_checks": top_fact_checks,
    }
