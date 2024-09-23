# api/middleware.py

from django.http import HttpResponseRedirect
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
    # def dispatch(self, request, *args, **kwargs):
    #     # Check if the current request path matches the path to clear
    #     if request.path == '/accounts/profile/' or request.path == '/accounts/email/':
    #         # Get the response (this will execute the normal flow)
    #         response = super().dispatch(request, *args, **kwargs)

    #         # log response
    #         logger.info("this is the logged response\n",response)

    #         # Clear the response content
    #         response.content = b''

    #         # Now you can redirect (after clearing the response)
    #         return HttpResponseRedirect('http://localhost:8000')  # Your redirect path

    def process_response(self, request, response):
        # Intercept the request path
        # logger.info(f"Requested path: {request.path}")

        if request.path == '/accounts/profile/':
            response.path = 'http://localhost:3000/stdupdate'
            response.content = b''

        # if request.user.is_authenticated:
        #     if user_logged_in_receiver(sender=None, request=request, user=request.user):
        #         if request.path == '/accounts/profile/' or request.path == '/accounts/email/':

        #             user = request.user

        #             if user.is_authenticated:
        #                 # Create access token
        #                 refresh = RefreshToken.for_user(request.user)
        #                 access_token = str(refresh.access_token)

        #                 logger.info('remove unvalid session')
        #                 # Clear the response content
        #                 response.content = b''

        #                 # Set the access token in a cookie
        #                 response.set_cookie(
        #                     key='access_token',
        #                     value=access_token,
        #                     httponly=True,
        #                     secure=True,  # Use this in production
        #                     samesite='None'  # Adjust based on your needs
        #                 )
        #                 logger.info(f'Redirecting user {user} in the middleware')
        #                 return redirect("http://localhost:3000/stdupdate")

        # return http response with the access token

        if request.path == '/accounts/profile/':
            logger.info(f'this fucker:{request.path}')
            response.content = b''
            logger.info(f'this fucker:{response}')
            refresh = RefreshToken.for_user(request.user)
            access_token = str(refresh.access_token)

            if request.user.is_authenticated:
                if response.content == b'':
                    logger.info("successfully deleted response now creating cookie")
            # Set the access token in a cookie
            response.set_cookie(
                key='access_token',
                value=access_token,
                httponly=True,
                secure=True,  # Use this in production
                samesite='None'  # Adjust based on your needs
            )
            # redirect("http://localhost:3000/stdupdate")
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