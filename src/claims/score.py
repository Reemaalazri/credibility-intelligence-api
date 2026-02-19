from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status

# simple + explainable baseline (perfect for coursework)
RISK_KEYWORDS_HIGH = ["hoax", "conspiracy", "secretly", "fake", "fraud", "rigged", "stolen"]
RISK_KEYWORDS_MED = ["reportedly", "sources say", "unconfirmed", "allegedly", "claims"]


@api_view(["POST"])
def score_claim(request):
    text = (request.data.get("text") or "").strip()
    if not text:
        return Response({"error": "text is required"}, status=status.HTTP_400_BAD_REQUEST)

    lower = text.lower()
    signals = []
    score = 0.15  # baseline uncertainty

    for kw in RISK_KEYWORDS_MED:
        if kw in lower:
            signals.append(kw)
            score += 0.2

    for kw in RISK_KEYWORDS_HIGH:
        if kw in lower:
            signals.append(kw)
            score += 0.35

    if len(text) > 200:
        signals.append("length>200")
        score += 0.1

    score = max(0.0, min(1.0, score))

    if score >= 0.75:
        risk_level = "high"
    elif score >= 0.45:
        risk_level = "medium"
    else:
        risk_level = "low"

    return Response({
        "input": text,
        "risk_score": round(score, 2),
        "risk_level": risk_level,
        "signals": signals,
        "note": "Baseline heuristic scorer (replace with ML model later).",
    })
