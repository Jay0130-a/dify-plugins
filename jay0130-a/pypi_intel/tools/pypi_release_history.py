from __future__ import annotations

from typing import Any, Generator

from dify_plugin import Tool
from dify_plugin.entities.tool import ToolInvokeMessage

from ._client import PyPIClient
from ._errors import friendly_error_message


class PyPIReleaseHistoryTool(Tool):
    def _invoke(self, tool_parameters: dict[str, Any]) -> Generator[ToolInvokeMessage, None, None]:
        name = (tool_parameters.get("package") or "").strip()
        if not name:
            yield self.create_text_message("package is required, e.g. \"requests\".")
            return
        try:
            with PyPIClient() as client:
                rows = client.releases(
                    name,
                    include_prereleases=bool(tool_parameters.get("include_prereleases") or False),
                    limit=int(tool_parameters.get("limit") or 10),
                )
        except Exception as exc:
            yield self.create_text_message(friendly_error_message(exc))
            return
        yield self.create_json_message({"package": name, "count": len(rows), "releases": rows})
        if not rows:
            yield self.create_text_message("No matching releases found.")
            return
        yield self.create_text_message(
            "\n".join(f"- {row['version']} ({row.get('uploaded_at') or 'unknown'})" for row in rows)
        )
