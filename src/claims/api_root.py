from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework.reverse import reverse


@api_view(["GET"])
def api_root(request, format=None):
    return Response({
        "claims": reverse("claim-list", request=request, format=format),
        "reports": reverse("report-list", request=request, format=format),
        "score": reverse("score-claim", request=request, format=format),
    })
