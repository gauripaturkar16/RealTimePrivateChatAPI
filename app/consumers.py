import datetime
import json

from asgiref.sync import async_to_sync
from channels.db import database_sync_to_async
from channels.generic.websocket import AsyncWebsocketConsumer
from django.contrib.auth.models import User

from app.models import Message, Mychats


class MychatApp(AsyncWebsocketConsumer):
    
    async def connect(self):
        user = self.scope['user']
        
        if user.is_authenticated:
            # User is authenticated, proceed with connection
            await self.accept()
            await self.channel_layer.group_add(f"mychat_app_{user.username}", self.channel_name)
            print(f"WebSocket connected: {user.username}")
        else:
            # User is not authenticated, reject the connection
            await self.close()

    async def disconnect(self, close_code):
        user = self.scope['user']
        if user.is_authenticated:
            # Leave the group when the WebSocket disconnects
            await self.channel_layer.group_discard(f"mychat_app_{user.username}", self.channel_name)
            print(f"WebSocket disconnected: {user.username}")

    async def receive(self, text_data):
        text_data = json.loads(text_data)
        user = self.scope['user']

        if not user.is_authenticated:
            return  # Ignore the message if the user is not authenticated

        # Handle incoming message and send it to the appropriate group
        await self.channel_layer.group_send(
            f"mychat_app_{text_data['user']}",
            {
                'type': 'send_message',
                'msg': text_data['msg'],
                'attachment': text_data.get('attachment')  # Handle optional attachment
            }
        )
        
        # Save chat data (message and optional attachment)
        await self.save_chat(text_data)

    @database_sync_to_async
    def save_chat(self, text_data):
        user = self.scope['user']
        friend_username = text_data['user']
        friend = User.objects.get(username=friend_username)

        # Check if a chat exists, regardless of who initiated it
        mychats = Mychats.objects.filter(me=user, frnd=friend).first() or Mychats.objects.filter(me=friend, frnd=user).first()

        # If no chat exists, create one
        if not mychats:
            mychats = Mychats.objects.create(me=user, frnd=friend)

        # Save the message to the Message model, handling attachments if provided
        Message.objects.create(
            chat=mychats,
            user=user,
            msg=text_data['msg'],
            attachment=text_data.get('attachment')  # Save attachment if it's part of the data
        )

    async def send_message(self, event):
        # Send the message to WebSocket
        msg = event['msg']
        attachment = event.get('attachment')

        # Send message data back to WebSocket
        await self.send(text_data=json.dumps({
            'msg': msg,
            'attachment': attachment  # Include attachment in the WebSocket message if available
        }))
