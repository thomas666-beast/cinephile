from datetime import timedelta

import jwt
from django.conf import settings
from django.utils import timezone

PLAYBACK_TOKEN_LIFETIME = timedelta(minutes=30)


def issue_playback_token(*, user, content_type: str, content_id: int) -> str:
    """
    Issue a short-lived JWT for playback of one specific content item.
    Validated later by the streaming layer (Task 12).

    Claims:
      - user_id: who this token is for
      - content_type: "movie" | "episode"
      - content_id: the item's PK
      - iat / exp: issued at / expiry
      - type: "playback" (distinguishes from auth JWTs)
    """
    now = timezone.now()
    payload = {
        "user_id": user.id,
        "content_type": content_type,
        "content_id": content_id,
        "type": "playback",
        "iat": int(now.timestamp()),
        "exp": int((now + PLAYBACK_TOKEN_LIFETIME).timestamp()),
    }
    return jwt.encode(payload, settings.SECRET_KEY, algorithm="HS256")


def verify_playback_token(token: str, *, expected_content_type: str, expected_content_id: int) -> dict:
    """
    Verify a playback token. Raises jwt.PyJWTError on any failure.
    Also checks content binding so a movie token can't be replayed for an episode.
    """
    payload = jwt.decode(token, settings.SECRET_KEY, algorithms=["HS256"])
    if payload.get("type") != "playback":
        raise jwt.InvalidTokenError("Not a playback token.")
    if payload.get("content_type") != expected_content_type:
        raise jwt.InvalidTokenError("Token is for different content type.")
    if payload.get("content_id") != expected_content_id:
        raise jwt.InvalidTokenError("Token is for a different content item.")
    return payload
