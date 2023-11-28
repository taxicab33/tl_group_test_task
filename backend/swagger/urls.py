from django.urls import re_path
from drf_spectacular.views import (
    SpectacularRedocView,
    SpectacularSwaggerView,
    SpectacularJSONAPIView
)

urlpatterns = [
    re_path('schema-json/', SpectacularJSONAPIView.as_view(), name='schema'),
    re_path('docs/redoc/', SpectacularRedocView.as_view(url_name='schema'), name='redoc'),
    re_path('docs/', SpectacularSwaggerView.as_view(url_name='schema'), name='swagger-ui'),
]
