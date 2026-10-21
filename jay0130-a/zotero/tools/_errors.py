from __future__ import annotations

import httpx

from ._client import ZoteroError


def friendly_error_message(exc: Exception, *, fallback: str = "Zotero request failed.") -> str:
    """Map any failure to a user-safe message; never embed credentials."""
    if isinstance(exc, ZoteroError):
        return exc.message
    if isinstance(exc, httpx.TimeoutException):
        return "Timed out talking to api.zotero.org."
    if isinstance(exc, httpx.HTTPError):
        return "Could not reach api.zotero.org. Check network connectivity and try again."
    return fallback
