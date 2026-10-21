from __future__ import annotations

from typing import Any, Generator

from dify_plugin import Tool
from dify_plugin.entities.tool import ToolInvokeMessage

from ._client import HackerNewsClient
from ._errors import friendly_error_message


class HNUserTool(Tool):
    def _invoke(self, tool_parameters: dict[str, Any]) -> Generator[ToolInvokeMessage, None, None]:
        username = (tool_parameters.get("username") or "").strip()
        if not username:
            yield self.create_text_message("username is required.")
            return
        try:
            with HackerNewsClient() as client:
                user = client.get_user(username, recent=int(tool_parameters.get("recent") or 5))
        except Exception as exc:
            yield self.create_text_message(friendly_error_message(exc))
            return
        yield self.create_json_message(user)
        lines = [f"{user['id']} — karma {user.get('karma')}, joined {user.get('created_at')}"]
        if user.get("about"):
            lines.append(user["about"][:500])
        for s in user.get("submissions", []):
            lines.append(f"- [{s.get('type')}] {s.get('title') or ''} {s.get('url') or ''}")
        yield self.create_text_message("\n".join(lines))
