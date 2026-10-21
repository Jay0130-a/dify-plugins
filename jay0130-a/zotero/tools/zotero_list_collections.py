from __future__ import annotations

from typing import Any, Generator

from dify_plugin import Tool
from dify_plugin.entities.tool import ToolInvokeMessage

from ._client import ZoteroClient
from ._errors import friendly_error_message


def _coerce_limit(value: Any) -> int:
    try:
        return max(1, min(int(value or 25), 50))
    except (TypeError, ValueError):
        return 25


class ZoteroListCollectionsTool(Tool):
    def _invoke(
        self, tool_parameters: dict[str, Any]
    ) -> Generator[ToolInvokeMessage, None, None]:
        try:
            with ZoteroClient.from_credentials(self.runtime.credentials) as client:
                collections = client.list_collections(
                    limit=_coerce_limit(tool_parameters.get("limit"))
                )
        except Exception as exc:
            yield self.create_text_message(friendly_error_message(exc))
            return

        output = {"count": len(collections), "collections": collections}
        yield self.create_json_message(output)
        if collections:
            listing = "\n".join(
                f"- {c.get('name', '')} (key={c.get('key', '')}, {c.get('numItems', '?')} items)"
                for c in collections
            )
            yield self.create_text_message(f"Collections in the library://n{listing}")
        else:
            yield self.create_text_message("This library has no collections.")
