
import json
from channels.generic.websocket import WebsocketConsumer
import redis

class FeedbackChannels(WebsocketConsumer):
    def connect(self):
        self.accept()

        self.send(text_data=json.dumps({
            'type': "connection_established",
            'message':'You are connected!'
        }))

        r = redis.Redis(host='redis', port=6379)
        print('success: ',r.get('my_key'))

from channels.generic.websocket import AsyncWebsocketConsumer

from channels.layers import get_channel_layer

class FeedbackChannel(AsyncWebsocketConsumer):
    async def connect(self):
        channel_layer = get_channel_layer()  # Get the channel layer instance
        await channel_layer.group_add("feedback_channel", self.channel_name)
        await self.accept()

    async def disconnect(self, close_code):
        channel_layer = get_channel_layer()
        await channel_layer.group_discard("feedback_channel", self.channel_name)

    async def receive(self, text_data):
        data = json.loads(text_data)
        print(data)