from __future__ import annotations

from typing import Any

from dify_plugin import ToolProvider
from dify_plugin.errors.tool import ToolProviderCredentialValidationError

from tools._client import ZoteroClient, ZoteroError
from tools._errors import friendly_error_message


class ZoteroProvider(ToolProvider):
    """Validate the library scope with one minimal read request.

    The API key never appears in logs, error messages, or test output; only
    the HTTP status and a user-facing message surface upward.
    """

    def _validate_credentials(self, credentials: dict[str, Any]) -> None:
        try:
            with ZoteroClient.from_credentials(credentials) as client:
                client.probe()
        except ZoteroError as exc:
            raise ToolProviderCredentialValidationError(
                friendly_error_message(exc, fallback="Zotero credential validation failed.")
            ) from None
        except Exception as exc:  # network or unexpected failure
            raise ToolProviderCredentialValidationError(
                friendly_error_message(exc, fallback="Zotero credential validation failed.")
            ) from None
