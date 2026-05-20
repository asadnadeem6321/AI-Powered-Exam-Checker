"""
Views for User authentication and management
"""
from rest_framework import status, generics
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth import authenticate, get_user_model
from .serializers import (
    UserRegistrationSerializer,
    UserSerializer,
    UserLoginSerializer
)
from .serializers import (
    PasswordResetRequestSerializer,
    PasswordResetConfirmSerializer,
)
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes, force_str
from django.contrib.auth.tokens import default_token_generator
from django.core.mail import send_mail
from django.conf import settings
from django.contrib.auth.password_validation import validate_password
import os
import logging

logger = logging.getLogger(__name__)

User = get_user_model()


class UserRegistrationView(generics.CreateAPIView):
    """
    API endpoint for user registration
    POST /api/users/register/
    """
    queryset = User.objects.all()
    permission_classes = [AllowAny]
    serializer_class = UserRegistrationSerializer
    
    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        
        # Generate tokens
        refresh = RefreshToken.for_user(user)
        
        logger.info(f"New user registered: {user.email}")
        
        return Response({
            'message': 'User registered successfully',
            'user': UserSerializer(user).data,
            'tokens': {
                'refresh': str(refresh),
                'access': str(refresh.access_token),
            }
        }, status=status.HTTP_201_CREATED)


@api_view(['POST'])
@permission_classes([AllowAny])
def user_login(request):
    """
    API endpoint for user login
    POST /api/users/login/
    """
    serializer = UserLoginSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    
    email = serializer.validated_data['email']
    password = serializer.validated_data['password']
    
    user = authenticate(username=email, password=password)
    
    if user is None:
        logger.warning(f"Failed login attempt for email: {email}")
        return Response({
            'error': 'Invalid credentials'
        }, status=status.HTTP_401_UNAUTHORIZED)
    
    if not user.is_active:
        return Response({
            'error': 'User account is disabled'
        }, status=status.HTTP_403_FORBIDDEN)
    
    # Generate tokens
    refresh = RefreshToken.for_user(user)
    
    logger.info(f"User logged in: {user.email}")
    
    return Response({
        'message': 'Login successful',
        'user': UserSerializer(user).data,
        'tokens': {
            'refresh': str(refresh),
            'access': str(refresh.access_token),
        }
    }, status=status.HTTP_200_OK)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def user_profile(request):
    """
    API endpoint to get user profile
    GET /api/users/profile/
    """
    user = request.user
    serializer = UserSerializer(user)
    
    return Response({
        'user': serializer.data
    }, status=status.HTTP_200_OK)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def user_logout(request):
    """
    API endpoint for user logout
    POST /api/users/logout/
    """
    try:
        refresh_token = request.data.get('refresh_token')
        if refresh_token:
            token = RefreshToken(refresh_token)
            token.blacklist()
        
        logger.info(f"User logged out: {request.user.email}")
        
        return Response({
            'message': 'Logout successful'
        }, status=status.HTTP_200_OK)
    except Exception as e:
        logger.error(f"Error during logout: {str(e)}")
        return Response({
            'error': 'Logout failed'
        }, status=status.HTTP_400_BAD_REQUEST)



@api_view(['POST'])
@permission_classes([AllowAny])
def password_reset_request(request):
    """
    Request a password reset email.
    POST /api/users/password-reset/  { email }
    """
    serializer = PasswordResetRequestSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)

    email = serializer.validated_data['email']

    try:
        user = User.objects.get(email__iexact=email)
    except User.DoesNotExist:
        # Do not reveal whether an account exists
        return Response({'message': 'If an account with that email exists, a password reset link will be sent.'}, status=status.HTTP_200_OK)

    uid = urlsafe_base64_encode(force_bytes(user.pk))
    token = default_token_generator.make_token(user)

    frontend_url = os.getenv('FRONTEND_URL', 'http://localhost:3000')
    reset_link = f"{frontend_url}/reset-password?uid={uid}&token={token}"

    subject = 'Password Reset Request'
    message = f"Hi {getattr(user, 'name', '') or user.email},\n\nUse the link below to reset your password:\n{reset_link}\n\nIf you did not request this, you can safely ignore this email.\n"

    from_email = getattr(settings, 'DEFAULT_FROM_EMAIL', 'noreply@example.com')

    try:
        send_mail(subject, message, from_email, [user.email], fail_silently=False)
    except Exception as e:
        logger.error(f"Error sending password reset email: {str(e)}")
        return Response({'error': 'Failed to send email'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    return Response({'message': 'Password reset email sent'}, status=status.HTTP_200_OK)


@api_view(['POST'])
@permission_classes([AllowAny])
def password_reset_confirm(request):
    """
    Confirm password reset with uid and token.
    POST /api/users/password-reset/confirm/  { uid, token, new_password }
    """
    serializer = PasswordResetConfirmSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)

    uidb64 = serializer.validated_data['uid']
    token = serializer.validated_data['token']
    new_password = serializer.validated_data['new_password']

    try:
        uid = force_str(urlsafe_base64_decode(uidb64))
        user = User.objects.get(pk=uid)
    except Exception:
        return Response({'error': 'Invalid uid'}, status=status.HTTP_400_BAD_REQUEST)

    if not default_token_generator.check_token(user, token):
        return Response({'error': 'Invalid or expired token'}, status=status.HTTP_400_BAD_REQUEST)

    try:
        validate_password(new_password, user)
    except Exception as e:
        return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)

    user.set_password(new_password)
    user.save()

    return Response({'message': 'Password has been reset successfully'}, status=status.HTTP_200_OK)
