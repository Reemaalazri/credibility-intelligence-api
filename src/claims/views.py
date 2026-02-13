#from django.shortcuts import render

# Create your views here.
from rest_framework import viewsets
from .models import Claim, UserReport
from .serializers import ClaimSerializer, UserReportSerializer


class ClaimViewSet(viewsets.ReadOnlyModelViewSet):
    """
    Read-only endpoints for dataset claims.
    """
    queryset = Claim.objects.all().order_by("id")
    serializer_class = ClaimSerializer


class UserReportViewSet(viewsets.ModelViewSet):
    """
    Full CRUD endpoints for user reports (coursework requirement).
    """
    queryset = UserReport.objects.all().order_by("-created_at")
    serializer_class = UserReportSerializer
