from rest_framework.response import Response
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework import status
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.decorators import api_view
from .serializers import RegisterSerializer, LoginSerializer, RequestPasswordResetSerializer, SetNewPasswordSerializer
from rest_framework_simplejwt.token_blacklist.models import BlacklistedToken
from rest_framework_simplejwt.tokens import AccessToken
from django.contrib.auth.models import User
from django.utils.http import urlsafe_base64_encode
from django.utils.encoding import force_bytes
from django.conf import settings
from django.core.mail import send_mail
from django.contrib.auth.tokens import PasswordResetTokenGenerator


def get_tokens_for_user(user):
    refresh = RefreshToken.for_user(user)
    return {
        'refresh': str(refresh),
        'access': str(refresh.access_token)
    }


@api_view(['POST'])
def login(request):
    serializer = LoginSerializer(data=request.data)
    if serializer.is_valid():
        user = serializer.validated_data['user']
        tokens = get_tokens_for_user(user)
        return Response({"message": "Login successful", "user": user.username, "tokens": tokens},)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
def register(request):
    serializer = RegisterSerializer(data=request.data)
    if serializer.is_valid():
        user = serializer.save()
        tokens = get_tokens_for_user(user)
        return Response({"message": "User created successfully.",
                         "tokens": tokens}, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def logout(request):
    try:
        # getting the token from request header
        auth_header = request.META.get("AUTHORIZATION")
        if auth_header:
            token = auth_header.split()[1]
            # verifies whether the access token is correct or not
            access_token = AccessToken(token)
            # this line creates a new entry in the BlacklistedToken database table, effectively marking the token as invalid so it cannot be used for authentication anymore
            BlacklistedToken.objects.create(token=access_token)

        return Response({"message": "Logged out successfully"},
                        status=status.HTTP_205_RESET_CONTENT)
    except Exception as e:
        return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
@permission_classes([AllowAny])
def request_password_reset(request):
    # passing the requested email to data to RequestPasswordResetSerializer and checking if the email is there or not
    serializer = RequestPasswordResetSerializer(data=request.data)

    if serializer.is_valid():
        email = serializer.validated_data['email']
        user = User.objects.get(email=email)

        # checking in database if there was actually user registered with the given email
        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            return Response({
                "error": "User with this email does not exist."
            }, status=status.HTTP_404_NOT_FOUND)

        # a password reset token has been generated here
        token_generator = PasswordResetTokenGenerator()
        # the below line is used to securely encode the user's primary key user.pk into a format suitable for including a URL
        # why? because the primary key (user.pk) is a unique identifier for the user in the database, when the user clicks the reset link, the backend needs to know which account to reset
        uidb64 = urlsafe_base64_encode(force_bytes(user.pk))
        token = token_generator.make_token(user)

        reset_link = f"http://127.0.0.1:8000/api/reset-password/{uidb64}/{token}/"

        # sending mail with reset link
        send_mail(
            'Password Reset Request',
            f'You requested a password reset. Click the link below to reset your password:\n{reset_link}',
            settings.EMAIL_HOST_USER,
            [email],
            fail_silently=False,
        )

        return Response({"message": "Password reset link sent."},
                        status=200)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
@permission_classes([AllowAny])
def reset_password(request, uidb64, token):
    data = {
        'uidb64': uidb64,
        'token': token,
        'password': request.data.get('password')
    }

    serializer = SetNewPasswordSerializer(data=data)
    if serializer.is_valid():
        serializer.save()
        return Response({"message": "Password has been reset successfully."}, status=status.HTTP_200_OK)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
