from allauth.socialaccount.providers.google.views import GoogleOAuth2Adapter
from allauth.socialaccount.providers.oauth2.client import OAuth2Error
import jwt

class CustomGoogleOAuth2Adapter(GoogleOAuth2Adapter):
    def _decode_id_token(self, app, id_token, verify_signature=True):
        try:
            return jwt.decode(
                id_token,
                key=app.secret,
                algorithms=['RS256'],
                audience=app.client_id,
                leeway=30  # Increase leeway to 30 seconds
            )
        except jwt.ImmatureSignatureError as e:
            raise OAuth2Error("Invalid id_token") from e
