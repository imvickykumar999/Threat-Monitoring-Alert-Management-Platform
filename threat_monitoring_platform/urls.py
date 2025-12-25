from django.contrib import admin
from django.urls import path, include, re_path
from django.views.generic import RedirectView
from rest_framework import permissions
from drf_yasg.views import get_schema_view
from drf_yasg import openapi
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)

# Swagger/OpenAPI schema configuration
schema_view = get_schema_view(
    openapi.Info(
        title="Threat Monitoring & Alert Management Platform API",
        default_version="v1",
        description="API for threat monitoring and alert management system",
        terms_of_service="https://www.google.com/policies/terms/",
        contact=openapi.Contact(email="contact@threatmonitoring.local"),
        license=openapi.License(name="MIT License"),
    ),
    public=True,
    permission_classes=[permissions.AllowAny],
    url="https://siem.imvickykumar999.dpdns.org",
)

urlpatterns = [
    # Redirect root → Swagger UI
    path("", RedirectView.as_view(url="/api/", permanent=False)),

    # Admin
    path("admin/", admin.site.urls),

    # JWT Authentication
    path("api/auth/token/", TokenObtainPairView.as_view(), name="token_obtain_pair"),
    path("api/auth/token/refresh/", TokenRefreshView.as_view(), name="token_refresh"),

    # API routes
    path("api/", include("monitoring.urls")),

    # Swagger / OpenAPI
    re_path(
        r"^swagger(?P<format>\.json|\.yaml)$",
        schema_view.without_ui(cache_timeout=0),
        name="schema-json",
    ),
    path(
        "swagger/",
        schema_view.with_ui("swagger", cache_timeout=0),
        name="schema-swagger-ui",
    ),
    path(
        "redoc/",
        schema_view.with_ui("redoc", cache_timeout=0),
        name="schema-redoc",
    ),
    path(
        "openapi/",
        RedirectView.as_view(url="/swagger.json", permanent=False),
    ),
]
