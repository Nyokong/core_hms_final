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

from .models import Video
from api.tasks import create_m3u8_playlist

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
        # social_account = SocialAccount.objects.get(user=user)
        # # tokens = get_tokens_for_user(user)
        # tokens = "4321"
        # logger.info(f'Redirecting user {user} with token {tokens}')
        # print("user logged in:", social_account)
    try:
        # social_account = SocialAccount.objects.get(id=user)
        custom_user = custUser.objects.get(username=user)
        
        # Check if the student's number is empty
        if custom_user.student_number:
            logger.info(f'Student number Found: {user}')
            return False
        else:
            logger.info(f'No student number Found: {user}')
            return True
    except SocialAccount.DoesNotExist:
        logger.error(f'SocialAccount does not exist for user {user}')
        return False
    except custUser.DoesNotExist:
        logger.error(f'custUser does not exist for user {user}')
        return False


@receiver(post_save, sender=Video)
def create_video(sender, instance, created, **kwargs):
    if created:
        logger.info(f'Added video {instance.id} - now creating a task to generate .m3u8')
        # Trigger the background task to create the .m3u8 playlist
        # create_m3u8_playlist.delay(instance.cmp_video, instance.id,str(instance.cmp_video.path))
        create_m3u8_playlist.delay(instance.id)
