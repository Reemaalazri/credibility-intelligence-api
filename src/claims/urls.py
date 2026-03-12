from django.urls import path
from rest_framework.routers import DefaultRouter
from .views import ClaimViewSet, UserReportViewSet
from .api_root import api_root
from .score import score_claim

# Router automatically generates CRUD routes for claims and reports
router = DefaultRouter()
router.register(r"claims", ClaimViewSet, basename="claim")
router.register(r"reports", UserReportViewSet, basename="report")

# Core API endpoints
urlpatterns = [
    # API root listing available endpoints
    path("", api_root, name="api-root"),
    # Claim credibility scoring endpoint
    path("score/", score_claim, name="score-claim"),
]

# Add automatically generated router endpoints
urlpatterns += router.urls
