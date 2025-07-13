import os
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'water_management.settings')  # ✅ FIRST

import django
django.setup()  # ✅ ADD THIS to properly initialize Django apps

from django.core.asgi import get_asgi_application
from channels.routing import ProtocolTypeRouter, URLRouter
from channels.auth import AuthMiddlewareStack
import core.routing

application = ProtocolTypeRouter({
    "http": get_asgi_application(),
    "websocket": AuthMiddlewareStack(
        URLRouter(core.routing.websocket_urlpatterns)
    ),
})
