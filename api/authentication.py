from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework_simplejwt.exceptions import TokenError, InvalidToken
from rest_framework.response import Response
from rest_framework import status

class CustomJWTAuthentication(JWTAuthentication):
    def authenticate(self, request):
        try:
            return super().authenticate(request)
        except TokenError as e:
            return None

    def handle_exception(self, exc):
        if isinstance(exc, (TokenError, InvalidToken)):
            return Response({"message": "Token is invalid or expired."}, status=status.HTTP_401_UNAUTHORIZED)
        return super().handle_exception(exc)
