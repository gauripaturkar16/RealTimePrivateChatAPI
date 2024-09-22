


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
    user = models.ForeignKey(to=User, on_delete=models.CASCADE)
    msg = models.TextField()
    attachment = models.FileField(upload_to='attachments/', null=True, blank=True)
    timestamp = models.DateTimeField(auto_now_add=True)
    def __str__(self):
        return f"Message from {self.user.username} at {self.timestamp}"
