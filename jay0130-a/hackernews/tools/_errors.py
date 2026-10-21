from __future__ import annotations

import httpx

from ._client import HackerNewsError


def friendly_error_message(exc: Exception, *, fallback: str = "Hacker News request failed.") -> str:
    if isinstance(exc, HackerNewsError):
        return exc.message
    if isinstance(exc, httpx.TimeoutException):
        return "Timed out talking to Hacker News."
    if isinstance(exc, httpx.HTTPError):
        return "Could not reach Hacker News. Check network connectivity and try again."
    return fallback
