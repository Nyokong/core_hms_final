"""
ASGI config for hms_api project.

It exposes the ASGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/5.1/howto/deployment/asgi/
"""

# import os
# import django

# from django.conf import settings
# django.setup()


# os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')

# from channels.routing import ProtocolTypeRouter, URLRouter
# from channels.auth import AuthMiddlewareStack

# os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
# from django.core.asgi import get_asgi_application

# import api.routing 

# application = application = ProtocolTypeRouter({
#     "http": get_asgi_application(),
#     "websocket": URLRouter(api.routing.websocket_urlpatterns)
# })


import os
import django

from django.conf import settings

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()
from django.core.asgi import get_asgi_application

from channels.routing import ProtocolTypeRouter, URLRouter
from channels.auth import AuthMiddlewareStack

import api.routing

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')

application = application = ProtocolTypeRouter({
    "http": get_asgi_application(),
    "websocket": AuthMiddlewareStack(
        URLRouter(
            api.routing.websocket_urlpatterns
        )
    ),
})


CHANNEL_LAYERS = {
    "default": {
        "BACKEND": "channels_redis.core.RedisChannelLayer",
        "CONFIG": {
            "hosts": [
                {
                    "host": "redis",  # Replace with the actual Redis container name
                    "port": 6379,
                    "password": None,  # Optional: Redis password
                },
            ],
        },
    },
}
