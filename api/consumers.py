import json
import django
django.setup()
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from .models import FeedbackMessage, custUser
from .serializers import FeedbackMsgSerializer

class FeedbackChannel(AsyncWebsocketConsumer):
    async def connect(self):
        self.chat_id = self.scope['url_route']['kwargs']['chat_id']
        self.chat_group = 'chat_%s' % self.chat_id

        await self.channel_layer.group_add(
            self.chat_group,
            self.channel_name
        )

        await self.accept()

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(
            self.chat_group,
            self.channel_name
        )

    async def receive(self, text_data):
        text_data_json = json.loads(text_data)
        message = text_data_json['message']
        user = self.scope['user']
        
        # Save the message to the database
        # await self.save_message(user, message)

        await self.channel_layer.group_send(
            self.chat_group,
            {
                'type':'chat_message',
                'message':message,
                'user': user
            }
        )

    async def chat_message(self, event):
        message = event['message']
        user = event['user']

        # somehow this code works
        print('message:', message, 'from', user)
        # Save the message to the database

        # getid = custUser.objects.get(username=user)

        # print('\nuser id: ', getid.id)

        # await self.send(text_data=json.dumps({
        #     'message': message,
        #     'user': user
        # }))

    # @database_sync_to_async
    # def save_message(self, user, message):
    #     data = {'user': user, 'message': message}

    #     serializer = FeedbackMsgSerializer(data=data)

    #     if serializer.is_valid():
    #         serializer.save()
    #     else:
    #         # Handle the case where the data is not valid
    #         print(serializer.errors)
    #     # FeedbackMessage.objects.create(user=user, message=message)   
