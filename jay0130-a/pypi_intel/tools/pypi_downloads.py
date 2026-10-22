from __future__ import annotations

from typing import Any, Generator

from dify_plugin import Tool
from dify_plugin.entities.tool import ToolInvokeMessage

from ._client import PyPIClient
from ._errors import friendly_error_message


class PyPIDownloadsTool(Tool):
    def _invoke(self, tool_parameters: dict[str, Any]) -> Generator[ToolInvokeMessage, None, None]:
        name = (tool_parameters.get("package") or "").strip()
        if not name:
            yield self.create_text_message("package is required, e.g. \"requests\".")
            return
        try:
            with PyPIClient() as client:
                stats = client.downloads(name)
        except Exception as exc:
            yield self.create_text_message(friendly_error_message(exc))
            return
        yield self.create_json_message({"package": name, **stats})
        yield self.create_text_message(
            f"{name} downloads — day: {stats.get('last_day')}, week: {stats.get('last_week')}, month: {stats.get('last_month')}"
        )
