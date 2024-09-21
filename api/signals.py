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
            print(f"Lecturer found: {instance.username}")
            instance.is_lecturer = True
            instance.save()
        else:
            print(f"No lecturer found for: {instance.username}")

from .models import Submission, FeedbackRoom

@receiver(post_save, sender=Submission)
def create_feedback_room(sender, instance, created, **kwargs):
    if created:
        assignment = instance.assignment
        lecturer = assignment.created_by
        student = instance.student

        if not FeedbackRoom.objects.filter(lecturer=lecturer, student=student, submission=instance).exists():
            FeedbackRoom.objects.create(
                lecturer=lecturer,
                student=student,
                submission=instance
            )