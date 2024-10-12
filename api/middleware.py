# api/middleware.py

from django.http import HttpResponseRedirect, HttpResponse
from django.shortcuts import redirect
from django.utils.deprecation import MiddlewareMixin
from rest_framework_simplejwt.tokens import RefreshToken
import logging

from .signals import user_logged_in_receiver

logger = logging.getLogger('api')


class CustomRedirectMiddleware(MiddlewareMixin):

    def process_response(self, request, response):
        # Intercept the request path
        #or request.path == '/accounts/email/'
        if request.path == '/accounts/profile/':
            logger.info(f'this RESPONSE:{request.path}')
            response.content = b''
            # logger.info(f'this fucker:{response}')
            # refresh = RefreshToken.for_user(request.user)
            # access_token = str(refresh.access_token)
            if isinstance(response, HttpResponse):
                response.delete_cookie('messages')

            # if request.user.is_authenticated:
            #     if response.content == b'':
            #         logger.info("successfully deleted response now creating cookie")
            # Set the access token in a cookie
            # response.set_cookie(
            #     key='access_token',
            #     value=access_token,
            #     httponly=True,
            #     secure=True,  # Use this in production
            #     samesite='None'  # Adjust based on your needs
            # )
            # response.delete_cookie('messages')
            return redirect('http://localhost:8000/api/thank-you')
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