import logging
from rest_framework.response import Response
from django.utils import timezone

logger = logging.getLogger('django.request')
logger.setLevel(logging.INFO)

class RequestLoggingMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        timestamp = timezone.now()
        
        logger.info(f"Request: {request.method} {request.get_full_path()}")
        response = self.get_response(request)
        logger.info(f"Requested at:{timestamp} \nResponse: {response.status_code} {response.reason_phrase}")
        return response
        

# class CheckPasswordMiddleware:
#     def __init__(self, get_response):
#         self.get_response = get_response

#     def __call__(self, request):
#         if request.user.is_authenticated and request.user.needs_password:
#             print(request)
#             print(request.error_google)
#         return self.get_response(request)