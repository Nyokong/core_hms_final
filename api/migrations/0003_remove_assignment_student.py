# Generated by Django 5.1.1 on 2024-09-27 02:09

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0002_alter_custuser_email'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='assignment',
            name='student',
        ),
    ]
