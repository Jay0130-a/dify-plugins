from __future__ import annotations

from typing import Any, Generator

from dify_plugin import Tool
from dify_plugin.entities.tool import ToolInvokeMessage

from ._client import HackerNewsClient
from ._errors import friendly_error_message


class HNGetStoryTool(Tool):
    def _invoke(self, tool_parameters: dict[str, Any]) -> Generator[ToolInvokeMessage, None, None]:
        raw_id = tool_parameters.get("story_id")
        try:
            story_id = int(str(raw_id).strip())
        except (TypeError, ValueError):
            yield self.create_text_message("story_id must be the numeric Hacker News item ID.")
            return
        try:
            with HackerNewsClient() as client:
                story = client.get_story(
                    story_id,
                    max_comments=int(tool_parameters.get("max_comments") or 10),
                    comment_depth=int(tool_parameters.get("comment_depth") or 1),
                )
        except Exception as exc:
            yield self.create_text_message(friendly_error_message(exc))
            return
        yield self.create_json_message(story)
        lines = [f"{story['title']} ({story.get('points') or 0} points)", story["hn_url"]]
        if story.get("text"):
            lines.append("")
            lines.append(story["text"][:1500])
        for c in story.get("comments", []):
            lines.append("")
            lines.append(f"- {c.get('author')}: {c.get('text', '')[:500]}")
        yield self.create_text_message("\n".join(lines))
