from django import forms
from django.core.exceptions import ValidationError
from .models import VideoAsset

MAX_VIDEO_SIZE_BYTES = 10 * 1024 * 1024 * 1024  # 10 GB
ALLOWED_VIDEO_MIMES = {
    "video/mp4", "video/quicktime", "video/x-matroska",
    "video/webm", "video/x-msvideo",
}


class VideoAssetForm(forms.ModelForm):
    class Meta:
        model = VideoAsset
        fields = ("movie", "episode", "video_file", "mime_type", "status")
        widgets = {
            "mime_type": forms.TextInput(attrs={"placeholder": "video/mp4"}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.instance and self.instance.pk:
            # On edit, don't require re-uploading the file
            self.fields["video_file"].required = False

    def clean_video_file(self):
        f = self.cleaned_data.get("video_file")
        if not f:
            return f
        if hasattr(f, "size") and f.size > MAX_VIDEO_SIZE_BYTES:
            raise ValidationError(
                f"File is {f.size / (1024**3):.2f} GB; maximum is 10 GB. "
                "Split large files or raise the limit in catalog/forms.py."
            )
        # MIME check: prefer the client-provided type, fall back to extension
        mime = (self.cleaned_data.get("mime_type") or "").lower()
        if not mime:
            guessed = getattr(f, "content_type", None)
            if guessed:
                mime = guessed.lower()
        if mime and mime not in ALLOWED_VIDEO_MIMES:
            raise ValidationError(
                f"Unsupported MIME type '{mime}'. Allowed: {sorted(ALLOWED_VIDEO_MIMES)}"
            )
        return f
