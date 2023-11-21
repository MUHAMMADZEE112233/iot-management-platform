from rest_framework import serializers
from .models import CustomUser, Device, Data

class CustomUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomUser
        fields = ['id', 'username', 'email', 'role']

class DeviceSerializer(serializers.ModelSerializer):
    class Meta:
        model = Device
        fields = ['id', 'user', 'name', 'location']

class DataSerializer(serializers.ModelSerializer):
    class Meta:
        model = Data
        fields = ['id', 'device', 'timestamp', 'data']
