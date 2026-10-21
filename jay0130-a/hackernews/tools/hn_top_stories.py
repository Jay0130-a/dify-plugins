from __future__ import annotations

from typing import Any, Generator

from dify_plugin import Tool
from dify_plugin.entities.tool import ToolInvokeMessage

from ._client import HackerNewsClient
from ._errors import friendly_error_message


class HNTopStoriesTool(Tool):
    def _invoke(self, tool_parameters: dict[str, Any]) -> Generator[ToolInvokeMessage, None, None]:
        try:
            with HackerNewsClient() as client:
                stories = client.list_stories(
                    list_name=str(tool_parameters.get("list") or "top"),
                    limit=tool_parameters.get("limit") or 10,
                )
        except Exception as exc:
            yield self.create_text_message(friendly_error_message(exc))
            return
        yield self.create_json_message({"count": len(stories), "stories": stories})
        if not stories:
            yield self.create_text_message("No stories returned.")
            return
        lines = [f"{i}. {s['title']} ({s.get('points') or 0} points, {s.get('num_comments') or 0} comments) {s['hn_url']}" for i, s in enumerate(stories, 1)]
        yield self.create_text_message("\n".join(lines))
