from __future__ import annotations

from typing import Any, Generator

from dify_plugin import Tool
from dify_plugin.entities.tool import ToolInvokeMessage

from ._client import ZoteroClient
from ._errors import friendly_error_message


def _coerce_limit(value: Any) -> int:
    try:
        return max(1, min(int(value or 10), 50))
    except (TypeError, ValueError):
        return 10


class ZoteroGetCollectionItemsTool(Tool):
    def _invoke(
        self, tool_parameters: dict[str, Any]
    ) -> Generator[ToolInvokeMessage, None, None]:
        collection_key = (tool_parameters.get("collection_key") or "").strip()
        if not collection_key:
            yield self.create_text_message("Collection key is required (the 8-character key from Zotero).")
            return

        try:
            with ZoteroClient.from_credentials(self.runtime.credentials) as client:
                items = client.get_collection_items(
                    collection_key,
                    limit=_coerce_limit(tool_parameters.get("limit")),
                    include_abstract=bool(tool_parameters.get("include_abstract", True)),
                )
        except Exception as exc:
            yield self.create_text_message(friendly_error_message(exc))
            return

        output = {"collection_key": collection_key, "count": len(items), "items": items}
        yield self.create_json_message(output)
        yield self.create_text_message(
            "\n".join(f"- {i.get('title', '')} (key={i.get('key', '')})" for i in items)
            or "This collection is empty."
        )
