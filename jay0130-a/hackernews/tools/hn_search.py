from __future__ import annotations

from typing import Any, Generator

from dify_plugin import Tool
from dify_plugin.entities.tool import ToolInvokeMessage

from ._client import HackerNewsClient
from ._errors import friendly_error_message


class HNSearchTool(Tool):
    def _invoke(self, tool_parameters: dict[str, Any]) -> Generator[ToolInvokeMessage, None, None]:
        query = (tool_parameters.get("query") or "").strip()
        if not query:
            yield self.create_text_message("Query is required.")
            return
        try:
            with HackerNewsClient() as client:
                hits = client.search(
                    query,
                    search_type=str(tool_parameters.get("search_type") or "relevance"),
                    tags=(tool_parameters.get("tags") or "").strip() or None,
                    min_points=tool_parameters.get("min_points") or None,
                    max_age_days=tool_parameters.get("max_age_days") or None,
                    limit=tool_parameters.get("limit") or 10,
                )
        except Exception as exc:
            yield self.create_text_message(friendly_error_message(exc))
            return
        yield self.create_json_message({"query": query, "count": len(hits), "results": hits})
        if not hits:
            yield self.create_text_message("No matching Hacker News items.")
            return
        lines = []
        for i, hit in enumerate(hits, 1):
            head = f"{i}. [{hit['type']}] {hit['title'] or hit['text'][:80]}"
            if hit.get("points") is not None:
                head += f" ({hit['points']} points, {hit.get('num_comments') or 0} comments)"
            lines.append(head)
            lines.append(f"   {hit['hn_url']}")
        yield self.create_text_message("\n".join(lines))
