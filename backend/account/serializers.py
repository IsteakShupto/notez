from django.contrib.auth.models import User
from django.contrib.auth import authenticate
from rest_framework import serializers
from rest_framework.validators import UniqueValidator
from django.utils.http import urlsafe_base64_decode
from django.utils.encoding import force_str
from django.contrib.auth.tokens import PasswordResetTokenGenerator


# serializers.Serializer vs serializers.ModelSerializer = here ModelSerializer is tied to a django model and Serializer is not tied to any model
class LoginSerializer(serializers.Serializer):
    # setting the required criteria on username and password, these values will eventually come from frontend, i am just defining requirements for them to client-side
    username = serializers.CharField(required=True)
    password = serializers.CharField(write_only=True, required=True)

    def validate(self, data):
        username = data.get('username')
        password = data.get('password')

        user = authenticate(username=username, password=password)
        if user is None:
            raise serializers.ValidationError("Invalid username or password.")
        data['user'] = user
        return data


class RegisterSerializer(serializers.ModelSerializer):
    # below, i am customizing and giving requirements to email and password fields of django/drf's built in custom user model

    # and password2 is just a write_only field, i will not store it in db so i didn't create any models for it
    email = serializers.EmailField(
        required=True,
        validators=[UniqueValidator(queryset=User.objects.all())]
    )
    password = serializers.CharField(
        write_only=True, required=True, min_length=8)
    password2 = serializers.CharField(
        write_only=True, required=True, label='Confirm Password')

    class Meta:
        model = User
        fields = ('username', 'email', 'password', 'password2')

    def validate(self, data):
        if data['password'] != data['password2']:
            raise serializers.ValidationError("Passwords do not match.")
        return data

    def create(self, validated_data):
        user = User.objects.create_user(
            username=validated_data['username'],
            email=validated_data['email'],
            password=validated_data['password']
        )
        return user


# password reset request serializer
class RequestPasswordResetSerializer(serializers.Serializer):
    email = serializers.EmailField()

    def validate_email(self, value):
        # checking if database contains the email user is trying reset password on
        if not User.objects.filter(email=value).exists():
            raise serializers.ValidationError(
                "User with this email does not exist.")
        return value


# resetting the password serializer
class SetNewPasswordSerializer(serializers.Serializer):
    password = serializers.CharField(
        write_only=True, min_length=8, max_length=128)
    uidb64 = serializers.CharField()
    token = serializers.CharField()

    def validate(self, data):
        try:
            uid = force_str(urlsafe_base64_decode(data['uidb64']))
            user = User.objects.get(pk=uid)
        except (TypeError, ValueError, OverflowError, User.DoesNotExist):
            raise serializers.ValidationError("Invalid token or user ID.")

        # PasswordResetTokenGenerator is a powerful class which have a lot of functions like check token, validate token, generate tokens etc.
        token_generator = PasswordResetTokenGenerator()
        # internally django/drf creates a token for the user, using user id, password hash, timestamp(when the token was created - internally this value gets collected by django/drf) and then it checks if the current token gets matched with the token that i got from request reset password views
        if not token_generator.check_token(user, data['token']):
            raise serializers.ValidationError("Invalid or expired token.")
        return data

    def save(self, **Kwargs):
        # force_str = converts byte string to regular python string
        uid = force_str(urlsafe_base64_decode(self.validated_data['uidb64']))
        user = User.objects.get(pk=uid)
        user.set_password(self.validated_data['password'])
        user.save()
        return user
