# Hacker News

Read Hacker News from Dify agents — **no API key, no setup**. Search stories and comments, read a discussion with its top comments, pull the front page, or look up a user.

> 无需任何 API Key 即可在 Dify 中检索和阅读 Hacker News：搜索故事与评论、读取讨论及热门评论、拉取首页榜单、查看用户主页。

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

> "今天 Hacker News 首页有什么值得看的？挑三条并总结评论里的主要观点。"

The agent calls `hn_top_stories(list="top", limit=10)`, then `hn_get_story(story_id=..., max_comments=10)` for the chosen items, and summarises the plain-text comments.

> "Hacker News 上最近一周关于 local LLM inference 的讨论，只要 100 分以上的。"

`hn_search(query="local llm inference", min_points=100, max_age_days=7, tags="story")`.

## Privacy

See [PRIVACY.md](PRIVACY.md): no credentials, no storage, two fixed public hosts, GET only.

## Source repository

<https://github.com/Jay0130-a/dify-plugins> (see `jay0130-a/hackernews` on the plugin branch).

---

## 中文说明

**工具**

- `hn_search`：在故事与评论中全文检索（按相关性或最新排序），可限定标签、最低分数、时间范围。
- `hn_get_story`：读取一条故事及其热门评论（纯文本），可选包含一层回复。
- `hn_top_stories`：读取首页榜单（top / best / new / ask / show / job）。
- `hn_user`：查看用户的 karma、注册时间、简介与最近提交。

**配置**：无需任何配置。插件只访问 `hn.algolia.com`（公开搜索索引）与 `hacker-news.firebaseio.com`（官方 API），全部为只读 GET 请求，不发布、不点赞、不写任何内容，也不存储数据。

**示例**：让 Agent「看看今天 HN 首页有什么值得看的，挑三条并总结评论区观点」，它会先调 `hn_top_stories`，再对选中的条目调 `hn_get_story` 读取评论并总结。
