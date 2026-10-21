from __future__ import annotations

from typing import Any, Generator

from dify_plugin import Tool
from dify_plugin.entities.tool import ToolInvokeMessage

from ._client import ZoteroClient
from ._errors import friendly_error_message


def _format(item: dict[str, Any]) -> str:
    lines = [str(item.get("title", ""))]
    creators = ", ".join(item.get("creators", []))
    if creators:
        lines.append(f"Authors: {creators}")
    meta = " | ".join(
        str(item[k])
        for k in ("itemType", "date", "publication", "doi", "url")
        if item.get(k)
    )
    if meta:
        lines.append(meta)
    if item.get("abstract"):
        lines.append("")
        lines.append(str(item["abstract"]))
    for note in item.get("notes", []):
        lines.append("")
        lines.append(f"[note] {note}")
    return "\n".join(lines)


class ZoteroGetItemTool(Tool):
    def _invoke(
        self, tool_parameters: dict[str, Any]
    ) -> Generator[ToolInvokeMessage, None, None]:
        item_key = (tool_parameters.get("item_key") or "").strip()
        if not item_key:
            yield self.create_text_message("Item key is required (the 8-character key from Zotero).")
            return

        try:
            with ZoteroClient.from_credentials(self.runtime.credentials) as client:
                item = client.get_item(
                    item_key,
                    include_notes=bool(tool_parameters.get("include_notes", True)),
                )
        except Exception as exc:
            yield self.create_text_message(friendly_error_message(exc))
            return

        yield self.create_json_message(item)
        yield self.create_text_message(_format(item))
