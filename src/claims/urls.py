from rest_framework.routers import DefaultRouter
from .views import ClaimViewSet, UserReportViewSet

router = DefaultRouter()
router.register(r"claims", ClaimViewSet, basename="claim")
router.register(r"reports", UserReportViewSet, basename="report")

urlpatterns = router.urls
