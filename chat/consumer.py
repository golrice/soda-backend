import json

from channels.generic.websocket import AsyncWebsocketConsumer
from application.models import User

from chat.models import Message

class ChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.room_name = self.scope['url_route']['kwargs']['room_name']
        self.room_group_name = f"chat_{self.room_name}"

        print(f"Connected to room {self.room_name}")

        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )

        await self.accept()

    async def disconnect(self, code):
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )

    async def receive(self, text_data):
        text_data_json = json.loads(text_data)
        message = text_data_json['text']
        sender = text_data_json['sender']
        receiver = text_data_json['receiver']
        sender = await User.objects.aget(username=sender)
        receiver = await User.objects.aget(username=receiver)

        new_message = Message(content=message, sender=sender, receiver=receiver)
        await new_message.asave()
        
        await self.channel_layer.group_send(
            self.room_group_name,
            {
                'type': 'chat_message',
                'text': message,
                'sender': text_data_json['sender'],
            }
        )
    
    async def chat_message(self, event):
        message = event['text']

        await self.send(text_data=json.dumps({
           'type': 'chat_message',
           'text': message,
           'sender': event['sender'],
        }))
