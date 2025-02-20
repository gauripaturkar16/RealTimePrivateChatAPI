import os

import emoji
from django.conf import settings
from django.contrib import messages
from django.contrib.auth import logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.core.files.storage import FileSystemStorage, default_storage
from django.http import JsonResponse
from django.shortcuts import redirect, render
from django.views.decorators.csrf import csrf_exempt

from app.models import (Group, GroupMember, GroupMessage, Message, Mychats,
                        UProfile)

from .form import MessageForm, RegisterForm, UserProfileForm


@login_required
def home_view(request):
    # Fetch all friends (assuming frnds are all users except the logged-in user)
    frnds = User.objects.exclude(id=request.user.id)
    # Fetch chats for the current user
    chats = Message.objects.filter(chat__me=request.user) | Message.objects.filter(chat__frnd=request.user)
    
    # Fetch or create the user's profile
    user_profile, created = UProfile.objects.get_or_create(user=request.user)

    return render(request, 'index.html', {
        'user': request.user,
        'frnds': frnds,
        'chats': chats,
        'user_profile': user_profile,
    })

@login_required
def profile_view(request):
    # Get or create the user profile
    user_profile, created = UProfile.objects.get_or_create(user=request.user)
    
    if request.method == "POST":
        form = UserProfileForm(request.POST, request.FILES, instance=user_profile)
        if form.is_valid():
            form.save()
            return redirect('home')  # Redirect to home or another page after saving the profile
    else:
        form = UserProfileForm(instance=user_profile)

    return render(request, 'profile.html', {'form': form, 'user_profile': user_profile})

from .form import ProfileEditForm


@login_required
def edit_profile_view(request):
    # Get or create the user's profile
    profile, created = UProfile.objects.get_or_create(user=request.user)

    if request.method == 'POST':
        form = ProfileEditForm(request.POST, request.FILES, instance=profile)
        if form.is_valid():
            form.save()
            return redirect('profile')  # Replace 'profile' with the name of your profile view URL
    else:
        form = ProfileEditForm(instance=profile)

    return render(request, 'edit_profile.html', {'form': form})
# def send_message(request):
#     if request.method == 'POST':
#         form = MessageForm(request.POST, request.FILES)
#         if form.is_valid():
#             form.save()  # This will save text and/or audio
#             return JsonResponse({'status': 'Message sent successfully'})
#     else:
#         form = MessageForm()
#     return render(request, 'chat/send_message.html', {'form': form})

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


# @login_required
# def send_message(request):
#     if request.method == 'POST':
#         message_text = request.POST.get('message')
#         attachment = request.FILES.get('attachment')
#         frnd_name = request.POST.get('frnd')  # Make sure to send the friend's username with the request
#         # Handle the file upload
       
#         if attachment:
#             fs = FileSystemStorage()
#             filename = fs.save(attachment.name, attachment)
#             file_url = fs.url(filename)
#         else:
#             file_url = None

#         # Create your Message object
#         mychats_data = Mychats.objects.filter(me=request.user, frnd=frnd_name).first() or Mychats.objects.filter(me=frnd_name, frnd=request.user).first()

#         message = Message.objects.create(
#             chat=mychats_data,
#             user=request.user,
#             text=message_text,
#             attachment=file_url  # Assuming your Message model has an attachment field
#         )

#         return JsonResponse({'status': 'success', 'file_url': file_url})

from django.core.files.base import ContentFile


@csrf_exempt
def send_message(request):
    if request.method == "POST":
        message_text = request.POST.get('message', '')
        attachment = request.FILES.get('attachment', None)
        # Convert any emoji shortcodes in the message text to actual emojis
        message_text_with_emoji = emoji.emojize(message_text)
         # Save the message in the database (assuming your Message model has a text field)
        message =Message.objects.create(user=request.user, text=message_text_with_emoji)
          # Handle attachment saving if available
        attachment_name = None
        if attachment:
            # Save the attachment
            attachment_name = default_storage.save(f'media/{attachment.name}', ContentFile(attachment.read()))
        
        # Store the message and attachment info (example)
        # (You can replace this with your chat message saving logic)
        
        return JsonResponse({
            "success": True,
            "message_text": message_text_with_emoji,  # Return the message with emojis
            "attachment_name": attachment_name,  # Provide the attachment name here
        })
    
    return JsonResponse({
        "error": "Invalid request method"
    }, status=400)

def render_message(request, message_id):
    try:
        message = Message.objects.get(id=message_id)
    except Message.DoesNotExist:
        return JsonResponse({"error": "Message not found"}, status=404)

    # Render emoji shortcode as real emoji
    message_text = emoji.emojize(message.text)
    
    return render(request, 'index.html', {'message_text': message_text})
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

@csrf_exempt 
def upload_file(request):
    if request.method == 'POST' and request.FILES.get('attachment'):
        file = request.FILES['attachment']
        filename = default_storage.save(file.name, file)
        file_url = default_storage.url(filename)  # Get the URL of the saved file
        return JsonResponse({'attachment': filename})
    return JsonResponse({'error': 'File upload failed'}, status=400)

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

# View to list all groups
@login_required
def group_list(request):
    groups = Group.objects.all()
    return render(request, 'group_list.html', {'groups': groups})

# View to create a group
@login_required
def create_group(request):
    if request.method == 'POST':
        name = request.POST.get('name')
        description = request.POST.get('description', '')
        group = Group.objects.create(name=name, description=description)
        # Add the user as a member of the new group
        GroupMember.objects.create(group=group, user=request.user)
        return redirect('group_list')
    return render(request, 'create_group.html')

# View to show the messages of a group and send new messages
@login_required
def group_chat(request, group_id):
    group = Group.objects.get(id=group_id)
    messages = GroupMessage.objects.filter(group=group).order_by('-timestamp')
    
    if request.method == 'POST':
        content = request.POST.get('content')
        GroupMessage.objects.create(group=group, sender=request.user, content=content)
    
    return render(request, 'group_chat.html', {'group': group, 'messages': messages})

# View to list all groups
@login_required
def group_list(request):
    groups = Group.objects.all()
    return render(request, 'group_list.html', {'groups': groups})

# View to create a group
@login_required
def create_group(request):
    if request.method == 'POST':
        name = request.POST.get('name')
        description = request.POST.get('description', '')
        member_ids = request.POST.getlist('members')  # Get the list of selected member IDs

        group = Group.objects.create(name=name, description=description)
        # Add the user as a member of the new group
        GroupMember.objects.create(group=group, user=request.user)

         # Add the selected users as members
        for member_id in member_ids:
            user = User.objects.get(id=member_id)
            GroupMember.objects.create(group=group, user=user)

        return redirect('group_list')
     # Pass all users to the template for selection
    users = User.objects.exclude(id=request.user.id)  # Exclude the current user
    return render(request, 'create_group.html', {'users': users})

# View to show the messages of a group and send new messages
@login_required
def group_chat(request, group_id):
    group = Group.objects.get(id=group_id)
    messages = GroupMessage.objects.filter(group=group).order_by('-timestamp')
    
    if request.method == 'POST':
        content = request.POST.get('content')
        GroupMessage.objects.create(group=group, sender=request.user, content=content)
    
    return render(request, 'group_chat.html', {'group': group, 'messages': messages})

from django.db.models import Q


@login_required
def starred_messages_view(request):
    user = request.user  # Get the logged-in user
    starred_messages = Message.objects.filter(Q(sender=user) | Q(user=user), is_starred=True)
    return render(request, "starred_messages.html", {"starred_messages": starred_messages})

@login_required
def archived_chats_view(request):
    user = request.user  # Get the logged-in user
    archived_messages = Message.objects.filter(Q(sender=user) | Q(user=user), is_archived=True)
    return render(request, "archived_chats.html", {"archived_messages": archived_messages})

@login_required
def settings_view(request):
    user = request.user  # Get the logged-in user
    # Settings can be personalized or general for the user
    return render(request, "settings.html", {})