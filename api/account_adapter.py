from allauth.account.adapter import DefaultAccountAdapter
from rest_framework_simplejwt.tokens import RefreshToken
from django.http import HttpResponseRedirect
from django.shortcuts import redirect
from django.contrib.auth import login

import logging

logger = logging.getLogger('api')

from .models import custUser

class MyAccountAdapter(DefaultAccountAdapter):

    def get_login_redirect_url(self, request):
        # get user instance
        user = request.user

        custom_user = custUser.objects.get(username=user)

        login(request=request, user=custom_user)

        logger.info(f'SESSION USER: {request.COOKIES.get('sessionid')}')

        # logger.info(f'Redirecting user {user} with token {tokens["access"]} from redirect')
        logger.info(f'Logging {user} From Google Account_Adapter')

        # go to the front end to add employee number
        # return 'http://localhost:8000/api/thank-you'
        return "http://localhost:3000"

    