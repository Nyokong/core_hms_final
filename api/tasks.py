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
    


# @shared_task
# def create_m3u8_playlist(video_id):

#     try:
#         video_instance = Video.objects.get(id=video_id)
#         logger.info(f'ID: {video_instance.id} - {video_instance.title}')

#         file_obj = video_instance.cmp_video

#         # Create a temporary file
#         with tempfile.NamedTemporaryFile(delete=False) as temp_file:
#             # Write the content of the uploaded file to the temporary file
#             for chunk in file_obj.chunks():
#                 temp_file.write(chunk)

#             # Declare temp_file
#             temp_file_path = temp_file.name

#         # Process the video for adaptive streaming
#         input_file_path = str(temp_file_path)
#         logger.info(f'FILE PATH: {input_file_path}')

#         # Debugging: Check if the file exists
#         if not os.path.exists(input_file_path):
#             logger.error(f'Temporary file path not found: {input_file_path}')
#             return None
        
#         # Start background task
#         subfolder_path = os.path.join(settings.MEDIA_ROOT, 'hls_videos', str(video_id))
#         output_dir = os.path.join(settings.MEDIA_ROOT, 'hls_videos', str(video_id))
#         os.makedirs(output_dir, exist_ok=True)

#         temp_dir = os.path.join(subfolder_path, 'temp')
#         os.makedirs(temp_dir, exist_ok=True)
#         os.environ['TEMP'] = temp_dir
#         os.environ['TMPDIR'] = temp_dir

#         try:
#             with tempfile.TemporaryDirectory() as temp_dir:
#                 video = mp.VideoFileClip(input_file_path).resize(0.5)
#                 logger.info('Resize done')

#                 segment_duration = 5
#                 segments = []

#                 logger.info("Now cutting into segments")
#                 for i in range(0, int(video.duration), segment_duration):
#                     segment = video.subclip(i, min(i + segment_duration, video.duration))

#                     temp_audiofile = os.path.join(temp_dir, f'temp_audio_{i}.m4a')
#                     segment_file = os.path.join(subfolder_path, f'segment_{i}.ts')
                    
#                     segment.write_videofile(segment_file, codec='libx264', audio_codec='aac', temp_audiofile=temp_audiofile)
#                     segments.append(segment_file)

#                 # Commenting out the HLS playlist creation part
#                 # playlist = m3u8.M3U8()
#                 # for segment_file in segments:
#                 #     playlist.add_segment(m3u8.Segment(uri=segment_file, duration=segment_duration))

#                 # playlist_file = os.path.join(subfolder_path, 'playlist.m3u8')
#                 # with open(playlist_file, 'w') as f:
#                 #     f.write(playlist.dumps())

#                 for temp_file in os.listdir(temp_dir):
#                     os.remove(os.path.join(temp_dir, temp_file))

#                 logger.info('Background task was successful')
#                 return segments  # Returning segments for debugging
#         except Exception as e:
#             logger.error(f"Error during video processing: {e}")
#             return None
#     except Exception as e:
#         logger.error(f"Error during video processing: {e}")
#         return None
#         # return f'The file path: {file_obj}'

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

        # command = [
        #     'ffmpeg', '-y', '-i', temp_file_path,
        #     '-vf', 'scale=w=1280:h=720', '-c:v', 'libx264', '-b:v', '3000k', '-hls_time', '10', '-hls_playlist_type', 'vod',
        #     '-hls_segment_filename', os.path.join(output_dir, '720p_%03d.ts'), os.path.join(output_dir, '720p.m3u8'),
        #     '-vf', 'scale=w=854:h=480', '-c:v', 'libx264', '-b:v', '1500k', '-hls_time', '10', '-hls_playlist_type', 'vod',
        #     '-hls_segment_filename', os.path.join(output_dir, '480p_%03d.ts'), os.path.join(output_dir, '480p.m3u8'),
        #     '-vf', 'scale=w=640:h=360', '-c:v', 'libx264', '-b:v', '800k', '-hls_time', '10', '-hls_playlist_type', 'vod',
        #     '-hls_segment_filename', os.path.join(output_dir, '360p_%03d.ts'), os.path.join(output_dir, '360p.m3u8')
        # ]

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
        
        return output_dir
    except Exception as e:
        logger.error(f"Error during video processing: {e}")
        return None

    # def create_m3u8_playlist(video_vid, video_id, video_file_path):
    # Process the video for adaptive streaming
    # file_obj = video_vid
    # input_file_path = str(file_obj.temporary_file_path())

    # # Debugging: Check if the file exists
    # if not os.path.exists(input_file_path):
    #     logger.info(f'temporary file path not found {input_file_path}')

    # logger.info(f'video: {video_id} path: {video_file_path}')

    # # Start background task
    # # Create the subfolder inside 'hls_videos'
    # subfolder_path = os.path.join(settings.MEDIA_ROOT, 'hls_videos', str(video_id))

    # output_dir = os.path.join(settings.MEDIA_ROOT, 'hls_videos', str(video_id))

    # os.makedirs(output_dir, exist_ok=True)

    # # Set the temp directory for moviepy
    # temp_dir = os.path.join(subfolder_path, 'temp')
    # os.makedirs(temp_dir, exist_ok=True)
    # os.environ['TEMP'] = temp_dir
    # os.environ['TMPDIR'] = temp_dir

    # try:
    #     # Load the video file
    #     video = mp.VideoFileClip(input_file_path).resize(0.5)

    #     # Split the video into segments (e.g., 10 seconds each)
    #     segment_duration = 5
    #     segments = []

    #     logger.info("now cutting into segments")
    #     for i in range(0, int(video.duration), segment_duration):
    #         # create the segments
    #         segment = video.subclip(i, min(i + segment_duration, video.duration))

    #         # Ensure audio is included and specify temp audio file location
    #         temp_audiofile = os.path.join(temp_dir, f'temp_audio_{i}.m4a')

    #         # create segment path
    #         segment_file = os.path.join(subfolder_path, str(f'segment_{i}.ts'))
            
    #         segment.write_videofile(segment_file, codec='libx264',audio_codec='aac', temp_audiofile=temp_audiofile)

    #         segments.append(segment_file)

    #     # Create the M3U8 playlist
    #     playlist = m3u8.M3U8()
    #     for segment_file in segments:
    #         playlist.add_segment(m3u8.Segment(uri=segment_file, duration=segment_duration))

    #     # Save the playlist to a file in the subfolder
    #     playlist_file = os.path.join(subfolder_path, 'playlist.m3u8')
    #     with open(playlist_file, 'w') as f:
    #         f.write(playlist.dumps())

    #     # Clean up temporary files
    #     for temp_file in os.listdir(temp_dir):
    #         os.remove(os.path.join(temp_dir, temp_file))

    #     logger.info(f'background task was successfull')
    # except Exception as e:
    #     logger.info(f"Error during HLS creation: {e}")
