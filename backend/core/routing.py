from django.urls import re_path
from . import consumers

websocket_urlpatterns = [
    re_path(r'ws/water/(?P<user_id>\d+)/$', consumers.WaterDataConsumer.as_asgi()),
]