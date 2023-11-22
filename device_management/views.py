from django.contrib.auth import login
from django.contrib.auth.hashers import make_password
from django.shortcuts import get_object_or_404
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken

from .models import Device, CustomUser
from .permissions import IsLO, IsLE, IsLM, IsOW
from .serializers import DeviceSerializer, DataSerializer, CustomUserSerializer


@api_view(['POST'])
def register_user(request):
    """
    Registers a new user and handles the user registration process.

    Args:
        request (object): The HTTP request object containing the user registration data.

    Returns:
        Response: The HTTP response object with the access token, success message, and user data.

    Raises:
        KeyError: If the required fields are not provided in the request data.
    """
    try:
        data = request.data
        username = data.get('username')
        password = data.get('password')

        if not username or not password:
            return Response({'error': 'Please provide both username and password'}, status=status.HTTP_400_BAD_REQUEST)

        if CustomUser.objects.filter(username=username).exists():
            return Response({'error': 'Username already exists'}, status=status.HTTP_400_BAD_REQUEST)

        data['password'] = make_password(password)
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


@api_view(['POST'])
def login_user(request):
    """
    Handles the login functionality for a user.

    Args:
        request (POST request object): The HTTP request object containing the login data in the request body.

    Returns:
        Response: A success response with the generated JWT token and a message indicating successful login, along with the serialized user data.
                    An error response indicating the reason for the error.

    Example Usage:
        # Request data:
        {
            "username": "john",
            "password": "password123"
        }

        # Response (success):
        {
            "access_token": "<JWT access token>",
            "message": "User registered and logged in successfully",
            "result": "<serialized user data>"
        }

        # Response (error - missing username):
        {
            "error": "Please provide both username and password"
        }

        # Response (error - invalid password):
        {
            "error": "Invalid password"
        }
    """
    try:
        data = request.data
        if 'username' not in data or 'password' not in data:
            return Response({'error': 'Please provide both username and password'}, status=status.HTTP_400_BAD_REQUEST)

        username = data['username']
        password = data['password']

        user = get_object_or_404(CustomUser, username=username)

        if not user.check_password(password):
            return Response({'error': 'Invalid password'}, status=status.HTTP_400_BAD_REQUEST)

        # Generate JWT token
        refresh = RefreshToken.for_user(user)

        # Log in the user
        login(request, user)

        serializer = CustomUserSerializer(user)
        return Response({
            'access_token': str(refresh.access_token),
            'message': 'User logged in successfully',
            'result': serializer.data
        }, status=status.HTTP_200_OK)

    except KeyError:
        return Response({'error': 'Invalid input data'}, status=status.HTTP_400_BAD_REQUEST)


"""
Lev Operator
Permissions:

Device Management:
View assigned devices
Submit data to assigned devices
User Interaction:
View basic user profile
Endpoints:

GET /devices: Retrieve assigned devices
POST /data/submit: Submit data to assigned devices
GET /users/{user_id}: View basic user profile
"""


@api_view(['GET'])
@permission_classes([IsAuthenticated, IsLO])
def get_devices(request):
    """
    Retrieves a list of devices associated with a specific user.

    Args:
        request (object): The request object containing information about the current request.

    Returns:
        list: A list of serialized device data.

    Example Usage:
        ```python
        # Import necessary modules and classes

        # Define the function
        @api_view(['GET'])
        @permission_classes([IsAuthenticated, IsLO])
        def get_devices(request):
            # Retrieve devices associated with the current user
            devices = Device.objects.filter(user=request.user)
            # Serialize the devices data
            serializer = DeviceSerializer(devices, many=True)
            # Return the serialized data as a response
            return Response(serializer.data)
        ```
    """
    devices = Device.objects.filter(user=request.user)
    serializer = DeviceSerializer(devices, many=True)
    return Response(serializer.data)


@api_view(['POST'])
@permission_classes([IsAuthenticated, IsLO])
def submit_data(request):
    """
    Submit data to a device.

    Args:
        request (HttpRequest): The HTTP request object.

    Returns:
        Response: The HTTP response object.

    Raises:
        Http404: If the device with the given device_id is not found.
        PermissionDenied: If the user is not authorized to submit data to the device.
        KeyError: If the input data is invalid.
    """
    try:
        data = request.data
        device_id = data.get('device_id')
        data_value = data.get('data')

        if not device_id or not data_value:
            return Response({'error': 'Please provide both device_id and data'}, status=status.HTTP_400_BAD_REQUEST)

        device = Device.objects.filter(id=device_id).first()
        if not device or (device.user != request.user or device.user.role not in ['LM', 'OW']):
            return Response({'error': 'You are not authorized to submit data to this device'},
                            status=status.HTTP_401_UNAUTHORIZED)

        data['device'] = device_id
        serializer = DataSerializer(data=data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    except KeyError:
        return Response({'error': 'Invalid input data'}, status=status.HTTP_400_BAD_REQUEST)


"""
Lev Engineer
Permissions:

Device Management:
Add new devices
Update device information

Endpoints:

POST /devices: Add new devices
PUT /devices/{device_id}: Update device information
GET /users/{user_id}/details: View detailed user profiles
"""


@api_view(['POST'])
@permission_classes([IsAuthenticated, IsLE])
def add_device(request):
    """
    Add a new device.

    Args:
        request (HttpRequest): The HTTP request object.

    Returns:
        Response: The HTTP response object.

    Raises:
        KeyError: If the input data is invalid.
    """
    try:
        data = request.data
        if 'name' not in data or 'location' not in data:
            return Response({'error': 'Please provide both name and location'}, status=status.HTTP_400_BAD_REQUEST)

        if 'user' in data:
            user = get_object_or_404(CustomUser, username=data['user'])
            if user:
                data['user'] = user.id
            else:
                data['user'] = request.user.id
        else:
            data['user'] = request.user.id
        serializer = DeviceSerializer(data=data)

        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    except KeyError:
        return Response({'error': 'Invalid input data'}, status=status.HTTP_400_BAD_REQUEST)


@api_view(['PUT'])
@permission_classes([IsAuthenticated, IsLE])
def update_device(request, device_id):
    """
    Update a device with the provided device_id.

    Args:
        request (HttpRequest): The HTTP request object.
        device_id (int): The ID of the device to be updated.

    Returns:
        Response: The HTTP response containing the updated device data or an error message.

    Raises:
        KeyError: If the input data is invalid.

    """
    try:
        device = get_object_or_404(Device, id=device_id)
        if device.user != request.user or device.user.role not in ['LM', 'OW']:
            return Response({'error': 'You are not authorized to update this device'},
                            status=status.HTTP_401_UNAUTHORIZED)

        data = request.data
        if 'name' not in data or 'location' not in data:
            return Response({'error': 'Please provide both name and location'}, status=status.HTTP_400_BAD_REQUEST)

        serializer = DeviceSerializer(device, data=data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    except KeyError:
        return Response({'error': 'Invalid input data'}, status=status.HTTP_400_BAD_REQUEST)


"""
Lev Manager
Permissions:

Device Management:
Delete devices
View all devices
View users

Endpoints:

DELETE /devices/{device_id}: Delete devices
GET /devices/all: View all devices
PUT /users/{user_id}/permissions: Manage user roles and permissions
"""


@api_view(['DELETE'])
@permission_classes([IsAuthenticated, IsLM])
def delete_device(request, device_id):
    """
    Delete a device.

    Args:
        request (Request): The HTTP request object.
        device_id (int): The ID of the device to be deleted.

    Returns:
        Response: The HTTP response object with a success message.
    """
    device = get_object_or_404(Device, id=device_id)
    device.delete()
    return Response({'message': 'Device deleted successfully'}, status=status.HTTP_200_OK)


@api_view(['GET'])
@permission_classes([IsAuthenticated, IsLM])
def get_all_devices(request):
    """
    Retrieve all devices.

    This API endpoint allows authenticated users with LM (License Manager) permission
    to retrieve a list of all devices in the system.

    Returns:
        Response: A response object containing serialized data of all devices.
    """
    devices = Device.objects.all()
    serializer = DeviceSerializer(devices, many=True)
    return Response(serializer.data)


@api_view(['GET'])
@permission_classes([IsAuthenticated, IsLM])
def get_user(request, user_id):
    """
    Retrieve a specific user by their ID.

    Args:
        request (HttpRequest): The HTTP request object.
        user_id (int): The ID of the user to retrieve.

    Returns:
        Response: The serialized data of the retrieved user.
    """
    user = get_object_or_404(CustomUser, id=user_id)
    serializer = CustomUserSerializer(user)
    return Response(serializer.data)


"""
Owner
Permissions:

Device Management:
Full control over devices
User Interaction:
Manage all aspects of users and their roles
Endpoints:

DELETE /devices/{device_id}: Delete devices
PUT /devices/{device_id}: Modify device details
GET /users: View all users
PUT /users/{user_id}/roles: Manage user roles and permissions
"""


@api_view(['PUT'])
@permission_classes([IsAuthenticated, IsOW])
def update_device(request, device_id):
    """
    Update a device with the provided data.

    Args:
        request (HttpRequest): The HTTP request object.
        device_id (int): The ID of the device to be updated.

    Returns:
        Response: The HTTP response containing the updated device data or error message.
    """
    try:
        device = get_object_or_404(Device, id=device_id)
        data = request.data
        if 'name' not in data or 'location' not in data or 'user' not in data:
            return Response({'error': 'Please provide name, location and user'}, status=status.HTTP_400_BAD_REQUEST)

        serializer = DeviceSerializer(device, data=data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    except KeyError:
        return Response({'error': 'Invalid input data'}, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET'])
@permission_classes([IsAuthenticated, IsOW])
def get_all_users(request):
    """
    Retrieve all users.

    This API endpoint returns a list of all users in the system.

    Parameters:
        request (HttpRequest): The HTTP request object.

    Returns:
        Response: The HTTP response containing the serialized data of all users.
    """
    users = CustomUser.objects.all()
    serializer = CustomUserSerializer(users, many=True)
    return Response(serializer.data)


@api_view(['PUT'])
@permission_classes([IsAuthenticated, IsOW])
def manage_user_roles(request, user_id):
    """
    Manage the roles of a user.

    Args:
        request (HttpRequest): The HTTP request object.
        user_id (int): The ID of the user.

    Returns:
        Response: The HTTP response object.

    Raises:
        Http404: If the user with the given ID does not exist.
        KeyError: If there is an invalid input data.
    """
    try:
        user = get_object_or_404(CustomUser, id=user_id)
        data = request.data
        if 'role' not in data:
            return Response({'error': 'Please provide the updated role of the user'}, status=status.HTTP_400_BAD_REQUEST)

        serializer = CustomUserSerializer(user, data=data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    except KeyError:
        return Response({'error': 'Invalid input data'}, status=status.HTTP_400_BAD_REQUEST)


@api_view(['DELETE'])
@permission_classes([IsAuthenticated, IsOW])
def delete_user(request, user_id):
    """
    Delete a user with the given user_id.

    Args:
        request (HttpRequest): The HTTP request object.
        user_id (int): The ID of the user to be deleted.

    Returns:
        Response: A response indicating the success of the operation.
    """
    user = get_object_or_404(CustomUser, id=user_id)
    user.delete()
    return Response({'message': 'User deleted successfully'}, status=status.HTTP_200_OK)