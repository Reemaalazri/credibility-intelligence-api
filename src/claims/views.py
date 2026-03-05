# from django.shortcuts import render

# Create your views here.
from rest_framework import viewsets, filters
from .models import Claim, UserReport
from .serializers import ClaimSerializer, UserReportSerializer
from django_filters.rest_framework import DjangoFilterBackend
from .filters import ClaimFilter
from rest_framework.decorators import action
from rest_framework.response import Response


class ClaimViewSet(viewsets.ReadOnlyModelViewSet):
    """
    Read-only endpoints for dataset claims.
    """
    queryset = Claim.objects.all()
    # queryset = Claim.objects.all().order_by("id")
    serializer_class = ClaimSerializer

    filter_backends = [
        DjangoFilterBackend,
        filters.SearchFilter,
        filters.OrderingFilter,
    ]
    filterset_class = ClaimFilter
    search_fields = ["statement", "speaker", "subjects", "context"]
    ordering_fields = ["id", "created_at", "speaker", "label"]
    ordering = ["-created_at"]

    @action(detail=False, methods=["get"], url_path="by-speaker/(?P<speaker>[^/.]+)")
    def by_speaker(self, request, speaker=None):
        """
        Retrieve claims by speaker name.
        Example: /api/claims/by-speaker/obama
        """
        claims = Claim.objects.filter(speaker__icontains=speaker)
        serializer = self.get_serializer(claims, many=True)
        return Response(serializer.data)


class UserReportViewSet(viewsets.ModelViewSet):
    """
    Full CRUD endpoints for user reports (coursework requirement).
    """
    queryset = UserReport.objects.all().order_by("-created_at")
    serializer_class = UserReportSerializer
    search_fields = ["statement_text", "speaker", "report_reason"]
    filterset_fields = ["status", "risk_level"]
    ordering_fields = ["created_at", "risk_score"]
