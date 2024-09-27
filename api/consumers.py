
import json
from channels.generic.websocket import WebsocketConsumer
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.layers import get_channel_layer
from .models import FeedbackRoom, custUser, FeedbackMessage

import threading
from django.db import transaction

from asgiref.sync import async_to_sync, sync_to_async

import logging
logger = logging.getLogger('api')


class FeedbackChannel(WebsocketConsumer):
    def connect(self):
        channel_layer = get_channel_layer()  # Get the channel layer instance
        self.user_id = self.scope['user'].id 
        self.room_id = self.scope['url_route']['kwargs']['room_id']  # Extract room_id
        # self.group_name = f'user_{self.user_id}'
        self.group_name = f'room_{self.room_id}'
        
        # Join room channel
        async_to_sync(channel_layer.group_add)(self.group_name, self.channel_name)

        # accept connection
        self.accept()

        # send ACK to client
        async_to_sync(self.send(text_data=json.dumps({
            'type': "connection_established",
            'message': 'You are connected!'
        })))

    # what happens the the connection is cut
    def disconnect(self, close_code):
        channel_layer = get_channel_layer()
        channel_layer.group_discard(self.group_name, self.channel_name)

    
    def receive(self, text_data):
        data = json.loads(text_data)
        message = data['message']

        try:
            feedback_room = FeedbackRoom.objects.get(pk=self.room_id) 

            if feedback_room:
                # Use the feedback_room object
                # ... your code here ...
                logger.info(f"Room retrieved successfully! ROOM: {feedback_room.id} {message}")
                
                async_to_sync(
                        self.channel_layer.group_send
                )(
                        self.group_name,
                        {
                            'type': 'feedback_message',
                            'message': message,
                            'sender_id': self.user_id,
                        }
                    )
                
                # create Feedback message
                FeedbackMessage.objects.create(
                    feedback_room=feedback_room,
                    sender=self.scope['user'],
                    message=message
                )

                # sync_to_async(self.send(text_data=json.dumps({
                #     'message': message,
                #     'sender': feedback_room.lecturer.username,
                # })))
            else:
                logger.info(f"feedback_room doesnt exist! ROOM: {self.room_id}")

        except FeedbackRoom.DoesNotExist:
            # Handle invalid room ID or create a new room (optional)
            logger.info("cannot find room | Room should aleady exist")

    def get_room(self):
        # Alternatively, use async_to_sync from django.db
        # from django.db import async_to_sync
        # return await async_to_sync(FeedbackRoom.objects.get)(pk=self.room_id)
        pass
        # with transaction.atomic():
        #     logger.info("Logged data")
        #     return await sync_to_async(FeedbackRoom.objects.get)(pk=self.room_id)

    def feedback_message(self, event):
        message = event['message']
        sender = event['sender_id']

        # Send message to WebSocket
        self.send(text_data=json.dumps({
            'message': message,
            'sender': sender,
        }))
