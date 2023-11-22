import pytest
from django.test import Client
from model_bakery import baker
from rest_framework.authtoken.models import Token
from rest_framework.test import APIClient
from device_management.models import CustomUser, Device
from device_management.views import register_user, login_user, get_devices, submit_data, add_device, update_device, delete_device, get_all_devices, get_user, update_device, get_all_users, manage_user_roles
import os
from django.conf import settings

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'iot_management_platform.settings')  # Set your actual settings module

# Configure Django settings
if not settings.configured:
    settings.configure()

# Your test code follows here
# ...

@pytest.fixture
def api_client():
    return APIClient()

@pytest.fixture
def user(db):
    user = baker.make(CustomUser, username='john', password='password123')
    user.set_password('password123')
    user.save()
    return user

@pytest.fixture
def device(db, user):
    return baker.make(Device, user=user, name='Device 1', location='Location 1')


BASE_URL = 'http://135.181.6.243:9000'


def test_register_user(api_client):
    response = api_client.post(f'{BASE_URL}/register/', {'username': 'john', 'password': 'password123'})
    assert response.status_code == 201
    assert 'access_token' in response.data
    assert 'message' in response.data
    assert response.data['message'] == 'User registered and logged in successfully'
    assert 'result' in response.data

def test_login_user(api_client, user):
    response = api_client.post(f'{BASE_URL}/login/', {'username': 'john', 'password': 'password123'})
    assert response.status_code == 200
    assert 'access_token' in response.data
    assert 'message' in response.data
    assert response.data['message'] == 'User logged in successfully'
    assert 'result' in response.data

def test_get_devices(api_client, user, device):
    api_client.force_authenticate(user=user)
    response = api_client.get(f'{BASE_URL}/devices/')
    assert response.status_code == 200
    assert len(response.data) == 1
    assert response.data[0]['name'] == 'Device 1'
    assert response.data[0]['location'] == 'Location 1'

def test_submit_data(api_client, user, device):
    api_client.force_authenticate(user=user)
    response = api_client.post(f'{BASE_URL}/devices/add/data/', {'device_id': device.id, 'data': 'Test data'})
    assert response.status_code == 201
    assert 'message' in response.data
    assert response.data['message'] == 'Data submitted successfully'
    assert 'result' in response.data

def test_add_device(api_client, user):
    api_client.force_authenticate(user=user)
    response = api_client.post(f'{BASE_URL}/devices/add/', {'name': 'Device 2', 'location': 'Location 2'})
    assert response.status_code == 201
    assert 'message' in response.data
    assert response.data['message'] == 'Device added successfully'
    assert 'result' in response.data

def test_update_device(api_client, user, device):
    api_client.force_authenticate(user=user)
    response = api_client.put(f'{BASE_URL}/devices/{device.id}/', {'name': 'Updated Device', 'location': 'Updated Location'})
    assert response.status_code == 200
    assert 'message' in response.data
    assert response.data['message'] == 'Device updated successfully'
    assert 'result' in response.data

def test_delete_device(api_client, user, device):
    api_client.force_authenticate(user=user)
    response = api_client.delete(f'{BASE_URL}/devices/{device.id}/delete/')
    assert response.status_code == 200
    assert 'message' in response.data
    assert response.data['message'] == 'Device deleted successfully'
    assert 'result' in response.data