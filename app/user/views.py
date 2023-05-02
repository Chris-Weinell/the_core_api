"""
Views for the user API.
"""
from rest_framework import generics
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework.permissions import IsAuthenticated
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer, TokenRefreshSerializer
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

from user.serializers import UserSerializer


class CreateUserView(generics.CreateAPIView):
    """Create a new user in the system."""
    serializer_class = UserSerializer


class ManageUserView(generics.RetrieveUpdateAPIView):
    """Manage the authenticated user."""
    serializer_class = UserSerializer
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    def get_object(self):
        """Retrieve and return the authenticated user."""
        return self.request.user


class CreateTokenView(TokenObtainPairView):
    """Create JSON Web Token for user"""
    serializer_class = TokenObtainPairSerializer


class RefreshTokenView(TokenRefreshView):
    """Refresh JSON Web Token for user"""
    serializer_class = TokenRefreshSerializer
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]