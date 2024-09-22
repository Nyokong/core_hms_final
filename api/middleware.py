# api/middleware.py

from django.shortcuts import redirect
from django.utils.deprecation import MiddlewareMixin
from rest_framework_simplejwt.tokens import RefreshToken
import logging

from .signals import user_logged_in_receiver

logger = logging.getLogger('api')

# def get_tokens_for_user(user):
#     refresh = RefreshToken.for_user(user)
#     return {
#         'refresh': str(refresh),
#         'access': str(refresh.access_token),
#     }

class CustomRedirectMiddleware(MiddlewareMixin):
    def process_response(self, request, response):
        if request.user.is_authenticated:
            if user_logged_in_receiver(sender=None, request=request, user=request.user):
                if request.path == '/accounts/profile/' or request.path == '/accounts/email/':
                    user = request.user
                    if user.is_authenticated:
                        # Create access token
                        refresh = RefreshToken.for_user(request.user)
                        access_token = str(refresh.access_token)

                        logger.info('remove unvalid session')
                        response.delete_cookie('sessionid')
                        response.delete_cookie('csrf')

                        # Set the access token in a cookie
                        response.set_cookie(
                            key='access_token',
                            value=access_token,
                            httponly=True,
                            secure=True,  # Use this in production
                            samesite='None'  # Adjust based on your needs
                        )
                        logger.info(f'Redirecting user {user} in the middleware')
                        return redirect("http://localhost:3000/stdupdate")
        return response

class DeleteMessagesCookieMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        cookie_value = request.COOKIES.get('sessionid')

        if cookie_value == "undefined":
            print("deleting this cookie")
        response = self.get_response(request)
        response.delete_cookie('messages')
        
        return response