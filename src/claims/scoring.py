import re
from dataclasses import dataclass
from functools import lru_cache
from typing import Dict, List, Tuple

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

from .models import Claim


LABEL_TO_SIGNAL = {
    "true": 1.00,
    "mostly-true": 0.70,
    "half-true": 0.20,
    "barely-true": -0.40,
    "false": -0.80,
    "pants-fire": -1.00,
    "pants on fire": -1.00,
    "pants-on-fire": -1.00,
}

NEG_WORDS = {
    "not", "no", "never", "none", "cannot", "can't",
    "dont", "don't", "doesnt", "doesn't", "isnt", "isn't",
    "wasnt", "wasn't", "arent", "aren't", "wont", "won't",
    "without", "neither", "nor"
}

STOPLIKE = {
    "the", "a", "an", "is", "are", "was", "were", "be", "been", "being",
    "of", "in", "on", "at", "to", "for", "from", "by", "with", "about",
    "that", "this", "these", "those", "it", "its", "as", "and", "or",
    "if", "then", "than", "but"
}

INVERSION_PHRASES = [
    "false that",
    "wrong that",
    "myth that",
    "claim that",
    "claims that",
    "say that",
    "says that",
    "people who say",
    "deceived by",
    "not true that",
]

RISK_KEYWORDS_HIGH = [
    "hoax", "conspiracy", "secretly", "fake", "fraud",
    "rigged", "stolen", "coverup", "scam"
]

RISK_KEYWORDS_MED = [
    "reportedly", "sources say", "unconfirmed", "allegedly",
    "claims", "they don't want you to know"
]


@dataclass(frozen=True)
class Match:
    claim_id: int
    url: str
    label: str
    speaker: str
    statement: str
    similarity: float
    stance: str
    stance_score: float
    oriented_signal: float
    topic_score: float


def _tokens(text: str) -> List[str]:
    return re.findall(r"[a-z']+", (text or "").lower())


def _content_tokens(text: str) -> List[str]:
    return [t for t in _tokens(text) if t not in STOPLIKE]


def _has_negation(text: str) -> bool:
    return any(t in NEG_WORDS for t in _tokens(text))


def _topic_match(a: str, b: str) -> float:
    ta = set(_content_tokens(a))
    tb = set(_content_tokens(b))
    if not ta or not tb:
        return 0.0
    return len(ta & tb) / max(1, min(len(ta), len(tb)))


def _shared_token_count(a: str, b: str) -> int:
    return len(set(_content_tokens(a)) & set(_content_tokens(b)))


def _has_inversion_phrase(text: str) -> bool:
    lower = (text or "").lower()
    return any(p in lower for p in INVERSION_PHRASES)


def _label_signal(label: str) -> float:
    if not label:
        return 0.0
    return LABEL_TO_SIGNAL.get(label.strip().lower(), 0.0)


def _oriented_signal(label: str, stance: str) -> float:
    signal = _label_signal(label)

    if stance == "supports":
        return signal
    if stance == "refutes":
        return -signal
    return 0.0


def _classify_stance(query: str, evidence: str, sim: float) -> Tuple[str, float]:
    overlap = _topic_match(query, evidence)
    neg_q = _has_negation(query)
    neg_e = _has_negation(evidence)

    if overlap < 0.18 and sim < 0.30:
        return "unrelated", 0.20

    if overlap >= 0.35 and neg_q != neg_e:
        score = 0.62 + (0.22 * min(sim, 1.0))

        if _has_inversion_phrase(evidence):
            return "supports", round(min(score, 0.90), 3)

        return "refutes", round(min(score, 0.95), 3)

    if sim >= 0.42 or overlap >= 0.38:
        score = 0.52 + (0.22 * min(sim, 1.0))
        return "supports", round(min(score, 0.90), 3)

    if sim >= 0.32 and overlap >= 0.22:
        score = 0.45 + (0.18 * min(sim, 1.0))
        return "supports", round(min(score, 0.80), 3)

    return "unrelated", 0.20


@lru_cache(maxsize=1)
def _build_index():
    rows = []
    corpus = []

    for c in Claim.objects.only("id", "label", "speaker", "statement").all():
        text = (c.statement or "").strip()
        if not text:
            continue

        rows.append({
            "id": c.id,
            "label": c.label or "",
            "speaker": c.speaker or "",
            "statement": text,
        })
        corpus.append(text)

    if not corpus:
        raise ValueError("No claims available in local dataset.")

    vectorizer = TfidfVectorizer(
        lowercase=True,
        stop_words="english",
        ngram_range=(1, 2),
        min_df=2,
        max_features=50000,
    )
    matrix = vectorizer.fit_transform(corpus)
    return vectorizer, matrix, rows


def score_text(text: str, request=None, top_k: int = 6) -> Dict:
    text = (text or "").strip()
    if not text:
        raise ValueError("text is required")

    vectorizer, matrix, rows = _build_index()
    q = vectorizer.transform([text])
    sims = cosine_similarity(q, matrix)[0]

    candidate_idx = sims.argsort()[::-1][:25]
    SIM_THRESHOLD = 0.28

    matches: List[Match] = []
    signal_sum = 0.0
    abs_signal_sum = 0.0
    weight_total = 0.0

    similarities: List[float] = []
    stance_scores: List[float] = []
    strong_match_count = 0
    signals: List[str] = []

    query_tokens = set(_content_tokens(text))

    for idx in candidate_idx:
        sim = float(sims[idx])
        if sim < SIM_THRESHOLD:
            continue

        row = rows[int(idx)]
        evidence_text = row["statement"]
        evidence_tokens = set(_content_tokens(evidence_text))

        topic_score = _topic_match(text, evidence_text)
        shared_tokens = len(query_tokens & evidence_tokens)

        # hard filters to remove weak / irrelevant matches
        if topic_score < 0.40:
            continue

        if shared_tokens < 2:
            continue

        stance, stance_score = _classify_stance(text, evidence_text, sim) 

        # only keep strong support/refute evidence
        if stance == "unrelated":
            continue

        if stance_score < 0.65:
            continue

        label_signal = _label_signal(row["label"])
        oriented_signal = _oriented_signal(row["label"], stance)

        # neutral evidence should not be included
        if abs(oriented_signal) < 0.15:
            continue

        if request is not None:
            url = request.build_absolute_uri(f"/api/claims/{row['id']}/")
        else:
            url = f"/api/claims/{row['id']}/"

        weight = sim * stance_score * max(0.25, abs(label_signal)) * topic_score

        signal_sum += oriented_signal * weight
        abs_signal_sum += abs(oriented_signal * weight)
        weight_total += weight

        similarities.append(sim)
        stance_scores.append(stance_score)

        if sim >= 0.40 and stance_score >= 0.70 and topic_score >= 0.40:
            strong_match_count += 1

        matches.append(
            Match(
                claim_id=row["id"],
                url=url,
                label=row["label"],
                speaker=row["speaker"],
                statement=evidence_text,
                similarity=round(sim, 4),
                stance=stance,
                stance_score=round(stance_score, 3),
                oriented_signal=round(oriented_signal, 3),
                topic_score=round(topic_score, 3),
            )
        )

    matches = sorted(
        matches,
        key=lambda m: (m.topic_score, m.similarity, m.stance_score, abs(m.oriented_signal)),
        reverse=True
    )[:top_k]

    if weight_total == 0:
        credibility_score = 0.5
        confidence = 0.0
        verdict = "uncertain"
    else:
        raw_signal = signal_sum / weight_total
        raw_signal = max(-1.0, min(1.0, raw_signal))
        credibility_score = (raw_signal + 1.0) / 2.0

        coverage = min(1.0, strong_match_count / 3.0)
        avg_similarity = sum(similarities) / len(similarities) if similarities else 0.0
        avg_stance = sum(stance_scores) / len(stance_scores) if stance_scores else 0.0
        agreement = abs(signal_sum) / abs_signal_sum if abs_signal_sum > 0 else 0.0

        confidence = (
            0.30 * coverage +
            0.30 * avg_similarity +
            0.20 * avg_stance +
            0.20 * agreement
        )
        confidence = max(0.0, min(1.0, confidence))

        if confidence < 0.35:
            verdict = "uncertain"
        elif credibility_score >= 0.65:
            verdict = "likely_true"
        elif credibility_score <= 0.35:
            verdict = "likely_false"
        else:
            verdict = "disputed"

    lower = text.lower()
    risk_bonus = 0

    for kw in RISK_KEYWORDS_MED:
        if kw in lower:
            signals.append(kw)
            risk_bonus += 4

    for kw in RISK_KEYWORDS_HIGH:
        if kw in lower:
            signals.append(kw)
            risk_bonus += 7

    credibility_score = max(0.0, min(1.0, credibility_score))
    risk_score = int(round((1.0 - credibility_score) * 100))
    risk_score = min(100, max(0, risk_score + risk_bonus))

    if risk_score >= 70:
        risk_level = "high"
    elif risk_score >= 35:
        risk_level = "medium"
    else:
        risk_level = "low"

    supporting = []
    refuting = []

    for m in matches:
        item = {
            "id": m.claim_id,
            "url": m.url,
            "label": m.label,
            "speaker": m.speaker,
            "statement": m.statement,
            "similarity": m.similarity,
            "topic_score": m.topic_score,
            "stance_score": m.stance_score,
            "oriented_signal": m.oriented_signal,
        }

        if m.stance == "supports":
            supporting.append(item)
        elif m.stance == "refutes":
            refuting.append(item)

    return {
        "input": text,
        "credibility_score": round(credibility_score, 3),
        "risk_score": risk_score,
        "risk_level": risk_level,
        "confidence": round(confidence, 3),
        "verdict": verdict,
        "supporting_evidence": supporting[:3],
        "refuting_evidence": refuting[:3],
        "signals": signals,
        "method": "Strict support/refute evidence retrieval over LIAR with neutral evidence removed",
        "note": "Only evidence with sufficient topic overlap, shared tokens, and stance strength is included.",
    }


def rebuild_index():
    _build_index.cache_clear()
    _build_index()