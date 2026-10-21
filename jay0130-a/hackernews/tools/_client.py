from __future__ import annotations

import re
from typing import Any
from xml.sax.saxutils import unescape

import httpx

ALGOLIA_URL = "https://hn.algolia.com/api/v1"
FIREBASE_URL = "https://hacker-news.firebaseio.com/v0"
DEFAULT_TIMEOUT = 25.0
MAX_LIMIT = 50

_TAG_RE = re.compile(r"<[^>]+>")
_WS_RE = re.compile(r"\s+")
_STORY_TAGS = {"story", "show_hn", "ask_hn", "job", "poll"}


class HackerNewsError(Exception):
    def __init__(self, status: int, message: str) -> None:
        super().__init__(message)
        self.status = status
        self.message = message


def strip_html(text: str | None) -> str:
    if not text:
        return ""
    return _WS_RE.sub(" ", unescape(_TAG_RE.sub(" ", text))).strip()


def story_url(item_id: int | None) -> str:
    return f"https://news.ycombinator.com/item?id={item_id}" if item_id else ""


def compact_hit(hit: dict[str, Any]) -> dict[str, Any]:
    """Normalize an Algolia hit (story or comment) into a small record."""
    object_id = hit.get("objectID")
    try:
        numeric_id = int(object_id) if object_id is not None else None
    except (TypeError, ValueError):
        numeric_id = None
    title = hit.get("title") or hit.get("story_title") or ""
    return {
        "id": numeric_id,
        "type": "comment" if hit.get("comment_text") else "story",
        "title": title,
        "url": hit.get("url") or story_url(numeric_id),
        "hn_url": story_url(numeric_id),
        "author": hit.get("author") or "",
        "points": hit.get("points"),
        "num_comments": hit.get("num_comments"),
        "created_at": hit.get("created_at") or "",
        "text": strip_html(hit.get("comment_text") or hit.get("story_text"))[:1200],
    }


class HackerNewsClient:
    """Read-only client for Algolia HN search and the official Firebase API."""

    def __init__(self, timeout: float = DEFAULT_TIMEOUT) -> None:
        self._client = httpx.Client(
            timeout=timeout,
            headers={"Accept": "application/json", "User-Agent": "dify-hackernews-plugin/0.0.1"},
            follow_redirects=True,
        )

    def __enter__(self) -> "HackerNewsClient":
        return self

    def __exit__(self, *_exc: object) -> None:
        self._client.close()

    def _get(self, url: str, params: dict[str, Any] | None = None) -> Any:
        try:
            response = self._client.get(url, params=params)
        except httpx.TimeoutException as exc:
            raise HackerNewsError(0, "Timed out talking to Hacker News.") from exc
        except httpx.HTTPError as exc:
            raise HackerNewsError(0, f"Could not reach Hacker News: {type(exc).__name__}") from exc
        if response.status_code == 200:
            return response.json()
        if response.status_code == 404:
            raise HackerNewsError(404, "Not found on Hacker News.")
        if response.status_code == 429:
            raise HackerNewsError(429, "Hacker News is rate limiting requests. Retry shortly.")
        raise HackerNewsError(response.status_code, f"Hacker News returned HTTP {response.status_code}.")

    @staticmethod
    def _clamp(limit: int, default: int = 10) -> int:
        try:
            return max(1, min(int(limit or default), MAX_LIMIT))
        except (TypeError, ValueError):
            return default

    def search(
        self,
        query: str,
        *,
        search_type: str = "relevance",
        tags: str | None = None,
        min_points: int | None = None,
        max_age_days: int | None = None,
        limit: int = 10,
    ) -> list[dict[str, Any]]:
        endpoint = "/search_by_date" if search_type == "date" else "/search"
        params: dict[str, Any] = {"query": query, "hitsPerPage": self._clamp(limit), "tags": tags or "(story,comment)"}
        filters: list[str] = []
        if min_points:
            filters.append(f"points>={int(min_points)}")
        if max_age_days:
            filters.append(f"created_at_i>{int(max_age_days) * 86400}")
        if filters:
            params["numericFilters"] = ",".join(filters)
        payload = self._get(f"{ALGOLIA_URL}{endpoint}", params)
        return [compact_hit(hit) for hit in payload.get("hits", [])]

    def get_item(self, item_id: int) -> dict[str, Any]:
        return self._get(f"{FIREBASE_URL}/item/{int(item_id)}.json") or {}

    def get_story(self, item_id: int, *, max_comments: int = 10, comment_depth: int = 1) -> dict[str, Any]:
        item = self.get_item(item_id)
        if not item:
            raise HackerNewsError(404, f"Story {item_id} was not found on Hacker News.")
        comments = self._collect_comments(item.get("kids") or [], max_comments=max_comments, depth=comment_depth)
        return {
            "id": item.get("id"),
            "title": item.get("title") or "",
            "url": item.get("url") or story_url(item.get("id")),
            "hn_url": story_url(item.get("id")),
            "author": item.get("by") or "",
            "points": item.get("score"),
            "num_comments": item.get("descendants"),
            "created_at": _ts(item.get("time")),
            "text": strip_html(item.get("text")),
            "comments": comments,
        }

    def _collect_comments(self, kids: list[int], *, max_comments: int, depth: int) -> list[dict[str, Any]]:
        collected: list[dict[str, Any]] = []
        for kid in kids:
            if len(collected) >= max_comments:
                break
            child = self.get_item(kid)
            if not child or child.get("deleted") or child.get("dead"):
                continue
            entry = {
                "id": child.get("id"),
                "author": child.get("by") or "",
                "points": child.get("score"),
                "created_at": _ts(child.get("time")),
                "text": strip_html(child.get("text")),
            }
            if depth > 1:
                entry["replies"] = self._collect_comments(
                    child.get("kids") or [],
                    max_comments=max(1, max_comments - len(collected)),
                    depth=depth - 1,
                )
            collected.append(entry)
        return collected

    def list_stories(self, list_name: str = "top", limit: int = 10) -> list[dict[str, Any]]:
        name = list_name if list_name in {"top", "best", "new", "ask", "show", "job"} else "top"
        ids = self._get(f"{FIREBASE_URL}/{name}stories.json") or []
        stories = []
        for item_id in ids[: self._clamp(limit)]:
            item = self.get_item(item_id)
            if not item:
                continue
            stories.append(
                {
                    "id": item.get("id"),
                    "title": item.get("title") or "",
                    "url": item.get("url") or story_url(item.get("id")),
                    "hn_url": story_url(item.get("id")),
                    "author": item.get("by") or "",
                    "points": item.get("score"),
                    "num_comments": item.get("descendants"),
                    "created_at": _ts(item.get("time")),
                }
            )
        return stories

    def get_user(self, username: str, *, recent: int = 5) -> dict[str, Any]:
        user = self._get(f"{FIREBASE_URL}/user/{username}.json")
        if not user:
            raise HackerNewsError(404, f"Hacker News user {username!r} was not found.")
        submissions = []
        for item_id in (user.get("submitted") or [])[: max(0, min(int(recent or 0), 10))]:
            item = self.get_item(item_id)
            if not item:
                continue
            submissions.append(
                {
                    "id": item.get("id"),
                    "type": item.get("type"),
                    "title": item.get("title") or "",
                    "url": item.get("url") or story_url(item.get("id")),
                    "points": item.get("score"),
                    "created_at": _ts(item.get("time")),
                }
            )
        return {
            "id": user.get("id"),
            "karma": user.get("karma"),
            "created_at": _ts(user.get("created")),
            "about": strip_html(user.get("about")),
            "submissions": submissions,
        }


def _ts(value: Any) -> str:
    import datetime as _dt

    try:
        return _dt.datetime.fromtimestamp(int(value), tz=_dt.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    except (TypeError, ValueError, OSError):
        return ""
