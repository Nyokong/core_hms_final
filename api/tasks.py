from __future__ import absolute_import, unicode_literals
import os
import json

from django.conf import settings
from .models import Video
import logging
import tempfile
import subprocess

logger = logging.getLogger('api')

from celery import shared_task

logger.info("Tasks module loaded")

@shared_task
def encode_ffmpeg(video_id, input_file_path):
    try:
        from api.models import Video
        
        # Log the video ID being processed
        logger.info(f"Processing video with ID: {video_id}")

        try:
            video = Video.objects.get(id=video_id)
            logger.info(f"Found video: {video}")

        except Video.DoesNotExist:
            logger.error(f"Video with ID {video_id} does not exist.")
            return None

        title_code = video.title[:3].upper()
        full_name = video.cmp_video.name
        filename = full_name.split('/')[-1]

        # Extract the numeric part after the title code
        pos = filename.find(title_code)
        if pos != -1:
            numeric_part = filename[pos + len(title_code):]
        else:
            numeric_part = ""

        fullvid = f'{video.user.id}_{title_code}{numeric_part}'
        name_without_extension = fullvid.rsplit('.', 1)[0]

        output_dir = os.path.join(settings.MEDIA_ROOT, 'hls_videos', name_without_extension)
        os.makedirs(output_dir, exist_ok=True)

        output_hls_path = os.path.join(output_dir, name_without_extension)

        temp_file_path = os.path.join(output_dir, 'temp_video.mp4')

        with open(temp_file_path, 'wb') as temp_file:
            for chunk in video.cmp_video.chunks():
                temp_file.write(chunk)

        logger.info(f'FILE PATH CELERY: {temp_file_path}')

        # media\hls_videos\1_TES5\360p_000.ts
        
        # FFmpeg command to create a playlist with multiple bitrates
        command = [
            'ffmpeg', '-y', '-i', temp_file_path,
            '-vf', 'scale=w=1280:h=720', '-c:v', 'libx264', '-b:v', '3000k', '-hls_time', '2', '-hls_playlist_type', 'vod',
            '-hls_segment_filename', os.path.join(output_dir, '720p_%03d.ts'), os.path.join(output_dir, '720p.m3u8'),
            '-vf', 'scale=w=854:h=480', '-c:v', 'libx264', '-b:v', '1500k', '-hls_time', '2', '-hls_playlist_type', 'vod',
            '-hls_segment_filename', os.path.join(output_dir, '480p_%03d.ts'), os.path.join(output_dir, '480p.m3u8'),
            '-vf', 'scale=w=640:h=360', '-c:v', 'libx264', '-b:v', '800k', '-hls_time', '2', '-hls_playlist_type', 'vod',
            '-hls_segment_filename', os.path.join(output_dir, '360p_%03d.ts'), os.path.join(output_dir, '360p.m3u8'),
            '-vf', 'scale=w=426:h=240', '-c:v', 'libx264', '-b:v', '550k', '-hls_time', '2', '-hls_playlist_type', 'vod',
            '-hls_segment_filename', os.path.join(output_dir, '240p_%03d.ts'), os.path.join(output_dir, '240p.m3u8')
        ]
        # Execute the FFmpeg command
        result = subprocess.run(command, check=True, stdout=subprocess.PIPE)

        outpit_json = json.loads(result.stdout)

        video_length = None

        for stream in outpit_json['streams']:
            if stream['codec_type'] == 'video':
                video_length = float(stream['duration'])
                logger.info(f'VIDEO LENGTH: {video_length}')

        # and result_thumbnail.returncode !=0
        if result.returncode != 0 :
            logger.error('FFmpeg command failed')
            return None

        video.hls_name = "SAVED"
        video.is_running = False
        video.save()

        data = {'temp_path': f'{temp_file_path}', '720p_Path': f'{os.path.join(output_dir, '720p.m3u8')}'}
        return data

        # os.remove(temp_file_path)

        # return output_dir
    except Exception as e:
        logger.error(f"Error during video processing: {e}")