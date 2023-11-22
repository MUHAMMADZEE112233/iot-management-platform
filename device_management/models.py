from django.contrib.auth.models import AbstractUser, Group, Permission
from django.db import models
from timescale.db.models.fields import TimescaleDateTimeField
from django.utils import timezone


class CustomUser(AbstractUser):
    ROLE_CHOICES = (
        ('LO', 'Lev Operator'),
        ('LE', 'Lev Engineer'),
        ('LM', 'Lev Manager'),
        ('OW', 'Owner'),
    )
    role = models.CharField(max_length=2, choices=ROLE_CHOICES, default='LO')
    groups = models.ManyToManyField(Group, related_name='custom_users_set')
    user_permissions = models.ManyToManyField(Permission, related_name='custom_users_set')


class Device(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    name = models.CharField(max_length=200)
    location = models.CharField(max_length=200)


class Data(models.Model):
    device = models.ForeignKey(Device, on_delete=models.CASCADE)
    timestamp = TimescaleDateTimeField(interval="1 day", default=timezone.now)
    data = models.JSONField()
