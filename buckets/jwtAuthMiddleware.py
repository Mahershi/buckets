from channels.db import database_sync_to_async
from django.contrib.auth.models import AnonymousUser
from jwt import decode as jwt_decode
from django.conf import settings
from channels.auth import AuthMiddlewareStack
from myapp.models import User
from channels.middleware import BaseMiddleware
from jwt.exceptions import ExpiredSignatureError

# This middleware is only for WS connections.

@database_sync_to_async
def get_user(validated_token):
    try:
        print(validated_token)
        user = User.objects.get(id=validated_token["user_id"])
        return user
    except User.DoesNotExist:
        return AnonymousUser()


class JWTAuthMiddleware(BaseMiddleware):
    def __init__(self, inner):
        # Store the ASGI application we were passed
        self.inner = inner

    async def __call__(self, scope, receive, send):
        print("JWT AUTH INIT")
        headers = dict(scope['headers'])
        qp = scope['query_string'].decode().split('=')
        auth_key = qp[0]
        scope_d = dict(scope)
        print("Scope:", scope_d)

        if b'authorization' in headers:
            token_name, token_key = headers[b'authorization'].decode().split()
            if token_name == 'Bearer':
                decoded_data = None
                try:
                    # if token is expired, it throws ExpiredSignatureError and returns AnonymousUser to reject connection
                    decoded_data = jwt_decode(token_key, settings.SECRET_KEY, algorithms=["HS256"])

                    scope["user"] = await get_user(validated_token=decoded_data)
                except ExpiredSignatureError as e:
                    scope["user"] = AnonymousUser()
        elif auth_key == 'Authorization':
            # if auth is sent in Query Params for Web Socket connection. Because some web socket connection packages on client end does not allow any headers.
            auth_val = qp[1]
            token_name, token_key = auth_val.split('%20')
            if token_name == 'Bearer':
                try:
                    # if token is expired, it throws ExpiredSignatureError and returns AnonymousUser to reject connection
                    decoded_data = jwt_decode(token_key, settings.SECRET_KEY, algorithms=["HS256"])

                    scope["user"] = await get_user(validated_token=decoded_data)
                except ExpiredSignatureError as e:
                    scope["user"] = AnonymousUser()

        return await super().__call__(scope, receive, send)


def JwtAuthMiddlewareStack(inner):
    return JWTAuthMiddleware(AuthMiddlewareStack(inner))