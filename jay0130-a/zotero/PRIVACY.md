# Privacy Policy

## What this plugin sends

Every request goes to the single fixed host `api.zotero.org` over HTTPS. The
plugin sends only what is required to fulfill the requested read operation:

- The configured library scope (`user` or `group`) and its numeric library ID.
- The search query, item key, collection key, and pagination values that the
  agent passes to a tool.
- The configured `Zotero-API-Version: 3` header, and an `Authorization:
  Bearer <api key>` header only when the user configured an API key.

## What this plugin stores

Nothing. There is no database, no cache file, and no log file. Credentials
are held in memory by the Dify plugin runtime for the duration of a request
and are never written to disk, logs, or error messages.

## What this plugin does not do

- It never sends your library data anywhere except `api.zotero.org`.
- It never executes code, commands, or SQL.
- It performs only HTTP `GET` requests; no write operations exist in this plugin.

## Third parties

Zotero (Digital Scholar) is the only third party that receives requests.
Their handling of request data is described in Zotero's own privacy policy.
