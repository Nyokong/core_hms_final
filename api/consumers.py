
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
from .models import FeedbackRoom, custUser, FeedbackMessage

class FeedbackChannel(AsyncWebsocketConsumer):
    async def connect(self):
        channel_layer = get_channel_layer()  # Get the channel layer instance
        self.room_id = self.scope['url_route']['kwargs']['room_id']
        self.room_group_name = f'feedback_{self.room_id}'

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
        user_id = self.scope['user'].id

        feedbackroom = await FeedbackRoom.objects.get(id=self.room_id)
        user = await custUser.objects.get(id=user_id)

        # feedback_message = 
        # create the message
        FeedbackMessage.objects.create(
            feedback_room=feedbackroom,
            sender=user,
            message=message
        )

        # Send message to room group
        await self.channel_layer.group_send(
            self.room_group_name,
            {
                'type': 'feedback_message',
                'message': message,
                'username': user.username,
            }
        )

        print(data)

    async def feedback_message(self, event):
        message = event['message']
        sender = event['sender']

        # Send message to WebSocket
        await self.send(text_data=json.dumps({
            'message': message,
            'sender': sender,
        }))
