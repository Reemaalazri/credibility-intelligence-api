import os
from rest_framework.decorators import api_view, permission_classes, throttle_classes
from rest_framework.response import Response
from rest_framework import status
from .scoring import score_text
from .factcheck import search_google_factcheck
from rest_framework.permissions import IsAuthenticated
from .throttles import ScoreRateThrottle
from drf_spectacular.utils import extend_schema, OpenApiExample
from .serializers import (
    ScoreRequestSerializer,
    ScoreResponseSerializer,
    ErrorResponseSerializer,
)


# Convert a 0-1 score into a 0-100 percentage.
def _to_100(x):
    return max(0, min(100, int(round(float(x) * 100))))


# Map external credibility and confidence into a simple verdict label.
def _external_verdict(cred_score_100: int, conf_score_100: int) -> str:
    if conf_score_100 < 35:
        return "uncertain"
    if cred_score_100 >= 65:
        return "likely_true"
    if cred_score_100 <= 35:
        return "likely_false"
    return "disputed"


# Document the endpoint request, responses and example payloads.
@extend_schema(
    request=ScoreRequestSerializer,
    responses={
        200: ScoreResponseSerializer,
        400: ErrorResponseSerializer,
        401: ErrorResponseSerializer,
    },
    description="Analyse the credibility of a claim and return a credibility/risk summary.",
    examples=[
        OpenApiExample(
            "Score request example",
            value={"text": "vaccines cause autism"},
            request_only=True,
        ),
        OpenApiExample(
            "Score response example",
            value={
                "claim": "vaccines cause autism",
                "summary": {
                    "final_verdict": "likely_false",
                    "final_credibility_score": 18,
                    "final_risk_score": 82,
                    "final_confidence": 74,
                },
                "local_analysis": {},
                "external_analysis": {},
                "fusion": {},
            },
            response_only=True,
        ),
    ],
)
@api_view(["POST"])
@permission_classes([IsAuthenticated])
@throttle_classes([ScoreRateThrottle])
def score_claim(request):
    # Read and clean the input claim text from the request body.
    text = (request.data.get("text") or "").strip()
    if not text:
        return Response({"error": "text is required"}, status=status.HTTP_400_BAD_REQUEST)

    try:
        # Run the local scoring pipeline on the submitted claim.
        local_raw = score_text(text, request=request, top_k=5)

        # Try to prepare external fact-check lookup if the API key exists.
        api_key = os.getenv("GOOGLE_FACTCHECK_API_KEY")
        external_raw = None

        # Query Google Fact Check when the external API is configured.
        if api_key:
            try:
                external_raw = search_google_factcheck(
                    query=text,
                    api_key=api_key,
                    page_size=5,
                )
            except Exception as external_error:
                external_raw = {
                    "external_error": str(external_error),
                    "external_credibility_score": 0.5,
                    "external_risk_score": 50,
                    "external_confidence": 0.0,
                    "fact_checks": [],
                }
        else:
            external_raw = {
                "external_note": "GOOGLE_FACTCHECK_API_KEY not configured; returning local score only.",
                "external_credibility_score": 0.5,
                "external_risk_score": 50,
                "external_confidence": 0.0,
                "fact_checks": [],
            }

        # Normalize local and external scores into 0-100 values.
        local_cred_100 = _to_100(local_raw["credibility_score"])
        local_conf_100 = _to_100(local_raw["confidence"])

        ext_cred_100 = _to_100(external_raw.get("external_credibility_score", 0.5))
        ext_conf_100 = _to_100(external_raw.get("external_confidence", 0.0))

        # Count how much evidence each source contributed.
        local_evidence_count = (
            len(local_raw.get("supporting_evidence", [])) +
            len(local_raw.get("refuting_evidence", []))
        )
        external_evidence_count = len(external_raw.get("fact_checks", []))

        # Dynamic evidence strength:
        # higher confidence + more evidence => more weight
        # Compute source strength from confidence and evidence volume.
        local_strength = (local_conf_100 / 100.0) * (0.70 + 0.10 * min(local_evidence_count, 3))
        external_strength = (ext_conf_100 / 100.0) * (0.70 + 0.10 * min(external_evidence_count, 3))

        # Assign dynamic fusion weights based on source strength.
        if external_strength > 0:
            total_strength = local_strength + external_strength
            local_weight = int(round((local_strength / total_strength) * 100))
            external_weight = 100 - local_weight
        else:
            local_weight = 100
            external_weight = 0

        # Combine local and external scores into final fused outputs.
        final_cred_100 = int(round(
            (local_cred_100 * local_weight + ext_cred_100 * external_weight) / 100.0
        ))

        final_conf_100 = int(round(
            (local_conf_100 * local_weight + ext_conf_100 * external_weight) / 100.0
        ))

        final_risk_100 = 100 - final_cred_100

        # Convert the final fused scores into a user-facing verdict.
        if final_conf_100 < 40:
            final_verdict = "uncertain"
        elif final_cred_100 >= 65:
            final_verdict = "likely_true"
        elif final_cred_100 <= 35:
            final_verdict = "likely_false"
        else:
            final_verdict = "disputed"

        # Build the final API response with summary, source details, and fusion info.
        response = {
            "claim": text,
            "summary": {
                "final_verdict": final_verdict,
                "final_credibility_score": final_cred_100,
                "final_risk_score": final_risk_100,
                "final_confidence": final_conf_100,
            },
            "local_analysis": {
                "verdict": local_raw["verdict"],
                "credibility_score": local_cred_100,
                "risk_score": local_raw["risk_score"],
                "confidence": local_conf_100,
                "supporting_evidence_count": len(local_raw.get("supporting_evidence", [])),
                "refuting_evidence_count": len(local_raw.get("refuting_evidence", [])),
                "top_supporting_evidence": local_raw.get("supporting_evidence", [])[:2],
                "top_refuting_evidence": local_raw.get("refuting_evidence", [])[:2],
                "signals": local_raw.get("signals", []),
            },
            "external_analysis": {
                "source": "Google Fact Check Tools API",
                "verdict": _external_verdict(ext_cred_100, ext_conf_100) if external_evidence_count > 0 else "not_available",
                "credibility_score": ext_cred_100,
                "risk_score": external_raw.get("external_risk_score", 50),
                "confidence": ext_conf_100,
                "matched_fact_checks_count": external_evidence_count,
                "top_fact_checks": external_raw.get("fact_checks", [])[:2],
            },
            "fusion": {
                "local_weight": local_weight,
                "external_weight": external_weight,
                "method": "Dynamic confidence-weighted fusion of local LIAR retrieval and external fact-check evidence",
            },
        }

        # Add any external API notes or errors when present.
        if "external_note" in external_raw:
            response["external_analysis"]["note"] = external_raw["external_note"]

        if "external_error" in external_raw:
            response["external_analysis"]["error"] = external_raw["external_error"]

        return Response(response, status=status.HTTP_200_OK)

    # Return a bad request response if scoring fails.
    except Exception as e:
        return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)
