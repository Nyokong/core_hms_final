
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
        self.room_name = self.scope['url_route']['kwargs']['room_name']
        self.room_group_name = f'chat_{self.room_name}'

        # Join room channel
        await channel_layer.group_add(self.room_group_name, self.channel_name)
        await self.accept()

        await self.send(text_data=json.dumps({
            'type': "connection_established",
            'message':'You are connected!'
        }))

    async def disconnect(self, close_code):
        channel_layer = get_channel_layer()
        await channel_layer.group_discard(self.room_group_name, self.channel_name)

    async def receive(self, text_data):
        data = json.loads(text_data)
        message = data['message']
        username = self.scope['user'].username

        # Send message to room group
        await self.channel_layer.group_send(
            self.room_group_name,
            {
                'type': 'feedback_message',
                'message': message,
                'username': username,
            }
        )

        print(data)

    async def feedback_message(self, event):
        message = event['message']
        username = event['username']

        # Send message to WebSocket
        await self.send(text_data=json.dumps({
            'message': message,
            'username': username,
        }))
