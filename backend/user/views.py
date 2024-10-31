from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework import status
from .models import Profile
from .serializers import ProfileSerializer


@api_view(['GET', 'POST'])
@permission_classes([IsAuthenticated])
def profiles_list(request):
    if request.method == 'GET':
        # Get a list of all profiles
        profiles = Profile.objects.all()
        # many=True, because we want to serialize everything inside products
        serializer = ProfileSerializer(profiles, many=True)
        return Response(serializer.data)

    if request.method == 'POST':
        serializer = ProfileSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET', 'PUT', 'DELETE'])
@permission_classes([IsAuthenticated])
def profile(request, pk):
    try:
        # Get individual profile based on provided pk
        profile_instance = Profile.objects.get(id=pk)
    except Profile.DoesNotExist:
        return Response(status=status.HTTP_404_NOT_FOUND)

    if request.method == 'GET':
        serializer = ProfileSerializer(profile_instance)
        return Response(serializer.data)

    if request.method == 'PUT':
        serializer = ProfileSerializer(profile_instance, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    if request.method == 'DELETE':
        profile_instance.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
