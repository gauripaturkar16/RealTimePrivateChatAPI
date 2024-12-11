
from django.contrib.auth import logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.core.files.storage import FileSystemStorage
from django.http import JsonResponse
from django.shortcuts import redirect, render
from django.views.decorators.csrf import csrf_exempt

from app.models import Message, Mychats

from .form import MessageForm, UserProfileForm
from .models import UProfile


@login_required
def profile_view(request):
    # Get or create the user profile
    user_profile, created = UProfile.objects.get_or_create(user=request.user)
    
    if request.method == "POST":
        form = UserProfileForm(request.POST, request.FILES, instance=user_profile)
        if form.is_valid():
            form.save()
            return redirect('profile')  # Redirect to the profile page after saving
    else:
        form = UserProfileForm(instance=user_profile)

    return render(request, 'profile.html', {'form': form, 'user_profile': user_profile})


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

# def upload_attachment(request):
#     if request.method == 'POST' and request.FILES.get('attachment'):
#         file = request.FILES['attachment']
#         file_path = os.path.join(settings.MEDIA_ROOT, file.name)

#         with open(file_path, 'wb+') as destination:
#             for chunk in file.chunks():
#                 destination.write(chunk)

#         return JsonResponse({'attachment': file.name})

#     return JsonResponse({'error': 'No attachment uploaded'}, status=400)

@csrf_exempt 
def upload_file(request):
    if request.method == 'POST' and request.FILES.get('attachment'):
        file = request.FILES['attachment']
        filename = default_storage.save(file.name, file)
        file_url = default_storage.url(filename)  # Get the URL of the saved file
        print("File saved at:", file_url)  # Debugging line
        return JsonResponse({'attachment': file_url})
    return JsonResponse({'error': 'File upload failed'}, status=400)

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

# def register_view(request):
#     return render(request, 'register.html')

# from django.conf import settings
# from django.shortcuts import redirect


# def some_view(request):
#     return redirect(settings.REGISTER_URL)

from django.contrib import messages
from django.shortcuts import redirect, render

from .form import RegisterForm


def register_view(request):
    if request.method == 'POST':
        form = RegisterForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Account created successfully!')
            return redirect('login')  # Replace 'login' with your login page URL name
        else:
            messages.error(request, 'Please correct the errors below.')
    else:
        form = RegisterForm()
    return render(request, 'register.html', {'form': form})

@login_required
def logout_view(request):
    logout(request)
    return redirect('login')
