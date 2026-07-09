from django.utils import timezone
from rest_framework import generics, permissions, status
from rest_framework.views import APIView
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from .models import User
from .serializers import UserSerializer, UserUpdateSerializer, tokens_for_user, RegisterSerializer, LoginSerializer

def auth_payload(user):
    """Helper function: 
    Returns a dictionary containing the user's serialized data and JWT tokens.
    """
    data = UserSerializer(user).data
    data.update(tokens_for_user(user)) # both refresh token and access token will be sending to the frontend
    return data

class CurrentUserView(generics.RetrieveUpdateAPIView):
    """Get or update the currently authenticated user's profile."""
    permission_classes = [permissions.IsAuthenticated]

    def get_serializer_class(self):
        if self.request.method in ('PUT', 'PATCH'):
            return UserUpdateSerializer
        return UserSerializer

    def get_object(self):
        return self.request.user

class RegisterView(APIView):
    """Register a new user. Returns the user's data and JWT tokens upon successful registration."""
    permission_classes = [permissions.AllowAny]
    def post(self, request):
        serializer = RegisterSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        return Response(auth_payload(user), status=status.HTTP_201_CREATED)
    

class LoginView(APIView):
    """Authenticate a user and return their data along with JWT tokens."""
    permission_classes = [permissions.AllowAny]
    def post(self, request):
        serializer = LoginSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        return Response(auth_payload(serializer.validated_data["user"]), status=status.HTTP_200_OK)

# @api_view(['POST'])
# @permission_classes([permissions.IsAuthenticated])
# def sync_user(request):
#     """
#     Sync Firebase user data to local database.
#     Called by frontend after Firebase login to ensure backend user exists
#     and name are up to date.
#     """
#     user = request.user
#     name = request.data.get('name', '')
#     update_fields = []

#     if name:
#         parts = name.split(' ', 1)
#         first = parts[0]
#         last = parts[1] if len(parts) > 1 else ''
#         if user.first_name != first:
#             user.first_name = first
#             update_fields.append('first_name')
#         if user.last_name != last:
#             user.last_name = last
#             update_fields.append('last_name')

#     if update_fields:
#         user.save(update_fields=update_fields)

#     return Response(UserSerializer(user).data)