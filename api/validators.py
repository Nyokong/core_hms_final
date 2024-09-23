import logging

from rest_framework import serializers

logger = logging.getLogger('api')

def validate_file_size(file):
    max_size = 20 * 1024 * 1024 # 100 MB
    
    if file.size > max_size:
        logger.info("video is too big")
        raise serializers.ValidationError(f'File size too big - should not exceed {max_size/(1024 * 1024)} MB.')