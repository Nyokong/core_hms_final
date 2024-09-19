
import json
from channels.generic.websocket import WebsocketConsumer

class FeedbackChannel(WebsocketConsumer):
    def connect(self):
        self.accept()

        self.send(text_data=json.dumps({
            'type': "connection_established",
            'message':'You are connected!'
        }))

        print('success')