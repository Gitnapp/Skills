---
name: tikhub-xiaohongshu
description: "TikHub 小红书 API — 搜索笔记/用户，获取图文/视频笔记详情。Xiaohongshu (Little Red Book) search & content retrieval via TikHub."
version: 1.1.0
author: Hermes Agent
metadata:
  requires_env: ["TIKHUB_API_KEY"]
  source: "https://docs.tikhub.io"
---

# TikHub 小红书 API

通过 TikHub API 搜索小红书笔记/用户和获取笔记内容详情。

## Setup

已在 `.env` 配置好 `TIKHUB_API_KEY`。

Base URL: `https://api.tikhub.io` (global) / `https://api.tikhub.dev` (mainland China).
Auth: `Authorization: Bearer $TIKHUB_API_KEY`
Pricing: ~$0.001/call; non-200 not charged. Cache 24h via `cache_url`.

Script: `~/.hermes/scripts/tikhub_xhs.py`

## Two-Phase Workflow (搜索 + 解析正文)

### Phase 1: 搜索 — 拿标题/摘要/note_id

搜索 API 返回的 `desc` 字段是**截断预览**（~50-300 字），**不是全文**。只能用来筛选哪些笔记值得看正文。

**Response 结构**（搜索笔记 `search_notes`）:
```
response.data.data.items[i].note
  .id              — note_id（用于 Phase 2；注意是 `.id` 不是 `.note_id`）
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

**Response 结构**（笔记详情）:
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

## Critical: 搜索 desc 截断 vs 详情 desc 完整

| 特性 | 搜索 API (search_notes) | 详情 API (get_image_note_detail) |
|------|-------------------------|----------------------------------|
| desc 长度 | 截断 ~100-300 字 | 完整全文 |
| xsec_token | 不需要 | 不需要 |
| 费用 | $0.001/次 | $0.001/次 |
| 图片 | 压缩封面 | 高清大图 |
| IP 位置 | 无 | 有 |
| 缓存 | 24h | 24h |

## Usage

### 搜索笔记
```bash
python ~/.hermes/scripts/tikhub_xhs.py search-notes --keyword "深圳美食" --page 1
```

参数：
- `--keyword` (必填) 搜索关键词
- `--page` 页码 (从1开始)
- `--sort-type` 排序: `general`(综合) / `time_descending`(最新)
- `--note-type` 类型: `不限` / `video` / `image`
- `--time-filter` 时间: `不限` / `one_day` / `one_week` / `one_month` / `three_months`

### 搜索用户
```bash
python ~/.hermes/scripts/tikhub_xhs.py search-users --keyword "美食博主" --page 1
```

### 获取图文笔记详情
```bash
python ~/.hermes/scripts/tikhub_xhs.py get-image-note --note-id 690f31f500000000030102e7
# 或通过分享链接
python ~/.hermes/scripts/tikhub_xhs.py get-image-note --share-text "http://xhslink.com/o/xxx"
```

### 获取视频笔记详情
```bash
python ~/.hermes/scripts/tikhub_xhs.py get-video-note --note-id 697c0eee000000000a03c308
```

### 原始 JSON 输出
所有命令支持 `--raw` 参数输出完整 JSON。

## Notes

- 所有成功的 API 请求都会计费（$0.001/次）
- 响应使用 Bearer Token 认证
- 详情接口返回会被 TikHub 缓存 24h，通过 `cache_url` 重复访问不计费
- API 优先使用 App V2 接口（最稳定推荐），不需要 xsec_token
- 先试 `get_image_note_detail`，空结果则试 `get_video_note_detail`，仍失败时回退 App/Web/WebV2
- 搜索的 desc 是截断的：告知用户"desc 被小红书截断，全文需额外调用获取"
- 互动数据用 `.id`（不是 `.note_id`，后者常为空）
- `urllib` 会被 Cloudflare 封禁，脚本已设置浏览器 User-Agent 绕过
- 更多已知问题和 API 响应结构见 `references/known-issues.md`

## API Endpoints

| 功能 | 方法 | 端点 |
|------|------|------|
| 搜索笔记 | GET | `/api/v1/xiaohongshu/app_v2/search_notes` |
| 搜索用户 | GET | `/api/v1/xiaohongshu/app_v2/search_users` |
| 图文笔记详情 | GET | `/api/v1/xiaohongshu/app_v2/get_image_note_detail` |
| 视频笔记详情 | GET | `/api/v1/xiaohongshu/app_v2/get_video_note_detail` |
| 热搜词 | GET | `/api/v1/xiaohongshu/web_v3/fetch_trending` |
