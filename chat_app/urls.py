from django.urls import path
from chat_app.views import home, create_friend, friend_list, upload_file
from chat_app.views import UploadVideoView, StartChatView
from django.views.generic.base import RedirectView

urlpatterns = [
    path("home/", home, name="home_page"),
    path("", RedirectView.as_view(url="/home")),
    path("create_friend/", create_friend, name="create_friend"),
    path("friend_list/", friend_list, name="friend_list"),
    path("chat/<str:room_name>/", StartChatView.as_view(), name="start_chat"),
    path("chat/chat_1/upload-file/", upload_file, name="upload_file"),
    path("chat/chat_1/upload-video/", UploadVideoView.as_view(), name="video_file"),
]
