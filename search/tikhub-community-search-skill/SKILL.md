---
name: tikhub-community-search
description: Use when searching community experience, creator/content signals, social comments, topics, trending lists, product/social proof, or public platform data through TikHub APIs across all supported platforms.
version: 1.0.0
author: Hermes Agent
license: Private
metadata:
  hermes:
    tags: [tikhub, social-search, community-research, api, douyin, tiktok, xiaohongshu, bilibili, reddit, youtube]
    related_skills: [website-to-markdown]
---

# TikHub Community Experience Search

## Overview

This skill turns TikHub into a cross-platform community experience search backend. Use it to collect public community signals: search results, notes/posts/videos, comments/replies, creators, hashtags/topics, trending/ranking pages, product/social proof, and platform-specific discovery feeds.

Primary sources read for this skill:

- `https://docs.tikhub.io/llms.txt`
- `https://api.tikhub.io/openapi.json`
- Individual `docs.tikhub.io/*.md` API pages where available
- Live API smoke test with the provided TikHub API key: `/api/v1/health/check` and `/api/v1/tikhub/user/get_user_info` returned HTTP 200

Base URL:

- Global: `https://api.tikhub.io`
- Mainland China optimized domain from docs: `https://api.tikhub.dev`

Auth:

- HTTP Bearer token: `Authorization: Bearer $TIKHUB_API_KEY`
- This portable Desktop skill includes `scripts/.env.local` with the provided key and `0600` permissions. Do not print it, paste it into responses, or commit it.

## When to Use

Use this skill when the user asks for:

- “社区经验搜索”, “用户真实反馈”, “评论区经验”, “达人/创作者内容”, “小红书/抖音/TikTok/Reddit/YouTube 怎么说”
- Cross-platform market/ugc research
- Search result sampling across public social platforms
- Comment/reply mining for pain points, objections, recipes, reviews, troubleshooting, buyer intent, or product usage
- Trending/topic/hashtag/ranking discovery
- Creator or account profile lookup
- Public post/video/note detail extraction

Do not use this skill for:

- Private account data that is not public
- Spam, fake engagement, mass account operations, or policy-violating automation
- Circumventing copyright or platform access controls
- Tasks where a cheaper official API or existing local CLI already answers the question

## Supported Platforms

The OpenAPI catalog contains 1123 paths, 54 API tags, grouped into these platform families:

- 抖音 / Douyin: Web, App V3, Search, Index, Billboard, Creator, Creator V2, Xingtu, Xingtu V2
- TikTok: Web, App V3, Creator, Shop Web, Ads, Analytics, Interaction
- 小红书 / Xiaohongshu: Web, Web V2, Web V3, App, App V2
- Lemon8
- Bilibili: Web, App
- Sora2
- 快手 / Kuaishou: Web, App
- 皮皮虾 / PiPiXia
- 微博 / Weibo: Web, Web V2, App
- 微信 / WeChat: Media Platform, Channels
- Instagram: V1, V2, V3
- YouTube: Web, Web V2
- Twitter/X
- Threads
- Reddit: App
- 知乎 / Zhihu
- 今日头条 / Toutiao: Web, App
- 西瓜视频 / Xigua
- LinkedIn: Web, Web V2
- 验证码 / Captcha Solver
- 临时邮箱 / Temp Mail
- Hybrid Parsing
- iOS Shortcut
- TikHub user/admin utility APIs, downloader APIs, health check, demo APIs

Exact counts and tags are in `references/supported-platforms.md` and `references/supported-platforms.json`.

## Files

- `references/endpoint-catalog.json` — complete OpenAPI endpoint catalog generated from `https://api.tikhub.io/openapi.json`.
- `references/community-search-endpoints.json` — filtered endpoints relevant to community search, discovery, recommendations, comments, users, posts/videos/notes, rankings, topics, products, and creator insights.
- `references/supported-platforms.md` — platform/tag/endpoints summary.
- `references/source-coverage.md` — crawl coverage, limitations, and verification notes.
- `scripts/tikhub_search.py` — stdlib-only helper for local endpoint search and authenticated calls.
- `scripts/.env.local` — local private API key file, mode `0600`.

## Quick Commands

From this skill folder:

```bash
cd ~/Desktop/tikhub-community-search-skill
python3 scripts/tikhub_search.py platforms
python3 scripts/tikhub_search.py find "搜索" --platform xiaohongshu --limit 20
python3 scripts/tikhub_search.py find "comment" --platform tiktok --limit 20
python3 scripts/tikhub_search.py find "trending" --platform youtube --limit 20
python3 scripts/tikhub_search.py find "reddit search" --limit 20
```

Call an endpoint:

```bash
python3 scripts/tikhub_search.py call GET /api/v1/tiktok/web/fetch_general_search \
  --param keyword="portable espresso" \
  --param offset=0 \
  --param search_id=""
```

Use China mainland optimized domain:

```bash
TIKHUB_BASE_URL=https://api.tikhub.dev python3 scripts/tikhub_search.py call GET /api/v1/douyin/search/fetch_video_search \
  --param keyword="露营咖啡" \
  --param offset=0
```

Refresh latest OpenAPI:

```bash
python3 scripts/tikhub_search.py refresh-openapi
```

## Community Search Workflow

1. Define the research target precisely.
   - Product/category: “便携咖啡机”, “AI 记笔记 app”, “宝宝湿疹护理”
   - Market/language/region: Chinese platforms vs global English platforms
   - Evidence type: posts, comments, creator videos, rankings, hashtags, shop/product reviews

2. Pick platform families by evidence quality.
   - Chinese “真实经验/种草/避坑”: Xiaohongshu, Douyin, Bilibili, Weibo, Zhihu
   - Short-video trend and creator language: TikTok, Douyin, Kuaishou, Lemon8
   - Long-form/video tutorials: YouTube, Bilibili
   - Forum-style objections and troubleshooting: Reddit, Zhihu
   - Product/social proof: TikTok Shop, Douyin ecommerce/Xingtu, Xiaohongshu notes, Instagram
   - Professional or B2B signals: LinkedIn

3. Find endpoints locally before calling.
   - `find "search keyword" --platform xiaohongshu`
   - `find "comment replies" --platform douyin`
   - `find "rank" --platform bilibili`
   - Prefer endpoints whose summaries match the target and whose required params you can satisfy.

4. Run cheap broad search first.
   - Query search/feed/ranking endpoints with 3–8 keyword variants.
   - Save IDs, URLs, cursors, search IDs, and platform-specific pagination fields.
   - Avoid immediately fetching every detail/comment endpoint; those cost more and may be slower.

5. Deepen only on promising items.
   - Fetch post/video/note detail for top results.
   - Fetch comments/replies for high-signal items.
   - Fetch creator/user profile if authority/context matters.

6. Normalize output into evidence rows.
   Minimum schema:
   - `platform`
   - `query`
   - `endpoint`
   - `item_id`
   - `url`
   - `author`
   - `created_at`
   - `text/title/summary`
   - `metrics`
   - `comments_sample`
   - `evidence_type`
   - `raw_json_path`

7. Synthesize patterns.
   - Cluster by use case, pain point, buying criterion, failure mode, workaround, sentiment, price sensitivity, regional language.
   - Quote short snippets with platform and URL where available.
   - Separate observed evidence from inference.

## Endpoint Selection Heuristics

- Search endpoint names usually include `search`, `fetch_*_search`, `general_search`, `keyword`, `suggest`, `creator search insights`, `product search`, or Chinese `搜索` / `关键词`.
- Discovery endpoints usually include `feed`, `recommend`, `discover`, `explore`, `hot`, `trending`, `rank`, `billboard`, `index`, `榜单`, `热门`, `推荐`.
- Community discussion endpoints include `comment`, `reply`, `comments`, `replies`, `评论`, `回复`.
- Topic endpoints include `hashtag`, `tag`, `topic`, `话题`.
- Product/shop endpoints include `shop`, `product`, `review`, `商品`, `评价`, `橱窗`.
- User/creator context endpoints include `user`, `profile`, `creator`, `followers`, `following`, `主页`, `创作者`.

## API Discipline

- Use timeout 30–60s, matching docs.
- TikHub docs say QPS limit is 10/s; stay below it. For research runs, use much lower concurrency unless the user explicitly asks for speed.
- Retry transient 5xx/network errors up to 3 times.
- Check `code`, `message`, `message_zh`, and `request_id` in JSON responses.
- Non-200 business code or HTTP 422 usually means missing/incorrect params; inspect endpoint params locally.
- Many TikHub responses are billed when successful. Start broad, then deepen selectively.
- Do not print the API key. Redact headers in logs.

## Platform Notes

- TikTok Web video CDN links may require `tt_chain_token` as a Cookie; some docs recommend TikTok App V3 endpoints for directly accessible watermark-free CDN links.
- Web vs App endpoints can return different fields and stability. If a Web endpoint fails or lacks detail, search the same platform’s App/V2/V3 endpoints.
- Some docs pages are protected or returned HTML/WAF during crawl; the live OpenAPI endpoint provided the complete machine-readable source of truth.
- Mainland China users should switch base URL to `https://api.tikhub.dev`; paths and params are unchanged.

## Verification Checklist

Before finalizing a community-search result:

- [ ] Platform and endpoint chosen from `endpoint-catalog.json` or `community-search-endpoints.json`
- [ ] Required params supplied exactly as documented
- [ ] API key loaded from env or `scripts/.env.local`, never displayed
- [ ] HTTP status and response `code` checked
- [ ] Pagination cursor/search_id retained when available
- [ ] Raw JSON saved if doing multi-step research
- [ ] Evidence rows include source platform, query, endpoint, item ID/URL, and timestamp/author when available
- [ ] Synthesis separates facts from interpretation
