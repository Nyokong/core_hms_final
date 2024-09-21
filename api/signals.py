# signals.py
import logging

from django.dispatch import receiver
from django.shortcuts import redirect

from allauth.socialaccount.signals import social_account_added
from allauth.account.signals import user_logged_in
from django.db.models.signals import post_save
from allauth.socialaccount.models import SocialAccount

from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken

from .models import custUser, Lecturer
logger = logging.getLogger('api')

@receiver(post_save, sender=custUser)
def check_lecturer_status(sender, instance, created, **kwargs):
    if created:
        if instance.student_number:
            if Lecturer.objects.filter(emp_num=instance.student_number).exists():
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

@receiver(user_logged_in)
def user_logged_in_receiver(request, user, **kwargs):
    try:
        social_account = SocialAccount.objects.get(user=user)
        # tokens = get_tokens_for_user(user)
        tokens = "4321"
        # logger.info(f'Redirecting user {user} with token {tokens}')
        print(social_account)
        # login?token={tokens}
        return Response({'msg':'this is working?'})
    except SocialAccount.DoesNotExist:
        logger.info(f'User {user} does not have a social account.')
    
