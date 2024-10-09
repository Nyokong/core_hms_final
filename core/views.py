from django.views.generic import TemplateView
from rest_framework.viewsets import generics
from allauth.socialaccount.models import SocialToken
from django.http import JsonResponse
from django.core.exceptions import ObjectDoesNotExist

from allauth.socialaccount.models import SocialAccount
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.response import Response
from allauth.account.models import EmailAddress

from rest_framework import status
import requests

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
from . import adapters

class GoogleLogin(SocialLoginView): # if you want to use Authorization Code Grant, use this
    adapter_class = adapters.CustomGoogleOAuth2Adapter
    callback_url = 'http://localhost:3000/success/'
    client_class = OAuth2Client

    def post(self, request, *args, **kwargs):
        access_token = request.data.get('access_token')
        id_token = request.data.get('id_token')

        if not access_token or not id_token:
            return Response({"error": "Missing tokens"}, status=status.HTTP_400_BAD_REQUEST)

        # Manually handle the tokens and authenticate the user
        try:
            # Use the tokens to authenticate the user
            user = self.authenticate_user(access_token, id_token)
            logger.info(f'USER DATA AUTH: {user}')

            # Generate JWT tokens
            refresh = RefreshToken.for_user(user)
            return Response({
                'access_token': str(refresh.access_token),
                'refresh_token': str(refresh),
            }, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)

    def authenticate_user(self, access_token, id_token):
        # Implement your custom authentication logic here
        # For example, you can use the tokens to get user info from Google
        # and create or get the user in your database
        user_info = self.get_user_info_from_google(access_token, id_token)
        logger.info(f'USER DATA: {user_info}')

        user = self.get_or_create_user(user_info)

        logger.info(f'USER GETORCREATE: {user}')

        return user
    
    def get_user_info_from_google(self, access_token, id_token):
        # Verify the ID token
        id_info = self.verify_id_token(id_token)

        logger.info(f'IDTOKEN {id_info}')
        
        # Fetch user info using the access token
        user_info = self.fetch_user_info(access_token)

        verified = 'True'

        if id_info.get("verified_email") == 'True':
            logger.info('THIS IS TRUE')
            verified = 'True'
        
        return {
            "email": user_info.get("email"),
            "name": user_info.get("name"),
            "given_name": user_info.get("given_name"),
            "family_name": user_info.get("family_name"),
            "picture": user_info.get("picture"),
            "locale": user_info.get("locale"),
            "hd": user_info.get("hd"),
            "email_verified": verified,  
            "sub": id_info.get("sub"),
            "profile": user_info.get("profile"),
            "gender": user_info.get("gender"),
            "birthdate": user_info.get("birthdate"),
            "phone_number": user_info.get("phone_number"),
            "address": user_info.get("address")
        }

    def verify_id_token(self, id_token):
        # Verify the ID token using Google's OAuth2 API
        response = requests.get(f'https://oauth2.googleapis.com/tokeninfo?id_token={id_token}')
        response.raise_for_status()
        return response.json()

    def fetch_user_info(self, access_token):
        # Fetch user info using the access token
        headers = {'Authorization': f'Bearer {access_token}'}
        response = requests.get('https://www.googleapis.com/oauth2/v1/userinfo', headers=headers)
        response.raise_for_status()
        return response.json()
    
    def get_or_create_user(self, user_info):
        from api.models import custUser
        # defaults={"username": user_info["name"]}
        # username = 'Callmekay Music (callmekaymusic)'
        # truncated_username = username[:8]

        if user_info["family_name"] != None:
            username = user_info["family_name"]
            last_name = user_info["family_name"]
        else:
            username = user_info["given_name"]
            last_name = user_info["given_name"]
            
        truncated_username = username[:8].lower() 

        # user, created = custUser.objects.get_or_create(username=truncated_username,email=user_info["email"], first_name=user_info["given_name"],last_name=last_name )

        try:
            user = custUser.objects.get(email=user_info["email"])
        except ObjectDoesNotExist:
            user = custUser.objects.create(
                email=user_info["email"],
                username=truncated_username,
                is_active=True,
            )

        # Ensure the social account is linked
        try:
            SocialAccount.objects.get(user=user, provider='google')
        except ObjectDoesNotExist:
            SocialAccount.objects.create(
                user=user,
                provider='google',
                uid=user_info["sub"],
                extra_data=user_info
            )

        try:
            email_address = EmailAddress.objects.get(user=user, email=user_info["email"])
        except ObjectDoesNotExist:
            email_address = EmailAddress.objects.create(
                user=user,
                email=user_info["email"],
                verified=user_info.get("email_verified",False), 
                primary=True
            )
            
        # return user regardless 
        return user


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