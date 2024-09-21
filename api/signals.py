# signals.py
from django.dispatch import receiver
from allauth.account.signals import user_logged_in
from rest_framework.response import Response

from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import custUser, Lecturer

@receiver(user_logged_in)
def check_password_setting(sender, request, user, **kwargs):
    if user.needs_password:
        return Response({"error_google:", "password_empty"})

@receiver(post_save, sender=custUser)
def check_lecturer_status(sender, instance, created, **kwargs):
    if created:
        if Lecturer.objects.filter(emp_num=instance.username).exists():
            instance.is_lecturer = True
            instance.save()
            print("a lecturer has been created")