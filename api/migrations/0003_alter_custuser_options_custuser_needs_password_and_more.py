# Generated by Django 5.1.1 on 2024-09-20 22:02

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0002_assignment_submitted_grade_video'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='custuser',
            options={},
        ),
        migrations.AddField(
            model_name='custuser',
            name='needs_password',
            field=models.BooleanField(default=True),
        ),
        migrations.AlterUniqueTogether(
            name='custuser',
            unique_together={('username',)},
        ),
    ]
