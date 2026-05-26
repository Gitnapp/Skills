# Source Coverage

已读取/抓取来源：
- https://docs.tikhub.io/llms.txt：索引到 1259 个 Markdown 文档链接，API Docs 行 1107 条，分组 54 个。
- https://api.tikhub.io/openapi.json：完整 OpenAPI，1123 条 paths，54 个 tags；这是生成 endpoint catalog 的主来源。
- docs.tikhub.io 单页 Markdown：成功抓取 1218/1259；其中部分 docs.tikhub.io/*.md 对非浏览器请求返回 HTML/WAF，但 OpenAPI 覆盖了这些 endpoints。
- 已用用户提供的 TikHub API key 调用 /api/v1/health/check 与 /api/v1/tikhub/user/get_user_info 验证：HTTP 200，key 可用；原始 key 未写入本文档。

生成文件：
- references/endpoint-catalog.json：全部 OpenAPI endpoints（1123）。
- references/community-search-endpoints.json：按社区经验搜索/发现/评论/推荐/榜单/用户/内容相关关键词筛出的候选 endpoints（1054）。
- references/supported-platforms.md/json：所有支持平台和分组汇总。

注意：TikHub 文档持续更新；使用前优先运行 scripts/tikhub_search.py refresh-openapi 重新拉取最新 OpenAPI。
