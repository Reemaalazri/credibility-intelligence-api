from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework.reverse import reverse
from drf_spectacular.utils import extend_schema
from .serializers import ApiRootSerializer


# Defines the API root endpoint used to list the main available routes
@extend_schema(
    responses=ApiRootSerializer,
    description="API root endpoint listing the main available API routes."
)
# Allows this view to handle GET requests
@api_view(["GET"])
# Returns links to the main API resources
def api_root(request, format=None):
    return Response({
        # access LIAR dataset claims
        "claims": reverse("claim-list", request=request, format=format),
        # access user reports
        "reports": reverse("report-list", request=request, format=format),
        # claim credibility scoring endpoint
        "score": reverse("score-claim", request=request, format=format),
    })
