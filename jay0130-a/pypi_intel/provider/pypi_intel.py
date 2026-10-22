from dify_plugin import ToolProvider


class PyPIIntelProvider(ToolProvider):
    """Public, credential-free provider: nothing to validate."""

    def _validate_credentials(self, credentials: dict) -> None:
        return None
