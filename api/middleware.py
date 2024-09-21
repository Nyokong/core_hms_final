# api/middleware.py
from django.http import JsonResponse

from django.shortcuts import redirect
from django.utils.deprecation import MiddlewareMixin
from rest_framework_simplejwt.tokens import RefreshToken
import logging

from .signals import user_logged_in_receiver

logger = logging.getLogger('api')

def get_tokens_for_user(user):
    refresh = RefreshToken.for_user(user)
    return {
        'refresh': str(refresh),
        'access': str(refresh.access_token),
    }

class CustomRedirectMiddleware(MiddlewareMixin):
    def process_response(self, request, response):
        if request.user.is_authenticated:
            if user_logged_in_receiver(sender=None, request=request, user=request.user):
                if request.path == '/accounts/profile/' or request.path == '/accounts/email/':
                    user = request.user
                    if user.is_authenticated:
                        tokens = get_tokens_for_user(user)

                        response = JsonResponse({'access_token': 'Login successful'})

                        response.set_cookie(
                            key='access_token',
                            value=tokens['access'],
                            httponly=True,  # This makes the cookie HTTP-only
                            secure=True,    # Use this in production to ensure the cookie is only sent over HTTPS
                            samesite='Lax'  # Adjust this based on your needs (Lax, Strict, None)
                        )

                        logger.info(f'Redirecting user {user} in the middleware')
                        return redirect(f'http://localhost:3000/stdupdate')
        return response