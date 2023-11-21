from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from django.contrib.auth.hashers import make_password
from rest_framework_simplejwt.tokens import RefreshToken
from .models import CustomUser
from .serializers import CustomUserSerializer
from django.contrib.auth import login

@api_view(['POST'])
def register_user(request):
    try:
        data = request.data
        if 'username' not in data or 'password' not in data:
            return Response({'error': 'Please provide both username and password'}, status=status.HTTP_400_BAD_REQUEST)

        username = data['username']
        if CustomUser.objects.filter(username=username).exists():
            return Response({'error': 'Username already exists'}, status=status.HTTP_400_BAD_REQUEST)

        data['password'] = make_password(data['password'])
        serializer = CustomUserSerializer(data=data)
        if serializer.is_valid():
            user = serializer.save()

            # Generate JWT token
            refresh = RefreshToken.for_user(user)

            # Log in the user
            login(request, user)

            return Response({
                'access_token': str(refresh.access_token),
                'message': 'User registered and logged in successfully',
                'result': serializer.data
            }, status=status.HTTP_201_CREATED)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    except KeyError:
        return Response({'error': 'Invalid input data'}, status=status.HTTP_400_BAD_REQUEST)

