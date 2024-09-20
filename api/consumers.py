
import json
from channels.generic.websocket import WebsocketConsumer

# class FeedbackChannel(WebsocketConsumer):
#     def connect(self):
#         self.accept()

#         self.send(text_data=json.dumps({
#             'type': "connection_established",
#             'message':'You are connected!'
#         }))

from channels.generic.websocket import AsyncWebsocketConsumer

from channels.layers import get_channel_layer

class FeedbackChannel(AsyncWebsocketConsumer):
    async def connect(self):
        channel_layer = get_channel_layer()  # Get the channel layer instance
        await channel_layer.group_add("feedback_channel", self.channel_name)
        await self.accept()

        await self.send(text_data=json.dumps({
            'type': "connection_established",
            'message':'You are connected! hellow Govner'
        }))

    async def disconnect(self, close_code):
        channel_layer = get_channel_layer()
        await channel_layer.group_discard("feedback_channel", self.channel_name)

    async def receive(self, text_data):
        data = json.loads(text_data)
        print(data)