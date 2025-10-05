"""Custom decoding"""

from typing import Any, TypeVar
import msgspec

from .types import HetznerTime, VerifiedTime

T = TypeVar("T", bound=msgspec.Struct)

HETZNER_TIME_FORMAT = "%Y-%m-%d %H:%M:%S.%f %z %Z"


def enc_hook(obj: Any) -> Any:
    """Given an object that msgspec doesn't know how to serialize by
    default, convert it into an object that it does know how to
    serialize"""
    if isinstance(obj, HetznerTime):
        return obj.strftime(HETZNER_TIME_FORMAT)
        # timezoneinfo = obj.strftime("%z %Z")
        # return f"{timestamp} {timezoneinfo}"

    if isinstance(obj, VerifiedTime):
        # 2025-09-26 06:38:40.535 +0000 UTC
        # Get the timestamp first
        if obj.timestamp:
            return obj.timestamp.strftime(HETZNER_TIME_FORMAT)
            # timestamp = obj.timestamp.isoformat(" ", timespec="milliseconds")
            # timezoneinfo = obj.timestamp.strftime("%z %Z")
            # return f"{timestamp} {timezoneinfo}"
        return ""
    raise NotImplementedError


def dec_hook(typ: type, obj: Any) -> Any:
    """Given a type in a schema, convert ``obj`` (composed of natively
    supported objects) into an object of type ``type``.

    Any `TypeError` or `ValueError` exceptions raised by this method will
    be considered "user facing" and converted into a `ValidationError` with
    additional context. All other exceptions will be raised directly.
    """
    if typ is HetznerTime:
        return HetznerTime.strptime(obj, HETZNER_TIME_FORMAT)

    if typ is VerifiedTime:
        if isinstance(obj, str) and obj == "":
            return VerifiedTime(verified=False)
        return VerifiedTime(
            verified=True, timestamp=HetznerTime.strptime(obj, HETZNER_TIME_FORMAT)
        )
    raise NotImplementedError


def decode_object[T](response: str, type: type[T]) -> T:
    """Decode object."""
    return msgspec.json.decode(response, type=type, dec_hook=dec_hook)


def encode_object(obj: msgspec.Struct) -> bytes:
    """Encode an object."""
    return msgspec.json.encode(obj, enc_hook=enc_hook)
