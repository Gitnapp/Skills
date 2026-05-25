---
name: xiaohongshu-search
description: "Search Xiaohongshu notes and parse full note content via TikHub APIs. Two-step workflow: search, pick note_id, fetch detail body."
version: 1.1.0
author: Hermes Agent
license: Private
metadata:
  hermes:
    tags: [xiaohongshu, 小红书, social-search, community-research, api, tikhub]
    related_skills: [tikhub-community-search]
  requires_env: [TIKHUB_API_KEY]
  source: "https://docs.tikhub.io"
---

# 小红书搜索 & 正文解析 Skill

两阶段流程：**先搜索**获取标题/摘要/note_id → **再解析**拉取完整正文。

## 文件

```
xiaohongshu-search-skill/
├── SKILL.md          — 本文档
├── README.md         — 快速使用说明
├── scripts/
│   ├── xhs.py        — 搜索和正文解析 CLI
│   └── .env.local    — API key（mode 0600）
└── references/
```

Base URL: `https://api.tikhub.io`
Auth: `Authorization: Bearer $TIKHUB_API_KEY`
Pricing: ~$0.001/call; non-200 not charged. Cache 24h via `cache_url`.

## 快速使用

```bash
cd ~/Desktop/eric-skills/cat-search/xiaohongshu-search-skill

# 搜索
python3 scripts/xhs.py search "关键词" --limit 10
python3 scripts/xhs.py search "GPT Pro" --sort time_descending --limit 5

# 获取正文
python3 scripts/xhs.py detail <note_id>
python3 scripts/xhs.py detail-from-url "https://www.xiaohongshu.com/explore/..."
```

## 两阶段工作流

### Phase 1: 搜索 — 拿标题/摘要/note_id

搜索 API 返回的 `desc` 字段是**截断预览**（~50-300 字），**不是全文**。只能用来筛选哪些笔记值得看正文。

**搜索参数：**

| 参数 | 类型 | 说明 |
|------|------|------|
| keyword | string (必填) | 搜索关键词 |
| page | int (默认 1) | 页码（从1开始） |
| sort_type | general / time_descending | 综合 / 最新 |
| note_type | 0 / 1 / 2 | 0=不限 1=图文 2=视频 |
| time_filter | 0 / 1 / 2 / 3 | 0=不限 1=一天内 2=一周 3=半年 |

**Response 结构（搜索笔记）:**

```
response.data.data.items[i].note
  .id              — note_id（用于 Phase 2；是 .id 不是 .note_id）
  .title           — 标题
  .desc            — 截断预览（不是全文！）
  .user.nickname   — 作者昵称
  .liked_count / .comments_count / .collected_count / .shared_count
  .last_update_time / .timestamp
```

分享 URL 用 `https://www.xiaohongshu.com/explore/{id}` 拼（`.share_url` 常为空）。

### Phase 2: 解析正文 — 拿完整内容

用 Phase 1 拿到的 note_id 调详情接口。**App V2 接口不需要 xsec_token**，这是相对 Web V3 的核心优势。

顺序：先试 `get_image_note_detail`，类型不对则 fallback 到 `get_video_note_detail`。

**Response 结构（笔记详情）:**

```
response.data.data[i].note_list[0]
  .desc            — 完整正文（已验证可到 800+ 字）
  .title           — 标题
  .user.nickname   — 作者
  .ip_location     — 发布位置
  .liked_count / .comments_count / .collected_count / .shared_count
  .image_list[].url_size_large — 高清大图 URL
  .time            — 发布时间戳
```

### 翻页

```python
# 搜索第1页：
GET /api/v1/xiaohongshu/app_v2/search_notes?keyword=xxx&page=1
# 从响应获取 search_id, search_session_id
# 搜索第2页：
GET /api/v1/xiaohongshu/app_v2/search_notes?keyword=xxx&page=2&search_id=xxx&search_session_id=xxx
```

## 关键对比：搜索 desc 截断 vs 详情 desc 完整

| 特性 | 搜索 API (search_notes) | 详情 API (get_image_note_detail) |
|------|-------------------------|----------------------------------|
| desc 长度 | 截断 ~100-300 字 | 完整全文 |
| xsec_token | 不需要 | 不需要 |
| 费用 | $0.001/次 | $0.001/次 |
| 图片 | 压缩封面 | 高清大图 |
| IP 位置 | 无 | 有 |
| 缓存 | 24h | 24h |

## CLI 用法

### 搜索笔记

```bash
python3 scripts/xhs.py search --keyword "深圳美食" --page 1
```

参数：
- `--keyword` (必填) 搜索关键词
- `--page` 页码 (从1开始)
- `--sort-type` 排序: `general`(综合) / `time_descending`(最新)
- `--note-type` 类型: `不限` / `video` / `image`
- `--time-filter` 时间: `不限` / `one_day` / `one_week` / `one_month` / `three_months`
- `--limit` 返回条数
- `--raw` 输出完整 JSON

### 获取图文笔记详情

```bash
python3 scripts/xhs.py get-image-note --note-id 690f31f500000000030102e7
# 或通过分享链接
python3 scripts/xhs.py get-image-note --share-text "http://xhslink.com/o/xxx"
```

### 获取视频笔记详情

```bash
python3 scripts/xhs.py get-video-note --note-id 697c0eee000000000a03c308
```

### 原始 JSON 输出

所有命令支持 `--raw` 参数输出完整 JSON。

## API Endpoints

| 功能 | 方法 | 端点 |
|------|------|------|
| 搜索笔记 | GET | `/api/v1/xiaohongshu/app_v2/search_notes` |
| 搜索用户 | GET | `/api/v1/xiaohongshu/app_v2/search_users` |
| 图文笔记详情 | GET | `/api/v1/xiaohongshu/app_v2/get_image_note_detail` |
| 视频笔记详情 | GET | `/api/v1/xiaohongshu/app_v2/get_video_note_detail` |
| 热搜词 | GET | `/api/v1/xiaohongshu/web_v3/fetch_trending` |

## API Discipline

- 每次调用 $0.001
- QPS 限制 10/s
- 先搜索（1 次）筛选，再解析 Top 3-5（3-5 次），总共 $0.004~$0.006/轮
- TikHub 会缓存 24 小时（见响应中的 `cache_url`），重复访问不扣费
- 不要打印 API key
- `urllib` 会被 Cloudflare 封禁，脚本已设置浏览器 User-Agent 绕过

## Pitfalls

1. **搜索 desc 是截断的** — 不要以为搜索结果的 desc 是全文。要完整正文必须调详情接口
2. **note_id 必须是 App V2 格式**（纯数字或字母组合如 `6a0e8d910000000035031f95`），不是 URL 参数。
   用 `.id`（不是 `.note_id`，后者常为空）
3. **视频笔记用 get_video_note_detail**，图文用 get_image_note_detail — 不确定时先试 image，自动 fallback
4. `share_text` 支持 APP 和 Web 分享链接，但 `note_id` 优先
5. 响应结构嵌套较深：`data.data.items[i].note`（搜索）和 `data.data[i]`（详情）

## Verification Checklist

- [ ] 搜索返回预期数量的结果
- [ ] 详情接口返回了完整的 desc（对比搜索摘要确认完整度）
- [ ] 互动数据（👍💬⭐）与搜索接口一致
- [ ] note_id 或 share_text 正确传递
