from __future__ import annotations

from typing import Any, Generator

from dify_plugin import Tool
from dify_plugin.entities.tool import ToolInvokeMessage

from ._client import PyPIClient
from ._errors import friendly_error_message


class PyPIVulnerabilitiesTool(Tool):
    def _invoke(self, tool_parameters: dict[str, Any]) -> Generator[ToolInvokeMessage, None, None]:
        name = (tool_parameters.get("package") or "").strip()
        if not name:
            yield self.create_text_message("package is required, e.g. \"requests\".")
            return
        version = (tool_parameters.get("version") or "").strip() or None
        try:
            with PyPIClient() as client:
                result = client.vulnerabilities(name, version)
        except Exception as exc:
            yield self.create_text_message(friendly_error_message(exc))
            return
        yield self.create_json_message(result)
        if not result["vulnerabilities"]:
            yield self.create_text_message(
                f"No known vulnerabilities for {result['package']} {result['version']} in OSV."
            )
            return
        lines = [f"{result['count']} known vulnerability(ies) for {result['package']} {result['version']}:"]
        for item in result["vulnerabilities"]:
            fixed = ", ".join(item.get("fixed_versions") or []) or "no fixed release listed"
            lines.append(f"- {item['id']}: {item.get('summary') or ''} (fixed in: {fixed})")
        yield self.create_text_message("\n".join(lines))
