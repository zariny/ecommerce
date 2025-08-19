from rest_framework_simplejwt.tokens import AccessToken
from rest_framework_simplejwt.exceptions import TokenError


class JWTTokenCookieDetection():
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        raw_token = request.COOKIES.get("access_token")
        request.jwt_pk = None
        if raw_token is not None:
            try:
                token = AccessToken(raw_token)
                request.jwt_pk = token.payload.get("user_id", None)
            except TokenError:
                pass

        response = self.get_response(request)
        return response