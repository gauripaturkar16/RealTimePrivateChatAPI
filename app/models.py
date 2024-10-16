from django.contrib.auth.models import User
from django.db import models

# Create your models here.

class Mychats(models.Model):
    me = models.ForeignKey(to=User, on_delete=models.CASCADE, related_name='it_me')
    frnd = models.ForeignKey(to=User, on_delete=models.CASCADE, related_name='my_frnd')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Chat between {self.me.username} and {self.frnd.username}"

class Message(models.Model):
    chat = models.ForeignKey(to=Mychats, on_delete=models.CASCADE, related_name='messages')
    
    # Make sender field nullable for the migration
    user = models.ForeignKey(to=User, on_delete=models.CASCADE, related_name='received_messages')
    sender = models.ForeignKey(to=User, on_delete=models.CASCADE, related_name='sent_messages', null=True)  # Allow null
    
    msg = models.TextField()
    attachment = models.FileField(upload_to='attachments/', null=True, blank=True)
    text = models.TextField(blank=True, null=True)
    audio_file = models.FileField(upload_to='audio/', blank=True, null=True)
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'Message from {self.sender.username} at {self.timestamp}'
