from allauth.socialaccount.adapter import DefaultSocialAccountAdapter
from rest_framework_simplejwt.tokens import RefreshToken
from django.shortcuts import redirect
import logging

logger = logging.getLogger('api')

class MySocialAccountAdapter(DefaultSocialAccountAdapter):
    def complete_login(self, request, sociallogin, **kwargs):
        user = sociallogin.user
        # user = request.user

        # Generate the access and refresh tokens
        refresh = RefreshToken.for_user(user)
        access_token = str(refresh.access_token)
        refresh_token = str(refresh)

        # # Create the response object
        response = 'http://localhost:8000/api/thank-you'

        # # Set the access and refresh tokens as cookies
        response.set_cookie('access_token', access_token, httponly=True, secure=True)
        response.set_cookie('refresh_token', refresh_token, httponly=True, secure=True)

        # logger.info(f'Redirecting user {user} with token {tokens["access"]} from redirect')
        logger.info(f'Logging {user} From Google but needs Student Number')

        # go to the front end to add employee number
        return response
        