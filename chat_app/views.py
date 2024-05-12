from django.shortcuts import render, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.db.models import Q
from chat_app.models import *
from django.http.response import HttpResponse, HttpResponseRedirect
from django.contrib import messages
import cloudinary.uploader
from django.http import JsonResponse
import magic, json
from django.conf import settings

# def room_name(request):
#     return render(request, 'chat/enter_room_name.html')
# def room(request, room_name):
#     return render(request, 'chat/chat.html', {'room_name': room_name})


def home(request):
    unread_msg = ChatMessage.count_overall_unread_msg(request.user.id)
    return render(request, "chat/home.html", {"unread_msg": unread_msg})


@login_required
def create_friend(request):
    user_1 = request.user
    if request.GET.get("id"):
        user2_id = request.GET.get("id")
        user_2 = get_object_or_404(User, id=user2_id)
        get_create = ChatSession.create_if_not_exists(user_1, user_2)
        if get_create:
            messages.add_message(
                request,
                messages.SUCCESS,
                f"{user_2.username} successfully added in your chat list!!",
            )
        else:
            messages.add_message(
                request,
                messages.SUCCESS,
                f"{user_2.username} already added in your chat list!!",
            )
        return HttpResponseRedirect("/create_friend")
    else:
        user_all_friends = ChatSession.objects.filter(Q(user1=user_1) | Q(user2=user_1))
        user_list = []
        for ch_session in user_all_friends:
            user_list.append(ch_session.user1.id)
            user_list.append(ch_session.user2.id)
        all_user = User.objects.exclude(
            Q(username=user_1.username) | Q(id__in=list(set(user_list)))
        )
    return render(request, "chat/create_friend.html", {"all_user": all_user})


@login_required
def friend_list(request):
    user_inst = request.user
    user_all_friends = (
        ChatSession.objects.filter(Q(user1=user_inst) | Q(user2=user_inst))
        .select_related("user1", "user2")
        .order_by("-updated_on")
    )
    all_friends = []
    for ch_session in user_all_friends:
        user, user_inst = (
            [ch_session.user2, ch_session.user1]
            if request.user.username == ch_session.user1.username
            else [ch_session.user1, ch_session.user2]
        )
        un_read_msg_count = (
            ChatMessage.objects.filter(
                chat_session=ch_session.id, message_detail__read=False
            )
            .exclude(user=user_inst)
            .count()
        )
        data = {
            "user_name": user.username,
            "room_name": ch_session.room_group_name,
            "un_read_msg_count": un_read_msg_count,
            "status": user.profile_detail.is_online,
            "user_id": user.id,
        }
        all_friends.append(data)

    return render(request, "chat/friend_list.html", {"user_list": all_friends})


import os
from urllib.parse import urlparse


@login_required
def start_chat(request, room_name):
    current_user = request.user
    try:
        check_user = ChatSession.objects.filter(
            Q(id=room_name[5:]) & (Q(user1=current_user) | Q(user2=current_user))
        )
    except Exception:
        return HttpResponse("Something went wrong!!!")
    if check_user.exists():
        chat_user_pair = check_user.first()
        opposite_user = (
            chat_user_pair.user2
            if chat_user_pair.user1.username == current_user.username
            else chat_user_pair.user1
        )

        fetch_all_message = (
            ChatMessage.objects.filter(chat_session__id=room_name[5:])
            .order_by("message_detail__timestamp")
            .select_related("chat_session")
        )

        fetch_messages_with_url = fetch_all_message.filter(~Q(message_detail__url=None))

        for message in fetch_all_message:
            if "url" in message.message_detail:
                url = message.message_detail["url"]
                path = urlparse(url).path
                fileExtension = os.path.splitext(path)[1]
                print(f"file extension ------------------------: {fileExtension}")
                print(
                    f"file extension ---------------------------------------------------------------------------"
                )
                # Dynamically create fileExtension as an attribute on ChatMessage
                message.fileExtension = fileExtension
                print(
                    f"file extension ------------------------: {message.message_detail}----{message.fileExtension }"
                )
            else:
                message.file_Extension = None

        return render(
            request,
            "chat/start_chat.html",
            {
                "room_name": room_name,
                "opposite_user": opposite_user,
                "fetch_all_message": fetch_all_message,
            },
        )
    else:
        return HttpResponse("You have't permission to chatting with this user!!!")


def get_last_message(request):
    session_id = request.data.get("room_id")
    qs = ChatMessage.objects.filter(chat_session__id=session_id)[10]
    return qs


def upload_file(request):
    if request.method == "POST":
        if request.FILES.get("file"):
            uploaded_file = request.FILES["file"]

            # Create a magic object
            magic_instance = magic.Magic(mime=True)
            # Get the MIME type using the magic object and the file contents
            mime_type = magic_instance.from_buffer(uploaded_file.read(2048))
            print(f"mime_type-------------------------: {mime_type}")
            uploaded_file.seek(0)  # Move the file pointer to the start of the file
            # other Cloudinary will raise exception: Empty File

            # Check if the MIME type starts with 'image/'
            if (
                mime_type.startswith("image/")
                or mime_type.startswith("vedio/")
                or mime_type.startswith("application/x-mpeg")
            ):
                return JsonResponse({"error": "incorrect file type"}, status=400)

            # Check if the MIME type is with 'application/octet-stream' or not in MIME_TYPE_IN_JSON
            # Load the JSON data from the file or Django settings

            mime_types = settings.MIME_TYPE
            key = "None"
            # Check if 'application/octet-stream' is in the MIME types
            if mime_type in mime_types.values():
                # Find the key corresponding to 'application/octet-stream'
                for k, value in mime_types.items():
                    # Send the key to the client
                    if value == mime_type:
                        key = k
                        print(f"key___________________________________________{key}")
                        break
            else:
                key = "None"

            try:
                # Upload the file to Cloudinary
                response = cloudinary.uploader.upload(
                    uploaded_file, resource_type="auto"
                )
                print(f"response_while_uploading: {response}")

                # Get the secure URL for the uploaded file
                uploaded_file_url = response["secure_url"]

                # Return the URL as JSON response
                return JsonResponse({"file_url": uploaded_file_url, "key": key})

            except cloudinary.exceptions.Error as e:
                print(f"Cloudinary upload error: {e}")
                # If upload fails, return an error response
                return JsonResponse(
                    {"error": "Error uploading file to Cloudinary"}, status=500
                )

        else:
            # If no file was uploaded, return a bad request error
            return JsonResponse(
                {"error": "File upload failed, request does not contain a file"},
                status=400,
            )
    else:
        # If request method is not POST, return method not allowed error
        return JsonResponse({"error": "Method not allowed"}, status=405)
