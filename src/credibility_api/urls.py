"""
URL configuration for credibility_api project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/6.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from claims.score import score_claim
from claims.views import RegisterView
from claims.home import home
# JWT authentication endpoints
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
    TokenVerifyView,
)
# OpenAPI / Swagger documentation endpoints
from drf_spectacular.views import (
    SpectacularAPIView,
    SpectacularSwaggerView,
    SpectacularRedocView,
)

urlpatterns = [
    path("", home, name="home"),
    path("admin/", admin.site.urls),
    path("api/", include("claims.urls")),
    path("api/score/", score_claim),

    # User registration
    path("api/auth/register/", RegisterView.as_view(), name="auth-register"),
    # JWT login (returns access and refresh tokens)
    path("api/auth/token/", TokenObtainPairView.as_view(), name="token_obtain_pair"),
    # Refresh expired access token
    path("api/auth/token/refresh/", TokenRefreshView.as_view(), name="token_refresh"),
    # Verify JWT token validity
    path("api/auth/token/verify/", TokenVerifyView.as_view(), name="token_verify"),
    
    # Login for Django REST Framework browsable API
    path("api-auth/", include("rest_framework.urls")),

    # OpenAPI schema
    path("api/schema/", SpectacularAPIView.as_view(), name="schema"),
    # Swagger interactive API documentation
    path("api/schema/swagger-ui/", SpectacularSwaggerView.as_view(url_name="schema"), name="swagger-ui"),
    # ReDoc API documentation
    path("api/schema/redoc/", SpectacularRedocView.as_view(url_name="schema"), name="redoc"),
]
