from django.urls import re_path
from . import channels

websocket_urlpatterns = [
    re_path(r'ws/feedback/(?P<chat_id>\w+)/$', channels.FeedbackChannel.as_asgi()),
]