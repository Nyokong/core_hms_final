# Generated by Django 5.1.1 on 2024-09-24 20:39

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='video',
            name='hls_path',
            field=models.CharField(blank=True, max_length=255, null=True, verbose_name='Streaming_Path'),
        ),
        migrations.AlterField(
            model_name='submission',
            name='video',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='video_being_submitted', to='api.video'),
        ),
    ]
