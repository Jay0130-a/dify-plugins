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


def _format(items: list[dict[str, Any]]) -> str:
    if not items:
        return "No matching items found in the library."
    lines = []
    for idx, item in enumerate(items, 1):
        creators = ", ".join(item.get("creators", [])[:3])
        header = f"{idx}. {item.get('title', '')}"
        if creators:
            header += f" — {creators}"
        if item.get("date"):
            header += f" ({item['date']})"
        lines.append(header)
        detail = f"   [{item.get('itemType', '')}] key={item.get('key', '')}"
        if item.get("doi"):
            detail += f" doi={item['doi']}"
        lines.append(detail)
        if item.get("abstract"):
            abstract = str(item["abstract"])
            lines.append(f"   {abstract[:300]}{'…' if len(abstract) > 300 else ''}")
    return "\n".join(lines)


class ZoteroSearchItemsTool(Tool):
    def _invoke(
        self, tool_parameters: dict[str, Any]
    ) -> Generator[ToolInvokeMessage, None, None]:
        query = (tool_parameters.get("query") or "").strip()
        if not query:
            yield self.create_text_message("Query is required.")
            return

        try:
            with ZoteroClient.from_credentials(self.runtime.credentials) as client:
                items = client.search_items(
                    query,
                    item_type=(tool_parameters.get("item_type") or "").strip() or None,
                    tag=(tool_parameters.get("tag") or "").strip() or None,
                    limit=_coerce_limit(tool_parameters.get("limit")),
                    include_abstract=bool(tool_parameters.get("include_abstract", True)),
                )
        except Exception as exc:
            yield self.create_text_message(friendly_error_message(exc))
            return

        output = {"query": query, "count": len(items), "items": items}
        yield self.create_json_message(output)
        yield self.create_text_message(_format(items))
