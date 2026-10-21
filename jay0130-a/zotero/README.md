# Zotero Library

Read-only access to a [Zotero](https://www.zotero.org/) library for Dify agents, through the official Zotero Web API (`api.zotero.org`).

> 只读访问 Zotero 文献库的 Dify 工具插件：检索文献、查看条目详情与批注笔记、浏览分类。详见下方中文说明。

## Tools

| Tool | What it does |
|---|---|
| `zotero_search_items` | Keyword search across title, creator, year, and abstract; returns compact metadata (key, type, title, creators, date, tags, DOI/URL, abstract). |
| `zotero_get_item` | Full metadata for one item by its 8-character key, including the plain text of child notes (your annotations). |
| `zotero_list_collections` | List the library's collections (folders) with their keys and item counts. |
| `zotero_get_collection_items` | List the top-level items of one collection. |

Typical agent flow: `zotero_list_collections` → `zotero_get_collection_items` → `zotero_get_item` (to read an item's abstract and your notes), or `zotero_search_items` → `zotero_get_item`.

## Setup

1. Decide the library scope:
   - **My library (user)**: your personal library. Requires an API key.
   - **Group library**: a Zotero group. Public groups can be read **without any key**.
2. Find the numeric **Library ID**:
   - User library: `https://www.zotero.org/settings/keys` → "Your ID for use in API calls".
   - Group library: the numeric ID in the group page URL (`https://www.zotero.org/groups/<id>/...`).
3. If a key is needed, create one at `https://www.zotero.org/settings/keys` with **read** access (library permissions), then paste it into the plugin credentials.

No other configuration is required. The plugin has exactly two dependencies (`dify_plugin`, `httpx`) and only ever performs HTTP `GET` requests against the single fixed host `api.zotero.org`.

## Example

With a public group library configured (no key), asking the agent:

> "帮我在 Zotero 里找关于 transformer attention 的文献，并给出第一条的摘要"

runs `zotero_search_items(query="transformer attention")`, then `zotero_get_item(key=...)` for the abstract.

## Privacy

See [PRIVACY.md](PRIVACY.md). In short: the plugin sends only the library scope, search queries / keys, and (if configured) the API key to `api.zotero.org`; it stores nothing, logs nothing, and performs no writes.

## Source repository

<https://github.com/Jay0130-a/dify-plugins> (see `jay0130-a/zotero` on the plugin branch).

---

## 中文说明（Zotero 文献库）

只读访问 [Zotero](https://www.zotero.org/) 文献库的 Dify 工具插件，走官方 Zotero Web API（`api.zotero.org`）。

**工具一览**

- `zotero_search_items`：按关键词检索文献（标题、作者、年份、摘要），返回紧凑元数据。
- `zotero_get_item`：按 8 位 key 查看条目完整元数据，可附带子笔记（你的批注）纯文本。
- `zotero_list_collections`：列出库中的分类及条目数。
- `zotero_get_collection_items`：浏览某个分类下的顶层条目。

**配置**

1. 选择库类型：个人库（需要 API Key）或小组库（公开小组无需 Key）。
2. 填数字库 ID：个人库在 `https://www.zotero.org/settings/keys` 页面的 "Your ID for use in API calls"；小组库用小组页面 URL 里的数字 ID。
3. 需要时在同页面创建只读 API Key 并粘贴。

依赖仅 `dify_plugin` 与 `httpx`；只对固定主机 `api.zotero.org` 发起 HTTP GET 请求，不做任何写操作，不存储、不记录任何数据。
