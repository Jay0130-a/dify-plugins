# hackernews（中文说明）

**工具**

- `hn_search`：在故事与评论中全文检索（按相关性或最新排序），可限定标签、最低分数、时间范围。
- `hn_get_story`：读取一条故事及其热门评论（纯文本），可选包含一层回复。
- `hn_top_stories`：读取首页榜单（top / best / new / ask / show / job）。
- `hn_user`：查看用户的 karma、注册时间、简介与最近提交。

**配置**：无需任何配置。插件只访问 `hn.algolia.com`（公开搜索索引）与 `hacker-news.firebaseio.com`（官方 API），全部为只读 GET 请求，不发布、不点赞、不写任何内容，也不存储数据。

**示例**：让 Agent「看看今天 HN 首页有什么值得看的，挑三条并总结评论区观点」，它会先调 `hn_top_stories`，再对选中的条目调 `hn_get_story` 读取评论并总结。
