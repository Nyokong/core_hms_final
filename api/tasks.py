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
def encode_ffmpeg(video_id):
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

        logger.info(f'FILE PATH: {temp_file_path}')

        # command = [
        #     'ffmpeg', '-y', '-i', temp_file_path,
        #     '-vf', 'scale=w=1280:h=720', '-c:v', 'libx264', '-b:v', '3000k', '-hls_time', '10', '-hls_playlist_type', 'vod',
        #     '-hls_segment_filename', os.path.join(output_dir, '720p_%03d.ts'), os.path.join(output_dir, '720p.m3u8'),
        #     '-vf', 'scale=w=854:h=480', '-c:v', 'libx264', '-b:v', '1500k', '-hls_time', '10', '-hls_playlist_type', 'vod',
        #     '-hls_segment_filename', os.path.join(output_dir, '480p_%03d.ts'), os.path.join(output_dir, '480p.m3u8'),
        #     '-vf', 'scale=w=640:h=360', '-c:v', 'libx264', '-b:v', '800k', '-hls_time', '10', '-hls_playlist_type', 'vod',
        #     '-hls_segment_filename', os.path.join(output_dir, '360p_%03d.ts'), os.path.join(output_dir, '360p.m3u8')
        # ]

        dynamic_path = "http://localhost:8000/media/hls_videos"

        command = [
            'ffmpeg', '-i', 
            temp_file_path,
            '-c:v', 'h264', 
            '-c:a', 'aac',
            '-hls_time', '5', 
            '-hls_list_size', '0', 
            '-hls_base_url', 
            dynamic_path + '/',
            '-movflags', 
            '+faststart','-y' , output_dir
        ]

        thumbnail_output_dir = os.path.join(settings.MEDIA_ROOT, 'thumbnail',f'{name_without_extension}')
        os.makedirs(thumbnail_output_dir, exist_ok=True)

        result = subprocess.run(command, capture_output=True, text=True)

        cmd_thumbnail = [
            'ffmpeg', '-y', '-i', temp_file_path,
            '-ss', '2', '-vframes', '1', '-q:v', '2', thumbnail_output_dir,
        ]

        result = subprocess.run(command, check=True)
        result_thumbnail = subprocess.run(cmd_thumbnail, check=True)

        outpit_json = json.loads(result.stdout)

        video_length = None

        for stream in outpit_json['streams']:
            if stream['codec_type'] == 'video':
                video_length = float(stream['duration'])
                break

        logger.info(f'FFmpeg stdout: {result.stdout}')
        logger.error(f'FFmpeg stderr: {result.stderr}')

        if result.returncode != 0 and result_thumbnail.returncode !=0:
            logger.error('FFmpeg command failed')
            return None
        else:
            video.hls_path = os.path.join(dynamic_path, name_without_extension)
            video.video_length = video_length
            video.thumbnail = thumbnail_output_dir
            video.status = 'completed'
            video.is_running = False
            video.save()

        os.remove(temp_file_path)

        return output_dir
    except Exception as e:
        logger.error(f"Error during video processing: {e}")
    #     return None
    #     from api.models import Video

    #     video = Video.objects.get(id=video_id)

    #     if video.status == 'pending':
    #         # Log the video ID being processed
    #         logger.info(f"Processing video with ID: {video.id}")
    #         video.is_running = True
    #         video.save()
    #         # 1_TES1

    #         input_video_path = video.cmp_video.path

    #         logger.info(input_video_path)

    #         output_dir = os.path.join(os.path.dirname(input_video_path), 'hls_videos')
    #         temp_file_path = os.path.join(output_dir, 'temp_video.mp4')
            
    #         os.makedirs(output_dir, exist_ok=True)

    #         # TES
    #         title_code = video.title[:3].upper()
    #         # 1_TESID
    #         fullName = f'{video.user.id}_{title_code}{video.id}'
    #         # full_name = video.cmp_video.name

    #         # filename = full_name.split('/')[-1]

    #         # Extract the numeric part after the title code

    #         # fullvid = f'{video.user.id}_{title_code}{numeric_part}'
    #         # name_without_extension = input_video_path.rsplit('.', 1)[0]

    #         # output_filename = os.path.splitext(os.path.basename(input_video_path))[0]+ '_hls.m3u8'
    #         # # output_dir = os.path.join(settings.MEDIA_URL, 'hls_videos', name_without_extension)
    #         # # out_hls_folder = os.path.join(output_dir, fullName)
    #         # output_hls_path = os.path.join(output_dir, output_filename)

    #         output_thumbnail_path = os.path.join(output_dir, os.path.splitext(os.path.basename(input_video_path))[0]+'_thumbnail.jpg')

    #         dynamic_path = "http://localhost:8000/media/hls_videos"

    #         # command = [
    #         #     'ffmpeg', '-i', 
    #         #     input_video_path,
    #         #     '-c:v', 'h264', 
    #         #     '-c:a', 'aac',
    #         #     '-hls_time', '5', 
    #         #     '-hls_list_size', '0', 
    #         #     '-hls_base_url', 
    #         #     {{ dynamic_path }}'/',
    #         #     '-movflags', 
    #         #     '+faststart','-y' ,output_hls_path,
    #         # ]

    #         command = [
    #             'ffmpeg', '-y', '-i', temp_file_path,
    #             '-vf', 'scale=w=1280:h=720', '-c:v', 'libx264', '-b:v', '3000k', '-hls_time', '10', '-hls_playlist_type', 'vod',
    #             '-hls_segment_filename', os.path.join(output_dir, '720p_%03d.ts'), os.path.join(output_dir, '720p.m3u8'),
    #             '-vf', 'scale=w=854:h=480', '-c:v', 'libx264', '-b:v', '1500k', '-hls_time', '10', '-hls_playlist_type', 'vod',
    #             '-hls_segment_filename', os.path.join(output_dir, '480p_%03d.ts'), os.path.join(output_dir, '480p.m3u8'),
    #             '-vf', 'scale=w=640:h=360', '-c:v', 'libx264', '-b:v', '800k', '-hls_time', '10', '-hls_playlist_type', 'vod',
    #             '-hls_segment_filename', os.path.join(output_dir, '360p_%03d.ts'), os.path.join(output_dir, '360p.m3u8')
    #         ]

    #         cmd_thumbnail = [
    #             'ffmpeg', '-y', '-i', input_video_path,
    #             '-ss', '2', '-vframes', '1', '-q:v', '2', output_thumbnail_path,
    #         ]

    #             # '-vf', 'scale=w=854:h=480', '-c:v', 'libx264', '-b:v', '1500k', '-hls_time', '10', '-hls_playlist_type', 'vod',
    #             # '-hls_segment_filename', os.path.join(output_dir, '480p_%03d.ts'), os.path.join(output_dir, '480p.m3u8'),
    #             # '-vf', 'scale=w=640:h=360', '-c:v', 'libx264', '-b:v', '800k', '-hls_time', '10', '-hls_playlist_type', 'vod',
    #             # '-hls_segment_filename', os.path.join(output_dir, '360p_%03d.ts'), os.path.join(output_dir, '360p.m3u8')

    #         result = subprocess.run(command, check=True)
    #         result_thumbnail = subprocess.run(cmd_thumbnail, check=True)

    #         outpit_json = json.loads(result.stdout)

    #         video_length = None

    #         for stream in outpit_json['streams']:
    #             if stream['codec_type'] == 'video':
    #                 video_length = float(stream['duration'])
    #                 break

    #         logger.info(f'FFmpeg stdout: {result.stdout}')
    #         logger.error(f'FFmpeg stderr: {result.stderr}')

    #         if result.returncode != 0 and result_thumbnail.returncode !=0:
    #             logger.error('FFmpeg command failed')
    #             return None
    #         else:
    #             video.hls_path = output_hls_path
    #             video.video_length = video_length
    #             video.thumbnail = output_thumbnail_path
    #             video.status = 'completed'
    #             video.is_running = False
    #             video.save()

                
            
    #         # command = [
    #         #     'ffmpeg', '-y', '-i', input_video_path,
    #         #     '-vf', 'scale=w=1280:h=720', '-c:v', 'libx264', '-b:v', '3000k', '-hls_time', '10', '-hls_playlist_type', 'vod',
    #         #     '-hls_segment_filename', os.path.join(output_dir, '720p_%03d.ts'), os.path.join(output_dir, '720p.m3u8'),
    #         #     '-vf', 'scale=w=854:h=480', '-c:v', 'libx264', '-b:v', '1500k', '-hls_time', '10', '-hls_playlist_type', 'vod',
    #         #     '-hls_segment_filename', os.path.join(output_dir, '480p_%03d.ts'), os.path.join(output_dir, '480p.m3u8'),
    #         #     '-vf', 'scale=w=640:h=360', '-c:v', 'libx264', '-b:v', '800k', '-hls_time', '10', '-hls_playlist_type', 'vod',
    #         #     '-hls_segment_filename', os.path.join(output_dir, '360p_%03d.ts'), os.path.join(output_dir, '360p.m3u8')
    #         # ]
    #     # try:
    #     #     video = Video.objects.get(id=video_id)
    #     #     logger.info(f"Found video: {video}")
    #     # except Video.DoesNotExist:
    #     #     logger.error(f"Video with ID {video_id} does not exist.")
    #     #     return None

    #     # title_code = video.title[:3].upper()
    #     # full_name = video.cmp_video.name
    #     # filename = full_name.split('/')[-1]

    #     # # Extract the numeric part after the title code
    #     # pos = filename.find(title_code)
    #     # if pos != -1:
    #     #     numeric_part = filename[pos + len(title_code):]
    #     # else:
    #     #     numeric_part = ""

    #     # fullvid = f'{video.user.id}_{title_code}{numeric_part}'
    #     # name_without_extension = fullvid.rsplit('.', 1)[0]

    #     # output_dir = os.path.join(settings.MEDIA_ROOT, 'hls_videos', name_without_extension)
    #     # os.makedirs(output_dir, exist_ok=True)

    #     # temp_file_path = os.path.join(output_dir, 'temp_video.mp4')

    #     # with open(temp_file_path, 'wb') as temp_file:
    #     #     for chunk in video.cmp_video.chunks():
    #     #         temp_file.write(chunk)

    #     # logger.info(f'FILE PATH: {temp_file_path}')

        

        
        
    #     # if result.returncode == 0:
    #     #     # Assuming the output_dir is within MEDIA_ROOT
    #     #     relative_path = os.path.relpath(os.path.join(output_dir, '360p.m3u8'), settings.MEDIA_ROOT)
    #     #     video = Video.objects.get(id=video_id)

    #     #     # Retrieve the Video instance by ID
    #     #     # Update the vid360p field
    #     #     video.vid360p = relative_path
    #     #     video.save(update_fields=['vid360p'])

    #     #     return video
    #     # else:
    #     #     print(f"Error: {result.stderr}")
    #     #     return None

    #     # # os.remove(temp_file_path)

    #     # # # http://localhost:8000/media/hls_videos/{video.user.id}_{title_code}{video.id}

    #     # # video.hls_path = f"http://localhost:8000/media/hls_videos/{video.user.id}_{title_code}{video.id}"
    #     # # video.save()

    #     return output_dir
    # except Exception as e:
    #     logger.error(f"Error during video processing: {e}")
    #     return None