# from django.contrib import admin

# from app.models import Mychats

# # Register your models here.

# @admin.register(Mychats)
# class MychatAdmin(admin.ModelAdmin):
#     list_display = ('id','me','frnd','chats')



from django.contrib import admin

from app.models import Message, Mychats

# Register your models here.

@admin.register(Mychats)
class MychatAdmin(admin.ModelAdmin):
    list_display = ('id', 'me', 'frnd', 'created_at')

@admin.register(Message)
class MessageAdmin(admin.ModelAdmin):
    list_display = ('id', 'chat', 'user', 'msg', 'timestamp')
