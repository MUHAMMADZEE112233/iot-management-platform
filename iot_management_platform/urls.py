from django.urls import path
from device_management import views

urlpatterns = [
    path('register_user/', views.register_user, name='register_user'),
    # path('register_device/', views.register_device, name='register_device'),
    # path('submit_device_data/', views.submit_device_data, name='submit_device_data'),
    # path('manage_devices/', views.manage_devices, name='manage_devices'),
    # path('manage_users/', views.manage_users, name='manage_users'),
]
