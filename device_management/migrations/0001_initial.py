# Generated by Django 4.2.7 on 2023-11-21 13:20

from django.db import migrations

class Migration(migrations.Migration):

    dependencies = [
        # Empty list means no dependencies
    ]

    operations = [
        migrations.RunSQL('CREATE EXTENSION IF NOT EXISTS timescaledb CASCADE;')
    ]
