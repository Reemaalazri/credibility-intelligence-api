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

# {"refresh":"eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ0b2tlbl90eXBlIjoicmVmcmVzaCIsImV4cCI6MTc3MzEwMTk2MSwiaWF0IjoxNzczMDE1NTYxLCJqdGkiOiJkYWIxMGQ1MjQ5MzM0NDExYmFkYmY4ODlmNjk2ZmQ1MSIsInVzZXJfaWQiOiIxIn0.sjyWAc5l6EKkWofTx67Olj-HiNYpZD_D4W31nSAb-JM",
# "access":"eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ0b2tlbl90eXBlIjoiYWNjZXNzIiwiZXhwIjoxNzczMDE1ODYxLCJpYXQiOjE3NzMwMTU1NjEsImp0aSI6ImFjMTBmZGM2MWQ4NzQ0MDhiMmFhZGNjZDY0Y2UxNTJkIiwidXNlcl9pZCI6IjEifQ.z1VzIWibb_98AVevIFP_z-UaCoum4Ni_tZNoiZONg3g"}% 
# admin: reema, password: ibrahim123
from django.contrib import admin
from django.urls import path, include
from claims.score import score_claim
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
    TokenVerifyView,
)

urlpatterns = [
    path("admin/", admin.site.urls),
    path("api/", include("claims.urls")),
    path("api/score/", score_claim),

    path("api/auth/token/", TokenObtainPairView.as_view(), name="token_obtain_pair"),
    path("api/auth/token/refresh/", TokenRefreshView.as_view(), name="token_refresh"),
    path("api/auth/token/verify/", TokenVerifyView.as_view(), name="token_verify"),
]