from __future__ import absolute_import, unicode_literals
import os
import moviepy.editor as mp
import m3u8

from django.conf import settings
from .models import Video
import logging
import tempfile

logger = logging.getLogger('api')

from celery import shared_task

logger.info("Tasks module loaded")

@shared_task
def add(x, y):
    return x + y


@shared_task
def create_m3u8_playlist(video_id):

    try:
        video_instance = Video.objects.get(id=video_id)
        logger.info(f'ID: {video_instance.id} - {video_instance.title}')

        file_obj = video_instance.cmp_video

        # Create a temporary file
        with tempfile.NamedTemporaryFile(delete=False) as temp_file:
            # Write the content of the uploaded file to the temporary file
            for chunk in file_obj.chunks():
                temp_file.write(chunk)

            # declare temp_file
            temp_file_path = temp_file.name

        # Process the video for adaptive streaming
        input_file_path = str(temp_file_path)

        logger.info(f'FILE PATH: {input_file_path}')

        #Debugging: Check if the file exists
        if not os.path.exists(input_file_path):
            return logger.info(f'temporary file path not found {input_file_path}')
        
        # Start background task
        # Create the subfolder inside 'hls_videos'
        subfolder_path = os.path.join(settings.MEDIA_ROOT, 'hls_videos', str(video_id))

        output_dir = os.path.join(settings.MEDIA_ROOT, 'hls_videos', str(video_id))

        os.makedirs(output_dir, exist_ok=True)

        # Set the temp directory for moviepy
        temp_dir = os.path.join(subfolder_path, 'temp')
        os.makedirs(temp_dir, exist_ok=True)
        os.environ['TEMP'] = temp_dir
        os.environ['TMPDIR'] = temp_dir

        try:
            # Create a temporary directory
            with tempfile.TemporaryDirectory() as temp_dir:
                # Load the video file
                video = mp.VideoFileClip(file_obj).resize(0.5)
                logger.info('Resize done')

                # Split the video into segments (e.g., 5 seconds each)
                segment_duration = 5
                segments = []

                logger.info("now cutting into segments")
                for i in range(0, int(video.duration), segment_duration):
                    # create the segments
                    segment = video.subclip(i, min(i + segment_duration, video.duration))

                    # Ensure audio is included and specify temp audio file location
                    temp_audiofile = os.path.join(temp_dir, f'temp_audio_{i}.m4a')

                    # create segment path
                    segment_file = os.path.join(subfolder_path, str(f'segment_{i}.ts'))
                    
                    segment.write_videofile(segment_file, codec='libx264',audio_codec='aac', temp_audiofile=temp_audiofile)

                    segments.append(segment_file)

                # Create the M3U8 playlist
                playlist = m3u8.M3U8()
                for segment_file in segments:
                    playlist.add_segment(m3u8.Segment(uri=segment_file, duration=segment_duration))

                # Save the playlist to a file in the subfolder
                playlist_file = os.path.join(subfolder_path, 'playlist.m3u8')
                with open(playlist_file, 'w') as f:
                    f.write(playlist.dumps())

                # Clean up temporary files
                for temp_file in os.listdir(temp_dir):
                    os.remove(os.path.join(temp_dir, temp_file))

                logger.info(f'background task was successfull')
                return playlist_file
        except Exception as e:
            logger.info(f"Error during HLS creation: {e}")
            return None

    except Video.DoesNotExist:
        return logger.error(f"Video with id {video_id} does not exist")
        # return f'The file path: {file_obj}'

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
