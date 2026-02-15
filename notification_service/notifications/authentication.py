import jwt
from django.conf import settings
from rest_framework.authentication import BaseAuthentication
from rest_framework.exceptions import AuthenticationFailed


class JWTUser:
    """Объект пользователя из JWT-токена."""

    def __init__(self, payload):
        self.id = payload['user_id']
        self.pk = payload['user_id']
        self.username = payload['username']
        self.is_authenticated = True


class JWTAuthentication(BaseAuthentication):
    """JWT-аутентификация для сервиса уведомлений."""

    def authenticate(self, request):
        auth_header = request.headers.get('Authorization')
        if not auth_header or not auth_header.startswith('Bearer '):
            return None

        token = auth_header.split(' ')[1]
        try:
            payload = jwt.decode(token, settings.JWT_SECRET, algorithms=['HS256'])
        except jwt.ExpiredSignatureError:
            raise AuthenticationFailed('Токен истёк.')
        except jwt.InvalidTokenError:
            raise AuthenticationFailed('Недействительный токен.')

        user = JWTUser(payload)
        return (user, token)
