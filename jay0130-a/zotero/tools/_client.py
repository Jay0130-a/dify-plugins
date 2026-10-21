from __future__ import annotations

import re
from typing import Any
from xml.sax.saxutils import unescape

import httpx

BASE_URL = "https://api.zotero.org"
API_VERSION = "3"
DEFAULT_TIMEOUT = 30.0
MAX_LIMIT = 50
MAX_ITEM_KEY = 12

_TAG_RE = re.compile(r"<[^>]+>")
_WS_RE = re.compile(r"\s+")


class ZoteroError(Exception):
    """A user-safe error carrying the HTTP status; never embeds credentials."""

    def __init__(self, status: int, message: str) -> None:
        super().__init__(message)
        self.status = status
        self.message = message


_STATUS_MESSAGES: dict[int, str] = {
    400: "Zotero rejected the request parameters.",
    401: "Zotero rejected the credentials (unauthorized). Check that the API key is valid and the library ID matches it.",
    403: "The API key does not grant access to this library. For private libraries the key needs read permission; some groups restrict API access.",
    404: "Not found in Zotero. Check the library ID, item key, or collection key.",
    429: "Zotero is rate limiting requests (they allow a steady ~1 request/second). Retry shortly.",
}


def strip_html(text: str) -> str:
    """Turn a Zotero note (HTML) into plain text; collapse whitespace."""
    without_tags = _TAG_RE.sub("\n", text)
    unescaped = unescape(without_tags)
    return _WS_RE.sub(" ", unescaped).strip()


def _creator_name(creator: dict[str, Any]) -> str:
    name = creator.get("name")
    if name:
        return str(name)
    family = creator.get("family") or ""
    given = creator.get("given") or ""
    return f"{given} {family}".strip()


def compact_item(entry: dict[str, Any], *, include_abstract: bool) -> dict[str, Any]:
    data = entry.get("data") or entry
    item_type = str(data.get("itemType") or "")
    compact: dict[str, Any] = {
        "key": entry.get("key") or data.get("key"),
        "itemType": item_type,
        "title": data.get("title") or data.get("name") or "",
        "creators": [_creator_name(c) for c in data.get("creators", [])][:10],
        "date": data.get("date") or "",
        "tags": [t.get("tag") for t in data.get("tags", []) if isinstance(t, dict) and t.get("tag")][:10],
    }
    doi = data.get("DOI") or data.get("doi")
    if doi:
        compact["doi"] = doi
    if data.get("url"):
        compact["url"] = data.get("url")
    if data.get("publicationTitle"):
        compact["publication"] = data.get("publicationTitle")
    if include_abstract and data.get("abstractNote"):
        compact["abstract"] = strip_html(str(data["abstractNote"]))
    return compact


class ZoteroClient:
    """Minimal read-only client for the Zotero Web API v3 (GET only)."""

    def __init__(self, library_type: str, library_id: str, api_key: str | None = None) -> None:
        if library_type not in {"user", "group"}:
            raise ZoteroError(0, "Library type must be 'user' or 'group'.")
        library_id = (library_id or "").strip()
        if not library_id.isdigit():
            raise ZoteroError(0, "Library ID must be the numeric ID (digits only).")
        self._base = f"{library_type}s/{library_id}"
        headers = {
            "Zotero-API-Version": API_VERSION,
            "Accept": "application/json",
        }
        if api_key and api_key.strip():
            headers["Authorization"] = f"Bearer {api_key.strip()}"
        self._client = httpx.Client(base_url=BASE_URL, headers=headers, timeout=DEFAULT_TIMEOUT)

    @classmethod
    def from_credentials(cls, credentials: dict[str, Any]) -> "ZoteroClient":
        return cls(
            library_type=str(credentials.get("library_type") or "user"),
            library_id=str(credentials.get("library_id") or ""),
            api_key=credentials.get("api_key") or None,
        )

    def __enter__(self) -> "ZoteroClient":
        return self

    def __exit__(self, *_exc: object) -> None:
        self._client.close()

    def _get(self, path: str, params: dict[str, Any] | None = None) -> Any:
        try:
            response = self._client.get(f"/{self._base}{path}", params=params)
        except httpx.TimeoutException as exc:
            raise ZoteroError(0, "Timed out talking to api.zotero.org.") from exc
        except httpx.HTTPError as exc:
            raise ZoteroError(0, f"Could not reach api.zotero.org: {type(exc).__name__}") from exc
        if response.status_code == 200:
            return response.json()
        message = _STATUS_MESSAGES.get(response.status_code)
        if message is None:
            if response.status_code >= 500:
                message = f"Zotero service error (HTTP {response.status_code}). Retry later."
            else:
                message = f"Zotero returned HTTP {response.status_code}."
        raise ZoteroError(response.status_code, message)

    def probe(self) -> None:
        self._get("/items", {"limit": 1})

    def _clamp_limit(self, limit: int) -> int:
        return max(1, min(int(limit or 10), MAX_LIMIT))

    def search_items(
        self,
        query: str,
        *,
        item_type: str | None = None,
        tag: str | None = None,
        limit: int = 10,
        include_abstract: bool = True,
    ) -> list[dict[str, Any]]:
        params: dict[str, Any] = {
            "q": query,
            "limit": self._clamp_limit(limit),
            "itemType": "-attachment",
        }
        if item_type:
            params["itemType"] = item_type
        if tag:
            params["tag"] = tag
        entries = self._get("/items", params)
        return [compact_item(e, include_abstract=include_abstract) for e in entries]

    def get_item(self, item_key: str, *, include_notes: bool = True) -> dict[str, Any]:
        item_key = (item_key or "").strip()
        if not item_key or len(item_key) > MAX_ITEM_KEY or not item_key.isalnum():
            raise ZoteroError(0, "Item key must be the 8-character alphanumeric key from Zotero.")
        entry = self._get(f"/items/{item_key}")
        result = compact_item(entry, include_abstract=True)
        if include_notes:
            children = self._get(f"/items/{item_key}/children")
            notes = [
                strip_html(str(child["data"].get("note", "")))
                for child in children
                if child.get("data", {}).get("itemType") == "note" and child.get("data", {}).get("note")
            ]
            if notes:
                result["notes"] = notes[:10]
        return result

    def list_collections(self, limit: int = 25) -> list[dict[str, Any]]:
        entries = self._get("/collections", {"limit": self._clamp_limit(limit)})
        return [
            {
                "key": e.get("key"),
                "name": (e.get("data") or {}).get("name") or "",
                "numItems": (e.get("meta") or {}).get("numItems"),
                "parent": (e.get("data") or {}).get("parentCollection"),
            }
            for e in entries
        ]

    def get_collection_items(
        self,
        collection_key: str,
        *,
        limit: int = 10,
        include_abstract: bool = True,
    ) -> list[dict[str, Any]]:
        collection_key = (collection_key or "").strip()
        if not collection_key or len(collection_key) > MAX_ITEM_KEY or not collection_key.isalnum():
            raise ZoteroError(0, "Collection key must be the 8-character alphanumeric key from Zotero.")
        entries = self._get(
            f"/collections/{collection_key}/items/top",
            {"limit": self._clamp_limit(limit)},
        )
        return [compact_item(e, include_abstract=include_abstract) for e in entries]
