# from allauth.socialaccount.adapter import DefaultSocialAccountAdapter, DefaultAccountAdapter
from allauth.account.adapter import DefaultAccountAdapter
# from django.shortcuts import redirect
from rest_framework_simplejwt.tokens import RefreshToken
import logging

logger = logging.getLogger('api')

# def get_tokens_for_user(user):
#     refresh = RefreshToken.for_user(user)
#     return {
#         'refresh': str(refresh),
#         'access': str(refresh.access_token),
#     }

print("Loading MySocialAccountAdapter")  
class MySocialAccountAdapter(DefaultAccountAdapter):

    def get_login_redirect_url(self, request):
        # get user instance
        user = request.user

        # logger.info(f'Redirecting user {user} with token {tokens["access"]} from redirect')
        logger.info(f'Logging {user} From Google but needs Student Number')

        # go to the front end to add employee number
        return f'http://localhost:3000'
    
    # def complete_login(self, request, sociallogin, **kwargs):
    #     user = sociallogin.user
    #     tokens = get_tokens_for_user(user)
    #     logger.info(f'Redirecting user {user} with token {tokens["access"]} from the adapter')
    #     return redirect(f'http://localhost:3000/login?token={tokens["access"]}')
        