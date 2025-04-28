# chat/consumers.py
import json
from channels.generic.websocket import AsyncWebsocketConsumer
from datetime import datetime

class ChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.room_name = self.scope['url_route']['kwargs']['room_name']
        self.room_group_name = f'chat_{self.room_name}'

        self.username = self.scope['query_string'].decode().split('=')[1]

        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )

        await self.accept()

        # Notify others that this user is online
        await self.channel_layer.group_send(
            self.room_group_name,
            {
                'type': 'user_status',
                'username': self.username,
                'status': 'online'
            }
        )

    async def disconnect(self, close_code):
        # Notify others that this user went offline
        await self.channel_layer.group_send(
            self.room_group_name,
            {
                'type': 'user_status',
                'username': self.username,
                'status': 'offline'
            }
        )

        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )

    async def receive(self, text_data):
        text_data_json = json.loads(text_data)
        message_type = text_data_json.get('type', 'chat')

        if message_type == 'chat':
            message = text_data_json['message']
            username = text_data_json['username']

            await self.channel_layer.group_send(
                self.room_group_name,
                {
                    'type': 'chat_message',
                    'message': message,
                    'username': username,
                    'timestamp': datetime.now().strftime('%H:%M:%S')
                }
            )
        elif message_type == 'typing':
            username = text_data_json['username']
            await self.channel_layer.group_send(
                self.room_group_name,
                {
                    'type': 'typing_indicator',
                    'username': username
                }
            )

    async def chat_message(self, event):
        message = event['message']
        username = event['username']
        timestamp = event['timestamp']

        await self.send(text_data=json.dumps({
            'type': 'chat',
            'message': message,
            'username': username,
            'timestamp': timestamp
        }))

    async def typing_indicator(self, event):
        username = event['username']

        await self.send(text_data=json.dumps({
            'type': 'typing',
            'username': username
        }))

    async def user_status(self, event):
        await self.send(text_data=json.dumps({
            'type': 'user_status',
            'username': event['username'],
            'status': event['status'],  # 'online' or 'offline'
        }))
