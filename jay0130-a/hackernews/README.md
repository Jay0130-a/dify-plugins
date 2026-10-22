# Hacker News

Read Hacker News from Dify agents — **no API key, no setup**. Search stories and comments, read a discussion with its top comments, pull the front page, or look up a user.

## Tools

| Tool | What it does |
|---|---|
| `hn_search` | Full-text search over stories and comments (relevance or newest first), with optional tag / minimum-points / recency filters. |
| `hn_get_story` | One story plus its top comments as plain text, optionally one level of replies. |
| `hn_top_stories` | The current front page: `top`, `best`, `new`, `ask`, `show`, or `job`. |
| `hn_user` | A user's karma, join date, about text, and recent submissions. |

Typical flow: `hn_top_stories` → `hn_get_story` to read the discussion, or `hn_search` → `hn_get_story`.

## Setup

None. The plugin talks only to two public, documented endpoints:

- `hn.algolia.com` — Algolia's public Hacker News search index.
- `hacker-news.firebaseio.com` — the official Hacker News API.

It is read-only: it never posts, votes, or writes anything, and it stores no data.

## Examples

The agent calls `hn_top_stories(list="top", limit=10)`, then `hn_get_story(story_id=..., max_comments=10)` for the chosen items, and summarises the plain-text comments.

`hn_search(query="local llm inference", min_points=100, max_age_days=7, tags="story")`.

## Privacy

See [PRIVACY.md](PRIVACY.md): no credentials, no storage, two fixed public hosts, GET only.

## Source repository

<https://github.com/Jay0130-a/dify-plugins> (see `jay0130-a/hackernews` on the plugin branch).
