from django.urls import path, re_path
from drf_yasg import openapi
from drf_yasg.views import get_schema_view
from rest_framework import permissions

from device_management import views

schema_view = get_schema_view(
    openapi.Info(
        title="IOT Management API",
        default_version='v1',
    ),
    public=True,
    permission_classes=[permissions.AllowAny],
)

urlpatterns = [
    path('register/', views.register_user, name='register_user'),
    path('login/', views.login_user, name='login'),
    path('users/all/', views.get_all_users, name='get_all_users'),
    path('users/<int:user_id>/', views.get_user, name='get_user'),
    path('users/<int:user_id>/roles/', views.manage_user_roles, name='manage_user_roles'),
    path('users/<int:user_id>/delete/', views.delete_user, name='delete_user'),
    path('devices/', views.get_devices, name='get_devices'),
    path('devices/all/', views.get_all_devices, name='get_all_devices'),
    path('devices/add/', views.add_device, name='add_device'),
    path('devices/<int:device_id>/', views.update_device, name='update_device_info'),
    path('devices/<int:device_id>/delete/', views.delete_device, name='delete_device'),
    path('devices/add/data/', views.submit_data, name='submit_data'),
    re_path(r'^swagger(?P<format>\.json|\.yaml)$', schema_view.without_ui(cache_timeout=0), name='schema-json'),
    path('swagger/', schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'),
    path('redoc/', schema_view.with_ui('redoc', cache_timeout=0), name='schema-redoc'),
]
