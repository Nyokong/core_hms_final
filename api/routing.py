from django.urls import re_path
from . import consumers

websocket_urlpatterns = [
    # re_path(r'ws/feedback/(?P<chat_id>\w+)/$', consumers.FeedbackChannel.as_asgi()),
    re_path(r'ws/feedback/(?P<room_id>\d+)', consumers.FeedbackChannel.as_asgi()),
]