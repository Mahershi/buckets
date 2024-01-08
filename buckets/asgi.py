"""
ASGI config for buckets project.

It exposes the ASGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/4.1/howto/deployment/asgi/
"""

import os

from django.core.asgi import get_asgi_application
from channels.routing import ProtocolTypeRouter, URLRouter
from myapp.views import BucketConsumer
from django.urls import re_path
from .jwtAuthMiddleware import JwtAuthMiddlewareStack



os.environ.setdefault("DJANGO_SETTINGS_MODULE", "buckets.settings")

application = ProtocolTypeRouter(
    {
        'websocket': JwtAuthMiddlewareStack(
            URLRouter([
                re_path(r'bucket/stream/(?P<bucket_id>\w+)/$', BucketConsumer.as_asgi()),
            ])
        ),
        'http': get_asgi_application()
    }
)
