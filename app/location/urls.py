"""
URL mappings for the location API.
"""
from django.urls import (
    path,
    include,
)

from rest_framework.routers import DefaultRouter

from location import views

router = DefaultRouter()
router.register('caverns', views.CavernsViewSet)
router.register('links', views.LinksViewSet)
router.register('favicon', views.FaviconView)

app_name = 'location'

urlpatterns = [
    path('', include(router.urls)),
]
