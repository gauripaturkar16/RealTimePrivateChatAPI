import datetime
import json

from asgiref.sync import async_to_sync
from channels.db import database_sync_to_async
from channels.generic.websocket import AsyncWebsocketConsumer
from django.contrib.auth.models import AnonymousUser, User

from app.models import Message, Mychats

from .models import Group, GroupMember, GroupMessage


class GroupChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        group_name = self.scope['url_route']['kwargs']['group_name']
        # Sanitize the group name by replacing spaces with underscores
        group_name = group_name.replace(" ", "_")    
        # Validate the group name
        if not group_name.isalnum() and not all(c in 'abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789-_.' for c in group_name):
                raise ValueError("Invalid group name.")
        
        # Fetch the group object using the group_name (sanitize it)
        self.group = await self.get_group(group_name)

        # Check if the user is a member of the group (you can skip this if it's not needed)
        self.user = self.scope['user']
        
            # Join the group
        await self.channel_layer.group_add(
                group_name,
                self.channel_name
            )
            # Accept the WebSocket connection
        await self.accept()

    async def send_system_message(self, message):
            await self.send(text_data=json.dumps({
                "system": message,
                "timestamp": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            }))

    async def disconnect(self, close_code):
          # Get the group name again (for disconnection)
        group_name = self.scope['url_route']['kwargs']['group_name']
        # Leave the group when disconnected
        await self.channel_layer.group_discard(
            group_name,
            self.channel_name
        )
    
    async def receive(self, text_data):
        try:
            data = json.loads(text_data)
            message = data['message']
            if message and self.user:
                # Save the message in the database
                await self.save_message(self.group, self.user, message)

                # Broadcast the message to the group
                await self.channel_layer.group_send(
                    self.group.name,
                    {
                        'type': 'chat_message',
                        'message': message,
                        'sender': self.user.username
                    }
                )
            # Now handle the message
        except KeyError:
            # Handle the error, possibly send a warning to the client
            await self.send(text_data=json.dumps({
                'error': 'Message key is missing'
            }))
        except json.JSONDecodeError:
            # Handle invalid JSON
            await self.send(text_data=json.dumps({
                'error': 'Invalid JSON format'
            }))
        
    async def chat_message(self, event):
        message = event['message']
        sender = event['sender']
        
        # Send message to WebSocket
        await self.send(text_data=json.dumps({
            'message': message,
            'sender': sender
        }))
    
    @database_sync_to_async
    def get_group(self, group_name):
        try:
            return Group.objects.get(name=group_name)
        except Group.DoesNotExist:
            return None

    @database_sync_to_async
    def save_message(self, group, sender, content):
        return GroupMessage.objects.create(group=group, sender=sender, content=content)
    
    @database_sync_to_async
    def is_user_member(self, group, user):
        return GroupMember.objects.filter(group=group, user=user).exists()

    
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
