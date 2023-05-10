from django.contrib import admin
from django.urls import path, include, re_path
from django.http import HttpResponseNotFound

from drf_spectacular.views import (
    SpectacularAPIView,
    SpectacularSwaggerView
)


urlpatterns = [
    path('admin/', admin.site.urls),
    path(
        'api/schema/',
        SpectacularAPIView.as_view(),
        name='api-schema'
    ),
    path(
        'api/docs/',
        SpectacularSwaggerView.as_view(url_name='api-schema'),
        name='api-docs'
    ),
    path('api/user/', include('user.urls')),
    path('api/location/', include('location.urls')),
    re_path(
        r'^favicon\.ico$', 
        lambda request: HttpResponseNotFound(), 
        name='favicon'
    ),
]
