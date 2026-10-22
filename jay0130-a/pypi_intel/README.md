# PyPI Package Intel

Dependency intelligence for Python packages — **no API key, no setup**. Check a package's latest metadata, release history, download counts, and known vulnerabilities before an agent adds, pins, or upgrades a dependency.

## Tools

| Tool | What it does |
|---|---|
| `pypi_package_info` | Latest version, summary, license, `requires-python`, homepage, yanked status, release count, upload date, declared dependencies. |
| `pypi_release_history` | Recent releases with upload dates, newest first; optionally include pre-releases. |
| `pypi_downloads` | Download counts for the last day / week / month (pypistats.org). |
| `pypi_vulnerabilities` | Known advisories from the OSV database for a package at a version (or its latest), with severity and fixed versions. |

Typical flow for a coding agent: `pypi_package_info` → `pypi_vulnerabilities` before adding a dependency; `pypi_release_history` + `pypi_downloads` when choosing between competing libraries.

## Setup

None. There are no credentials to configure. The plugin talks to three public, documented endpoints:

- `pypi.org` — the official PyPI JSON API (package metadata and releases).
- `pypistats.org` — public download statistics.
- `api.osv.dev` — the Open Source Vulnerabilities database (read-only query).

All requests are lookups: the plugin never publishes, modifies, installs, or resolves anything, and it stores no data.

## Examples

> "I want to add requests to the project — check the latest version and any known vulnerabilities first."

The agent calls `pypi_package_info(package="requests")` and `pypi_vulnerabilities(package="requests")`, then summarises the version, license, and any advisories with the versions that fix them.

> "Should I use pydantic or dataclasses-json? Compare maintenance activity and adoption."

`pypi_release_history(package="pydantic", limit=5)` + `pypi_downloads(package="pydantic")` for both packages.

## Privacy

See [PRIVACY.md](PRIVACY.md): no credentials, no storage, three fixed public hosts, lookup requests only.

## Source repository

<https://github.com/Jay0130-a/dify-plugins> (see `jay0130-a/pypi_intel` on the plugin branch).

Localized documentation: [README.zh_Hans.md](README.zh_Hans.md)
