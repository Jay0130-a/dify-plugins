# Privacy Policy

## What this plugin sends

This plugin requires **no credentials** and collects no personal data. It
contacts three fixed public hosts:

- `pypi.org` — the official PyPI JSON API, receiving only the package name
  being looked up.
- `pypistats.org` — public download statistics, receiving only the package name.
- `api.osv.dev` — the Open Source Vulnerabilities database, receiving the
  package name, its ecosystem (`PyPI`), and an optional version to query.

No user data, conversation content, or credentials are transmitted, because the
plugin has none.

## What this plugin stores

Nothing. There is no database, cache file, or log file.

## What this plugin does not do

- It never publishes, modifies, or deletes anything on PyPI or OSV. The OSV
  request is a `POST /v1/query` read-only lookup; no state is written.
- It never executes code, installs packages, or resolves dependencies.
- It contacts no host other than the three listed above.

## Third parties

PyPI (Python Software Foundation), pypistats.org, and Google's OSV database are
the only third parties receiving requests.
