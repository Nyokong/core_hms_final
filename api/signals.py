# signals.py
from django.dispatch import receiver
from allauth.account.signals import user_logged_in
from rest_framework.response import Response

@receiver(user_logged_in)
def check_password_setting(sender, request, user, **kwargs):
    if user.needs_password:
        return Response({"error_google:", "password_empty"})