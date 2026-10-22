from __future__ import annotations

import re
from typing import Any

import httpx

PYPI_URL = "https://pypi.org/pypi"
STATS_URL = "https://pypistats.org/api/packages"
OSV_URL = "https://api.osv.dev/v1/query"
DEFAULT_TIMEOUT = 25.0
MAX_NAME = 200

_NAME_RE = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._-]*$")


class PyPIError(Exception):
    def __init__(self, status: int, message: str) -> None:
        super().__init__(message)
        self.status = status
        self.message = message


def normalize_name(name: str) -> str:
    """PyPI treats case, dots, dashes and underscores as equivalent."""
    value = (name or "").strip()
    if not value or len(value) > MAX_NAME or not _NAME_RE.match(value):
        raise PyPIError(0, "Package name must be 1-200 characters of letters, digits, '.', '_' or '-'.")
    return re.sub(r"[-_.]+", "-", value).lower()


class PyPIClient:
    """Read-only client for PyPI, pypistats and OSV (no credentials)."""

    def __init__(self, timeout: float = DEFAULT_TIMEOUT) -> None:
        self._client = httpx.Client(
            timeout=timeout,
            headers={"Accept": "application/json", "User-Agent": "dify-pypi-intel-plugin/0.0.1"},
            follow_redirects=True,
        )

    def __enter__(self) -> "PyPIClient":
        return self

    def __exit__(self, *_exc: object) -> None:
        self._client.close()

    def _request(self, method: str, url: str, **kwargs: Any) -> Any:
        try:
            response = self._client.request(method, url, **kwargs)
        except httpx.TimeoutException as exc:
            raise PyPIError(0, "Timed out talking to the package index.") from exc
        except httpx.HTTPError as exc:
            raise PyPIError(0, f"Could not reach the package index: {type(exc).__name__}") from exc
        if response.status_code == 200:
            return response.json()
        if response.status_code == 404:
            raise PyPIError(404, "Package not found. Check the name, or the package may be unpublished.")
        if response.status_code == 429:
            raise PyPIError(429, "The package index is rate limiting requests. Retry shortly.")
        raise PyPIError(response.status_code, f"The package index returned HTTP {response.status_code}.")

    def package_json(self, name: str) -> dict[str, Any]:
        return self._request("GET", f"{PYPI_URL}/{normalize_name(name)}/json")

    def info(self, name: str) -> dict[str, Any]:
        payload = self.package_json(name)
        info = payload.get("info") or {}
        releases = payload.get("releases") or {}
        latest = info.get("version") or ""
        files = releases.get(latest) or []
        uploaded = files[0].get("upload_time_iso_8601") if files else None
        return {
            "name": info.get("name") or name,
            "version": latest,
            "summary": info.get("summary") or "",
            "license": (info.get("license_expression") or info.get("license") or "")[:200],
            "requires_python": info.get("requires_python") or "",
            "home_page": info.get("home_page") or (info.get("project_urls") or {}).get("Homepage") or "",
            "author": info.get("author") or "",
            "yanked": bool(info.get("yanked")),
            "release_count": len(releases),
            "latest_uploaded_at": uploaded,
            "requires_dist": (info.get("requires_dist") or [])[:30],
        }

    def releases(self, name: str, *, include_prereleases: bool = False, limit: int = 10) -> list[dict[str, Any]]:
        payload = self.package_json(name)
        releases = payload.get("releases") or {}
        rows: list[dict[str, Any]] = []
        for version, files in releases.items():
            if not files:
                continue
            first = files[0]
            if first.get("yanked"):
                continue
            if not include_prereleases and _is_prerelease(version):
                continue
            rows.append(
                {
                    "version": version,
                    "uploaded_at": first.get("upload_time_iso_8601"),
                    "requires_python": first.get("requires_python") or "",
                }
            )
        rows.sort(key=lambda row: row.get("uploaded_at") or "", reverse=True)
        return rows[: max(1, min(int(limit or 10), 50))]

    def downloads(self, name: str) -> dict[str, Any]:
        payload = self._request("GET", f"{STATS_URL}/{normalize_name(name)}/recent")
        data = payload.get("data") or {}
        return {
            "last_day": data.get("last_day"),
            "last_week": data.get("last_week"),
            "last_month": data.get("last_month"),
        }

    def vulnerabilities(self, name: str, version: str | None = None) -> dict[str, Any]:
        package_name = normalize_name(name)
        resolved = (version or "").strip()
        if not resolved:
            resolved = str((self.package_json(package_name).get("info") or {}).get("version") or "")
        if not resolved:
            raise PyPIError(0, "Could not determine the version to query.")
        payload = self._request(
            "POST",
            OSV_URL,
            json={"package": {"name": package_name, "ecosystem": "PyPI"}, "version": resolved},
        )
        vulns = []
        for item in payload.get("vulns") or []:
            vulns.append(
                {
                    "id": item.get("id"),
                    "aliases": (item.get("aliases") or [])[:5],
                    "summary": (item.get("summary") or "")[:300],
                    "severity": _severity(item),
                    "published": item.get("published"),
                    "fixed_versions": _fixed_versions(item),
                }
            )
        return {"package": package_name, "version": resolved, "count": len(vulns), "vulnerabilities": vulns}


def _is_prerelease(version: str) -> bool:
    return bool(re.search(r"(a|b|rc|dev|alpha|beta)\d*$", version, re.IGNORECASE))


def _severity(item: dict[str, Any]) -> str:
    for entry in item.get("severity") or []:
        if entry.get("type") == "CVSS_V3" and entry.get("score"):
            return str(entry["score"])
    database = item.get("database_specific") or {}
    return str(database.get("severity") or "")


def _fixed_versions(item: dict[str, Any]) -> list[str]:
    fixed: list[str] = []
    for affected in item.get("affected") or []:
        for rng in affected.get("ranges") or []:
            for event in rng.get("events") or []:
                if event.get("fixed"):
                    fixed.append(str(event["fixed"]))
    return sorted(set(fixed))[:5]
