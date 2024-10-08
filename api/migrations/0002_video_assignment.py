# Generated by Django 5.1.1 on 2024-10-08 17:13

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='video',
            name='assignment',
            field=models.ForeignKey(default=None, on_delete=django.db.models.deletion.CASCADE, related_name='assignment', to='api.assignment', verbose_name='assignment'),
        ),
    ]