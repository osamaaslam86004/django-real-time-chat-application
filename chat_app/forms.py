from django import forms
from django.core.exceptions import ValidationError
from django.core.validators import FileExtensionValidator


def validate_video_file(value):
    if not value.name.endswith((".mp4", ".avi", ".mov", ".mkv")):
        raise ValidationError("Only video files (MP4, AVI, MOV, MKV) are allowed.")


class VideoUploadForm(forms.Form):
    video_file = forms.FileField(
        label="Select a video file",
        required=True,
        validators=[
            FileExtensionValidator(allowed_extensions=["mp4", "avi", "mov", "mkv"])
        ],
    )

    def clean_video_file(self):
        video_file = self.cleaned_data["video_file"]
        validate_video_file(video_file)
        return video_file
