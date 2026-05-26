## [2026-05-21] 创建 TikHub 社区经验搜索 Skill

**改动文件：**
- `SKILL.md` — 定义 TikHub 社区经验搜索流程、平台支持、API 使用纪律和验证清单
- `README.md` — 添加本地使用与安装说明
- `scripts/tikhub_search.py` — 添加 stdlib-only 的 endpoint 搜索、平台列表和 API 调用助手
- `scripts/.env.local` — 保存本地 TikHub API key 配置，权限为 0600
- `references/endpoint-catalog.json` — 从 TikHub OpenAPI 生成完整 endpoint catalog
- `references/community-search-endpoints.json` — 生成社区搜索/发现/评论/推荐相关 endpoint 子集
- `references/supported-platforms.md` / `references/supported-platforms.json` — 汇总所有支持平台、API tags 与 endpoint 数量
- `references/openapi-summary.json` / `references/source-coverage.md` — 记录文档来源、覆盖范围和验证结果

**变更说明：**
基于 docs.tikhub.io 的 llms.txt、单页 Markdown 和 api.tikhub.io/openapi.json 构建一个可移植 Hermes skill，用于跨平台社区经验搜索。OpenAPI 作为完整机器可读来源，补足部分 docs Markdown 被 WAF/HTML 响应影响的问题。

**影响范围：**
Agent Prompt / Skill / API Research
