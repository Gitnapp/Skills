---
name: tikhub-xiaohongshu
description: "TikHub 小红书 API — 搜索笔记/用户，获取图文/视频笔记详情。Xiaohongshu (Little Red Book) search & content retrieval via TikHub."
version: 1.0.0
author: Hermes Agent
metadata:
  requires_env: ["TIKHUB_API_KEY"]
  source: "https://docs.tikhub.io"
---

# TikHub 小红书 API

通过 TikHub API 搜索小红书笔记/用户和获取笔记内容详情。

## Setup

已在 `.env` 配置好 `TIKHUB_API_KEY`。

Script: `~/.hermes/scripts/tikhub_xhs.py`

## Usage

### 搜索笔记
```bash
python ~/.hermes/scripts/tikhub_xhs.py search-notes --keyword "深圳美食" --page 1
```

参数：
- `--keyword` (必填) 搜索关键词
- `--page` 页码 (从1开始)
- `--sort-type` 排序: `general`(综合) / `most_popular` / `latest` / `most_commented`
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

- 所有成功的 API 请求**都会计费**
- 响应使用 Bearer Token 认证
- 图文/视频笔记详情的 `note-id` 可以从搜索结果的 Note ID 字段获取
- 响应支持缓存（24小时有效），访问缓存不计费
- API 优先使用 App V2 接口（最稳定推荐）
- `urllib` 会被 Cloudflare 封禁，脚本已设置浏览器 User-Agent 绕过
- 脚本独立运行时自动从 `~/.hermes/.env` 回退读取 API key
- 更多已知问题和 API 响应结构见 `references/known-issues.md`

## API Endpoints

| 功能 | 方法 | 端点 |
|------|------|------|
| 搜索笔记 | GET | `/api/v1/xiaohongshu/app_v2/search_notes` |
| 搜索用户 | GET | `/api/v1/xiaohongshu/app_v2/search_users` |
| 图文笔记详情 | GET | `/api/v1/xiaohongshu/app_v2/get_image_note_detail` |
| 视频笔记详情 | GET | `/api/v1/xiaohongshu/app_v2/get_video_note_detail` |
