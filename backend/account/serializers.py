from django.contrib.auth.models import User
from django.contrib.auth import authenticate
from rest_framework import serializers
from rest_framework.validators import UniqueValidator

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
