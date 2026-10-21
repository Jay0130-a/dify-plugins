from dify_plugin import ToolProvider


class HackerNewsProvider(ToolProvider):
    """Public, credential-free provider: nothing to validate."""

    def _validate_credentials(self, credentials: dict) -> None:
        return None
