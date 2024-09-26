# signals.py
import logging
import re

from django.dispatch import receiver
from django.shortcuts import redirect

from allauth.socialaccount.signals import social_account_added
from allauth.account.signals import user_logged_in
from django.db.models.signals import post_save, post_delete
from allauth.socialaccount.models import SocialAccount

from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken

from .models import Video
from api.tasks import test_ffmpeg

# straight imports
from django.conf import settings
import os
import shutil

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


# video signals
@receiver(post_save, sender=Video)
def create_video(sender, instance, created, **kwargs):
    if created:
        logger.info(f'Name of VIDEO {instance.cmp_video.name}')
        logger.info(f'ID: {instance.id} - {instance.title}')

        # Use regex to find the numeric part at the end of the filename
        title_code = instance.title[:3].upper()
        full_name = f'{instance.cmp_video.name}'

        filename = full_name.split('/')[-1]

        # Find the position of the title_code in the filename
        pos = filename.find(title_code)
        if pos != -1:
            # Extract the part of the filename after the title_code
            numeric_part = filename[pos + len(title_code):]
            
        logger.info(f'Added video {instance.user.id}_{title_code}{str(numeric_part)} - now creating a task to generate .m3u8')
        # Trigger the background task to create the .m3u8 playlist
        test_ffmpeg.delay(instance.id)

@receiver(post_delete, sender=Video)
def delete_related_files(sender, instance, **kwargs):
    if instance.cmp_video:
        video_path = instance.cmp_video.path
        if os.path.isfile(video_path):
            os.remove(video_path)
            logger.info(f'video is deleted is deleted')

        # Deleting any other related files
        # Delete the thumbnail
        if instance.thumbnail:
            thumbnail_path = instance.thumbnail.path
            if os.path.isfile(thumbnail_path):
                os.remove(thumbnail_path)
                logger.info(f'thumbnail is deleted')

        # Delete the HLS folder
        hls_folder_name = f"{instance.id}_{instance.title}"
        hls_folder_path = os.path.join(settings.MEDIA_ROOT, 'hls_videos', hls_folder_name)
        if os.path.isdir(hls_folder_path):
            shutil.rmtree(hls_folder_path)
            logger.info(f'hls folder for {hls_folder_name} is deleted')
        else:
            logger.warning(f"HLS folder not found: {hls_folder_path}")




