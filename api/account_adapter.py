from allauth.account.adapter import DefaultAccountAdapter
import logging

logger = logging.getLogger('api')

class MyAccountAdapter(DefaultAccountAdapter):

    def get_login_redirect_url(self, request):
        # get user instance
        user = request.user

        # logger.info(f'Redirecting user {user} with token {tokens["access"]} from redirect')
        logger.info(f'Logging {user} From Google but needs Student Number')

        # go to the front end to add employee number
        return f'http://localhost:8000'
    