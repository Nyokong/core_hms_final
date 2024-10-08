from django.views.generic import TemplateView
from rest_framework.viewsets import generics
from allauth.socialaccount.models import SocialToken
from django.http import JsonResponse

from django.contrib.auth import authenticate, login
from django.shortcuts import redirect

# logging
import logging
logger = logging.getLogger('api')

class IndexView(TemplateView):
    template_name = 'home.html'
    # context_object_name = 'items'

from allauth.socialaccount.providers.google.views import GoogleOAuth2Adapter
from allauth.socialaccount.providers.oauth2.client import OAuth2Client
from dj_rest_auth.registration.views import SocialLoginView

class GoogleLogin(SocialLoginView): # if you want to use Authorization Code Grant, use this
    adapter_class = GoogleOAuth2Adapter
    callback_url = 'http://localhost:3000/'
    client_class = OAuth2Client

    def post(self, request, *args, **kwargs):
        # Call the parent post method to handle the authentication
        response = super().post(request, *args, **kwargs)

        # Check if the user was authenticated successfully
        if response.status_code == 200:
            user = request.user
            # Create a session for the user
            login(request, user)
            # Optionally, set a cookie
            response.set_cookie('sessionid', request.session.session_key)

            logger.info(f'USER: {user} is logged in')

        return response

def custom_google_login(request):
    user = request.user
    if user.is_authenticated:
        logger.info(f"USER is logged {user}")
        try:
            token = SocialToken.objects.get(account__user=user, account__provider='google')
            response = JsonResponse({'message': 'Logged in successfully'})
            response.set_cookie('auth_token', token.token, httponly=True)

            login(request, user)
            return redirect('thank-you')
        except SocialToken.DoesNotExist:
            return JsonResponse({'error': 'Token not found'}, status=400)
    else:
        logger.info("Something went wrong")
    
    return redirect('http://localhost:8000/api/thank-you')