# chatapp/urls.py
from django.contrib.auth import views as auth_views
from django.urls import path

from . import views
from .form import ChatLoginForm
from .views import profile_view, upload_file

urlpatterns = [
    path('login/', auth_views.LoginView.as_view(template_name='login.html', authentication_form=ChatLoginForm), name='login'),
    path('index/', views.index, name='index'),
    path('logout/',views.logout_view,name='logout'),
    path('upload_file/', upload_file, name='upload_file'),
    path('profile/', profile_view, name='profile'),
    path('register/', views.register_view, name='register'),
    path('groups/', views.group_list, name='group_list'),
    path('groups/create/', views.create_group, name='create_group'),
    path('groups/<int:group_id>/', views.group_chat, name='group_chat'),
     path('send_message', views.send_message, name='send_message'),
]
