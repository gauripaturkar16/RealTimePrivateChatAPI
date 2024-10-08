# chatapp/urls.py
from django.contrib.auth import views as auth_views
from django.urls import path

from . import views
from .form import ChatLoginForm
from .views import upload_file

urlpatterns = [
    path('login/', auth_views.LoginView.as_view(template_name='login.html', authentication_form=ChatLoginForm), name='login'),
    path('index/', views.index, name='index'),
    path('logout/',views.logout_view,name='logout'),
    path('upload/', upload_file, name='upload_file'),

]
