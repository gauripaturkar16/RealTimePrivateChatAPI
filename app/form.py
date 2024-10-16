# chatapp/forms.py
from django import forms
from django.contrib.auth.forms import AuthenticationForm

from .models import Message


class MessageForm(forms.ModelForm):
    class Meta:
        model = Message
        fields = ['chat', 'user', 'sender', 'msg']

class ChatLoginForm(AuthenticationForm):
    username = forms.CharField(widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Username'}))
    password = forms.CharField(widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'Password'}))
