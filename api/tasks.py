from __future__ import absolute_import, unicode_literals
import os
from moviepy.editor import VideoFileClip
from django.conf import settings
from .models import Video
import logging

logger = logging.getLogger('api')

from celery import shared_task

@shared_task
def add(x, y):
    return x + y

# # Process the video for adaptive streaming
#             file_obj = request.data['cmp_video']
#             input_file_path = file_obj.temporary_file_path()

#             # Debugging: Check if the file exists
#             if not os.path.exists(input_file_path):
#                 return Response({"error": "Temporary file not found"}, status=status.HTTP_400_BAD_REQUEST)


#             # Start background task
#             # Create the subfolder inside 'hls_videos'
#             subfolder_path = os.path.join(settings.MEDIA_ROOT, 'hls_videos', str(video.id))

#             output_dir = os.path.join(settings.MEDIA_ROOT, 'hls_videos', str(video.id))

#             os.makedirs(output_dir, exist_ok=True)

#             # Set the temp directory for moviepy
#             temp_dir = os.path.join(subfolder_path, 'temp')
#             os.makedirs(temp_dir, exist_ok=True)
#             os.environ['TEMP'] = temp_dir
#             os.environ['TMPDIR'] = temp_dir

#             try:
#                 # Load the video file
#                 video = mp.VideoFileClip(input_file_path).resize(0.5)

#                 # Split the video into segments (e.g., 10 seconds each)
#                 segment_duration = 5
#                 segments = []

#                 print("now cutting into segments")
#                 for i in range(0, int(video.duration), segment_duration):
#                     # create the segments
#                     segment = video.subclip(i, min(i + segment_duration, video.duration))

#                     # Ensure audio is included and specify temp audio file location
#                     temp_audiofile = os.path.join(temp_dir, f'temp_audio_{i}.m4a')

#                     # create segment path
#                     segment_file = os.path.join(subfolder_path, str(f'segment_{i}.ts'))
                    
#                     segment.write_videofile(segment_file, codec='libx264',audio_codec='aac', temp_audiofile=temp_audiofile)

#                     segments.append(segment_file)

#                 # Create the M3U8 playlist
#                 playlist = m3u8.M3U8()
#                 for segment_file in segments:
#                     playlist.add_segment(m3u8.Segment(uri=segment_file, duration=segment_duration))

#                 # Save the playlist to a file in the subfolder
#                 playlist_file = os.path.join(subfolder_path, 'playlist.m3u8')
#                 with open(playlist_file, 'w') as f:
#                     f.write(playlist.dumps())

#                 # Clean up temporary files
#                 for temp_file in os.listdir(temp_dir):
#                     os.remove(os.path.join(temp_dir, temp_file))

# return Response({"message": "HLS playlist created successfully!", "playlist": playlist_file}, status=status.HTTP_200_OK)
#  except Exception as e:
#                 print(f"Error during HLS creation: {e}")
#                 return Response({"error": "HLS creation failed"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
