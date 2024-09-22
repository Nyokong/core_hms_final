from allauth.socialaccount.adapter import DefaultSocialAccountAdapter
from django.shortcuts import redirect
import logging

logger = logging.getLogger('api')

class MySocialAccountAdapter(DefaultSocialAccountAdapter):
    def complete_login(self, request, sociallogin, **kwargs):
        user = sociallogin.user
        logger.info(f'Redirecting user {user} from the adapter')
        return redirect(f'http://localhost:8000')
        