# from django.contrib.auth import logout
# from django.contrib.auth.decorators import login_required
# from django.contrib.auth.models import User
# from django.shortcuts import redirect, render

# from app.models import Mychats

# # Create your views here.

# @login_required
# def chat_home(request):
#     return render(request, 'index.html')

# @login_required
# def index(request):
#     frnd_name = request.GET.get('user',None)
#     mychats_data = None
#     if frnd_name:
#         if User.objects.filter(username=frnd_name).exists() and Mychats.objects.filter(me=request.user,frnd=User.objects.get(username=frnd_name)).exists():
#             frnd_ = User.objects.get(username=frnd_name)
#             mychats_data = Mychats.objects.get(me=request.user,frnd=frnd_).chats
#     frnds = User.objects.exclude(pk=request.user.id)
#     return render(request,'index.html',{'my':mychats_data,'chats': mychats_data,'frnds':frnds})

# @login_required
# def logout_view(request):
#     logout(request)
#     return redirect('login')


from django.contrib.auth import logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.shortcuts import redirect, render

from app.models import Message, Mychats

# Create your views here.

@login_required
def chat_home(request):
    return render(request, 'index.html')

@login_required
def index(request):
    frnd_name = request.GET.get('user', None)
    mychats_data = None
    if frnd_name:
        frnd_ = User.objects.filter(username=frnd_name).first()
        if frnd_ and Mychats.objects.filter(me=request.user, frnd=frnd_).exists():
            mychats_data = Message.objects.filter(chat__me=request.user, chat__frnd=frnd_).order_by('timestamp')
    frnds = User.objects.exclude(pk=request.user.id)
    return render(request, 'index.html', {'my': mychats_data, 'chats': mychats_data, 'frnds': frnds})

@login_required
def logout_view(request):
    logout(request)
    return redirect('login')
