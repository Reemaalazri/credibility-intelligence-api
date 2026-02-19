from django.urls import path
from rest_framework.routers import DefaultRouter
from .views import ClaimViewSet, UserReportViewSet
from .api_root import api_root
from .score import score_claim

router = DefaultRouter()
router.register(r"claims", ClaimViewSet, basename="claim")
router.register(r"reports", UserReportViewSet, basename="report")

# urlpatterns = router.urls

urlpatterns = [
    path("", api_root, name="api-root"),
    path("score/", score_claim, name="score-claim"),
]

urlpatterns += router.urls
