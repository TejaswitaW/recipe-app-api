"""
Views for the user API.
"""
from rest_framework import generics,authentication,permissions
from rest_framework.authtoken.views import ObtainAuthToken
from rest_framework.settings import api_settings

from user.serializers import (
    UserSerializer,
    AuthTokenSerializer
)

class CreateUserView(generics.CreateAPIView):
    """Create a new user in the system."""
    serializer_class = UserSerializer

class CreateTokenView(ObtainAuthToken):
    """Create a new auth token for user."""
    serializer_class = AuthTokenSerializer
    renderer_classes = api_settings.DEFAULT_RENDERER_CLASSES

class ManageUserView(generics.RetrieveUpdateAPIView):
    """Manage the authenticated user."""
    serializer_class = UserSerializer
    authentication_classes = [authentication.TokenAuthentication]
    permission_classes = [permissions.IsAuthenticated]

    # This view is typically used for retrieving (GET) or updating (PUT/PATCH) information about a single object. 
    # In this case, the "object" is the authenticated user.
    # Since the view is for managing the authenticated user, 
    # it is necessary to retrieve the current user (from self.request.user)
    # to ensure that the user can only interact with their own data.
    def get_object(self):
        """Retrive and return the authenticated user."""
        return self.request.user
