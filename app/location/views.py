"""
Views for the location APIs.
"""

from rest_framework import viewsets, mixins

from . import serializers
from core.models import Caverns, Links


class CavernsViewSet(
    mixins.RetrieveModelMixin,
    mixins.ListModelMixin,
    viewsets.GenericViewSet
):
    """Viewset for retrieving from Caverns API"""
    queryset = Caverns.objects.all()
    serializer_class = serializers.CavernsSerializer


class LinksViewSet(
    mixins.RetrieveModelMixin,
    mixins.ListModelMixin,
    viewsets.GenericViewSet
):
    """Viewset for retrieving from Links API"""
    queryset = Links.objects.all()
    serializer_class = serializers.LinksSerializer
