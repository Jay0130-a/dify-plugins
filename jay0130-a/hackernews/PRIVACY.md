# Privacy Policy

## What this plugin sends

This plugin requires **no credentials** and collects no personal data. Every
request is a read-only `GET` to one of two fixed public hosts:

- `hn.algolia.com` — full-text search over Hacker News (Algolia's public
  search API), receiving only the query terms and filters the agent passes.
- `hacker-news.firebaseio.com` — the official Hacker News API, receiving only
  item, user, and list identifiers.

## What this plugin stores

Nothing. There is no database, cache file, or log file, and there are no
credentials to store.

## What this plugin does not do

- It never posts, votes, or writes anything to Hacker News.
- It never executes code, commands, or SQL.
- It contacts no host other than the two listed above.

## Third parties

Algolia (search index) and the Hacker News API (Y Combinator) are the only
third parties receiving requests.
