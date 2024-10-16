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
from django.core.files.storage import FileSystemStorage
from django.http import JsonResponse
from django.shortcuts import redirect, render
from django.views.decorators.csrf import csrf_exempt

from app.models import Message, Mychats

from .form import MessageForm


def send_message(request):
    if request.method == 'POST':
        form = MessageForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()  # This will save text and/or audio
            return JsonResponse({'status': 'Message sent successfully'})
    else:
        form = MessageForm()
    return render(request, 'chat/send_message.html', {'form': form})

@login_required
def chat_home(request):
    return render(request, 'index.html')

@login_required
def index(request):
    frnd_name = request.GET.get('user', None)
    mychats_data = None
    messages = None
    if frnd_name:
        frnd_ = User.objects.filter(username=frnd_name).first()
        if frnd_:
            # Get the chat between the current user and the selected friend
            mychats_data = Mychats.objects.filter(me=request.user, frnd=frnd_).first()
            if not mychats_data:
                mychats_data = Mychats.objects.filter(me=frnd_, frnd=request.user).first()
            # Fetch all the messages in that chat if the chat exists
            if mychats_data:
                messages = Message.objects.filter(chat=mychats_data).order_by('timestamp')

    frnds = User.objects.exclude(pk=request.user.id)
    return render(request, 'index.html', {
        'my': mychats_data, 
        'chats': messages,  # Pass the messages to the template
        'frnds': frnds
    })


@login_required
def send_message(request):
    if request.method == 'POST':
        message_text = request.POST.get('message')
        attachment = request.FILES.get('attachment')
        frnd_name = request.POST.get('frnd')  # Make sure to send the friend's username with the request
        # Handle the file upload
       
        if attachment:
            fs = FileSystemStorage()
            filename = fs.save(attachment.name, attachment)
            file_url = fs.url(filename)
        else:
            file_url = None

        # Create your Message object
        mychats_data = Mychats.objects.filter(me=request.user, frnd=frnd_name).first() or Mychats.objects.filter(me=frnd_name, frnd=request.user).first()

        message = Message.objects.create(
            chat=mychats_data,
            user=request.user,
            text=message_text,
            attachment=file_url  # Assuming your Message model has an attachment field
        )

        return JsonResponse({'status': 'success', 'file_url': file_url})

def upload_attachment(request):
    if request.method == 'POST' and request.FILES.get('attachment'):
        file = request.FILES['attachment']
        file_path = os.path.join(settings.MEDIA_ROOT, file.name)

        with open(file_path, 'wb+') as destination:
            for chunk in file.chunks():
                destination.write(chunk)

        return JsonResponse({'attachment': file.name})

    return JsonResponse({'error': 'No attachment uploaded'}, status=400)

import os

from django.conf import settings
from django.core.files.storage import default_storage
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt


@csrf_exempt 
def upload_file(request):
    if request.method == 'POST' and request.FILES.get('attachment'):
        file = request.FILES['attachment']
        filename = default_storage.save(file.name, file)
        file_url = default_storage.url(filename)  # Get the URL of the saved file
        return JsonResponse({'attachment': filename})
    return JsonResponse({'error': 'File upload failed'}, status=400)


@login_required
def logout_view(request):
    logout(request)
    return redirect('login')
