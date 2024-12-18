from django.urls import path, re_path

from app.consumers import MychatApp

from . import consumers

websocket_urlpatterns =[

    path('ws/wsc/',MychatApp.as_asgi()),
    re_path(r'ws/group/(?P<group_name>[\w-]+)/$', consumers.GroupChatConsumer.as_asgi()),
]