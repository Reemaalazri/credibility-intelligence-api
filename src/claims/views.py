# from django.shortcuts import render

# Create your views here.
from rest_framework import viewsets, filters
from .models import Claim, UserReport
from .serializers import ClaimSerializer, UserReportSerializer
from django_filters.rest_framework import DjangoFilterBackend
from .filters import ClaimFilter
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAuthenticated, IsAdminUser


class ClaimViewSet(viewsets.ReadOnlyModelViewSet):
    """
    Read-only endpoints for dataset claims.
    """
    queryset = Claim.objects.all()
    # queryset = Claim.objects.all().order_by("id")
    serializer_class = ClaimSerializer
    permission_classes = [AllowAny]

    filter_backends = [
        DjangoFilterBackend,
        filters.SearchFilter,
        filters.OrderingFilter,
    ]
    filterset_class = ClaimFilter
    search_fields = ["statement", "speaker", "subjects", "context"]
    ordering_fields = ["id", "created_at", "speaker", "label"]
    ordering = ["-created_at"]

    @action(detail=False, methods=["get"], url_path=r"by-speaker/(?P<speaker>[^/.]+)")
    def by_speaker(self, request, speaker=None):
        """
        Retrieve claims by speaker (case-insensitive substring match),
        with the same pagination/filtering/ordering behaviour as the main list.
        Example: /api/claims/by-speaker/obama?label=false&ordering=-created_at
        """
        qs = self.get_queryset().filter(speaker__icontains=speaker)

        # Apply any query param filters (label, party, state, split, etc.) via ClaimFilter
        qs = self.filter_queryset(qs)

        # Apply pagination like the main /api/claims/
        page = self.paginate_queryset(qs)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(qs, many=True)
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

    def get_permissions(self):
        if self.action in ["create", "list", "retrieve"]:
            return [IsAuthenticated()]
        return [IsAdminUser()]
