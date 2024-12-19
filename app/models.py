from django.contrib.auth.models import User
from django.db import models


class UProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    profile_picture = models.ImageField(upload_to='profile_pics/', null=True, blank=True)
    bio = models.TextField(null=True, blank=True)
    location = models.CharField(max_length=255, null=True, blank=True)

    def __str__(self):
        return f"{self.user.username}'s Profile"
    
    def get_profile_picture(self):
        if self.profile_picture:
            return self.profile_picture.url
        return None

class Mychats(models.Model):
    me = models.ForeignKey(to=User, on_delete=models.CASCADE, related_name='it_me')
    frnd = models.ForeignKey(to=User, on_delete=models.CASCADE, related_name='my_frnd')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Chat between {self.me.username} and {self.frnd.username}"

class Message(models.Model):
    chat = models.ForeignKey(to=Mychats, on_delete=models.CASCADE, related_name='messages')
    msg = models.TextField()  # Emojis are stored as part of the text
    # Make sender field nullable for the migration
    user = models.ForeignKey(to=User, on_delete=models.CASCADE, related_name='received_messages')
    sender = models.ForeignKey(to=User, on_delete=models.CASCADE, related_name='sent_messages', null=True)  # Allow null
    msg = models.TextField()
    attachment = models.FileField(upload_to='attachments/', null=True, blank=True)
    text = models.TextField(blank=True, null=True)
    audio_file = models.FileField(upload_to='audio/', blank=True, null=True)
    timestamp = models.DateTimeField(auto_now_add=True)
    is_starred = models.BooleanField(default=False)  # For starred messages
    is_archived = models.BooleanField(default=False)  # For archived chats

    def __str__(self):
        return f'Message from {self.sender.username} at {self.timestamp}'

# Model to represent a Group
class Group(models.Model):
    name = models.CharField(max_length=255)
    description = models.TextField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name

# Model to represent a Group Message
class GroupMessage(models.Model):
    group = models.ForeignKey(Group, related_name='messages', on_delete=models.CASCADE)
    sender = models.ForeignKey(User, on_delete=models.CASCADE)
    content = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.sender.username}: {self.content[:30]}..."

# Model to represent a User's membership in a Group
class GroupMember(models.Model):
    group = models.ForeignKey(Group, related_name='members', on_delete=models.CASCADE)
    user = models.ForeignKey(User, related_name='group_memberships', on_delete=models.CASCADE)
    joined_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username} in {self.group.name}"