from __future__ import annotations

import httpx

from ._client import PyPIError


def friendly_error_message(exc: Exception, *, fallback: str = "PyPI request failed.") -> str:
    if isinstance(exc, PyPIError):
        return exc.message
    if isinstance(exc, httpx.TimeoutException):
        return "Timed out talking to the package index."
    if isinstance(exc, httpx.HTTPError):
        return "Could not reach the package index. Check network connectivity and try again."
    return fallback
