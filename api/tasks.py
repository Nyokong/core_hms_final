from __future__ import absolute_import, unicode_literals
import os
import m3u8

from django.conf import settings
from .models import Video
import logging
import tempfile
import subprocess

logger = logging.getLogger('api')

from celery import shared_task

logger.info("Tasks module loaded")

@shared_task
def add(x, y):
    return x + y
    
@shared_task
def test_ffmpeg(video_id):

    try:
        video_instance = Video.objects.get(id=video_id)
        logger.info(f'ID: {video_instance.id} - {video_instance.title}')

        output_dir = os.path.join(settings.MEDIA_ROOT, 'hls_videos', f'{str(video_instance.id)}_{str(video_instance.title)}')
        os.makedirs(output_dir, exist_ok=True)

        # file_obj = video_instance.cmp_video

        # Create a temporary file in the output directory
        temp_file_path = os.path.join(output_dir, 'temp_video.mp4')

        with open(temp_file_path, 'wb') as temp_file:
            # Write the content of the uploaded file to the temporary file
            # Write the content of the uploaded file to the temporary file
            for chunk in video_instance.cmp_video.chunks():
                temp_file.write(chunk)

        logger.info(f'FILE PATH: {temp_file_path}')

        command = [
            'ffmpeg', '-y', '-i', temp_file_path,
            '-vf', 'scale=w=1280:h=720', '-c:v', 'libx264', '-b:v', '3000k', '-hls_time', '10', '-hls_playlist_type', 'vod',
            '-hls_segment_filename', os.path.join(output_dir, '720p_%03d.ts'), os.path.join(output_dir, '720p.m3u8'),
            '-vf', 'scale=w=854:h=480', '-c:v', 'libx264', '-b:v', '1500k', '-hls_time', '10', '-hls_playlist_type', 'vod',
            '-hls_segment_filename', os.path.join(output_dir, '480p_%03d.ts'), os.path.join(output_dir, '480p.m3u8'),
            '-vf', 'scale=w=640:h=360', '-c:v', 'libx264', '-b:v', '800k', '-hls_time', '10', '-hls_playlist_type', 'vod',
            '-hls_segment_filename', os.path.join(output_dir, '360p_%03d.ts'), os.path.join(output_dir, '360p.m3u8')
        ]

        # Log the full FFmpeg command
        # logger.info(f'Running FFmpeg command: {" ".join(command)}')

        # subprocess.run(command, check=True)
        # Run FFmpeg command and capture output
        subprocess.run(command, capture_output=True, text=True)
        result = subprocess.run(command, capture_output=True, text=True)

        # Log FFmpeg output
        logger.info(f'FFmpeg stdout: {result.stdout}')
        logger.error(f'FFmpeg stderr: {result.stderr}')

        # Check if FFmpeg ran successfully
        if result.returncode != 0:
            logger.error('FFmpeg command failed')
            return None

        # Clean up temporary file
        os.remove(temp_file_path)

        # Save the path to the Video model
        video_instance.hls_path = f"hls_videos/{video_instance.id}_{video_instance.title}"
        video_instance.save()
        
        return output_dir
    except Exception as e:
        logger.error(f"Error during video processing: {e}")
        return None
