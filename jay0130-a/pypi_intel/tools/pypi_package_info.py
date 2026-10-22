from __future__ import annotations

from typing import Any, Generator

from dify_plugin import Tool
from dify_plugin.entities.tool import ToolInvokeMessage

from ._client import PyPIClient
from ._errors import friendly_error_message


class PyPIPackageInfoTool(Tool):
    def _invoke(self, tool_parameters: dict[str, Any]) -> Generator[ToolInvokeMessage, None, None]:
        name = (tool_parameters.get("package") or "").strip()
        if not name:
            yield self.create_text_message("package is required, e.g. \"requests\".")
            return
        try:
            with PyPIClient() as client:
                info = client.info(name)
        except Exception as exc:
            yield self.create_text_message(friendly_error_message(exc))
            return
        yield self.create_json_message(info)
        lines = [
            f"{info['name']} {info['version']}" + (" (YANKED)" if info.get("yanked") else ""),
            info.get("summary") or "",
            f"license: {info.get('license') or 'unknown'} | requires-python: {info.get('requires_python') or 'any'}",
            f"releases: {info.get('release_count')} | latest uploaded: {info.get('latest_uploaded_at') or 'unknown'}",
        ]
        if info.get("home_page"):
            lines.append(f"home: {info['home_page']}")
        yield self.create_text_message("\n".join(line for line in lines if line))
