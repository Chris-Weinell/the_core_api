"""
Serializers for location APIs
"""
from rest_framework import serializers

from core.models import Caverns, Links


class CavernsSerializer(serializers.ModelSerializer):
    """Serializer for Caverns Objects"""

    class Meta:
        model = Caverns
        fields = '__all__'


class LinksSerializer(serializers.ModelSerializer):
    """Serializer for Links Objects"""

    class Meta:
        model = Links
        fields = '__all__'
