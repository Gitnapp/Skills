#!/usr/bin/env python3
"""
TikHub 小红书 (Xiaohongshu) API CLI — search notes/users, get note detail.

Usage:
  # Search notes
  python tikhub_xhs.py search-notes --keyword "美食推荐" --page 1
  python tikhub_xhs.py search-notes --keyword "AI工具" --sort-type general --note-type video

  # Search users
  python tikhub_xhs.py search-users --keyword "美食博主" --page 1

  # Get image note detail
  python tikhub_xhs.py get-image-note --note-id 697c0eee000000000a03c308
  python tikhub_xhs.py get-image-note --share-text "http://xhslink.com/o/8GqargIxrko"

  # Get video note detail
  python tikhub_xhs.py get-video-note --note-id 697c0eee000000000a03c308
  python tikhub_xhs.py get-video-note --share-text "http://xhslink.com/o/8GqargIxrko"

  # Raw JSON output
  python tikhub_xhs.py search-notes --keyword "美食" --raw
"""
import json
import os
import sys
import urllib.request
import urllib.error
import argparse

API_KEY = os.environ.get("TIKHUB_API_KEY", "")

# Fallback: read from ~/.hermes/.env if env var not set
if not API_KEY:
    env_path = os.path.expanduser("~/.hermes/.env")
    if os.path.exists(env_path):
        with open(env_path) as f:
            raw = f.read()
        import re
        m = re.search(r'export\s+TIKHUB_API_KEY=([^\s"\']+|["\'][^"\']*["\'])', raw)
        if m:
            API_KEY = m.group(1).strip('"').strip("'")
BASE_URL = "https://api.tikhub.io/api/v1/xiaohongshu/app_v2"


def do_get(endpoint: str, params: dict) -> dict:
    """Make a GET request to the TikHub API."""
    if not API_KEY:
        print("Error: TIKHUB_API_KEY not set.", file=sys.stderr)
        sys.exit(1)

    # Build query string
    qs = "&".join(f"{k}={urllib.request.quote(str(v), safe='')}" for k, v in params.items() if v is not None and v != "")
    url = f"{BASE_URL}/{endpoint}?{qs}"

    req = urllib.request.Request(
        url,
        headers={
            "Authorization": f"Bearer {API_KEY}",
            "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36",
        },
        method="GET",
    )

    try:
        with urllib.request.urlopen(req, timeout=60) as resp:
            return json.loads(resp.read().decode("utf-8"))
    except urllib.error.HTTPError as e:
        body = e.read().decode("utf-8", errors="replace")
        print(f"HTTP {e.code} error:\n{body}", file=sys.stderr)
        sys.exit(1)
    except urllib.error.URLError as e:
        print(f"Connection error: {e.reason}", file=sys.stderr)
        sys.exit(1)


def format_result(data: dict, raw: bool) -> str:
    """Format API response as readable text."""
    if raw:
        return json.dumps(data, indent=2, ensure_ascii=False)

    lines = []
    lines.append(f"Code: {data.get('code')}")
    lines.append(f"Message: {data.get('message_zh') or data.get('message', '')}")

    d = data.get("data")
    if d is None:
        lines.append("(no data)")
        return "\n".join(lines)

    # Handle nested data.data structure (search results or note detail)
    inner = d.get("data") if isinstance(d, dict) else None
    if isinstance(inner, dict):
        items = inner.get("items") or []
        if items:
            lines.append(f"\nTotal items: {len(items)}")
            for i, item in enumerate(items, 1):
                note = item.get("note", item) if isinstance(item, dict) else item
                lines.append("")
                lines.append(f"--- #{i} ---")
                _format_note(note, lines)
            return "\n".join(lines)
    elif isinstance(inner, list):
        # Note detail: data.data = [{"note_list": [...]}]
        for entry in inner:
            if isinstance(entry, dict):
                note_list = entry.get("note_list", [entry])
                for i, note_item in enumerate(note_list, 1):
                    lines.append("")
                    lines.append(f"--- #{i} ---")
                    _format_note(note_item, lines)
        if any(isinstance(entry, dict) and entry.get("note_list") for entry in inner):
            return "\n".join(lines)

    # If data is a list, it's search results
    if isinstance(d, list):
        for i, item in enumerate(d, 1):
            lines.append("")
            lines.append(f"--- #{i} ---")
            _format_note(item, lines)
    elif isinstance(d, dict):
        # Single item (note detail) or paginated results
        items = d.get("items") or d.get("notes") or d.get("results") or []
        if items:
            lines.append(f"\nTotal: {d.get('total', len(items))}")
            for i, item in enumerate(items, 1):
                lines.append("")
                lines.append(f"--- #{i} ---")
                _format_note(item, lines)
        else:
            lines.append("")
            _format_note(d, lines)

    return "\n".join(lines)


def _format_note(item: dict, lines: list):
    """Format a single note/user dict."""
    # Note fields
    note_id = item.get("note_id") or item.get("id", "")
    title = item.get("title", item.get("display_title", ""))
    desc = item.get("desc", item.get("description", item.get("display_name", "")))
    user = item.get("user", item.get("author", {}))
    if isinstance(user, dict):
        user_name = user.get("nickname", user.get("nick_name", user.get("nickName", "")))
        user_id = user.get("user_id", "")
        if user_name:
            lines.append(f"Author: {user_name} ({user_id})")

    if title:
        lines.append(f"Title: {title}")
    if desc:
        lines.append(f"Description: {desc[:200]}")
    if note_id:
        lines.append(f"Note ID: {note_id}")

    # Stats
    interact = item.get("interact_info", item.get("interactInfo", {}))
    if isinstance(interact, dict):
        liked = interact.get("liked_count", interact.get("likedCount", ""))
        collected = interact.get("collected_count", interact.get("collectedCount", ""))
        commented = interact.get("comment_count", interact.get("commentCount", ""))
        shared = interact.get("share_count", interact.get("shareCount", ""))
        parts = []
        if liked:
            parts.append(f"❤️ {liked}")
        if collected:
            parts.append(f"⭐ {collected}")
        if commented:
            parts.append(f"💬 {commented}")
        if shared:
            parts.append(f"🔄 {shared}")
        if parts:
            lines.append(f"Stats: {'  '.join(parts)}")

    # Image/video count
    img_count = item.get("image_count", item.get("imageCount", ""))
    if img_count:
        lines.append(f"Images: {img_count}")

    # User search fields
    follower = item.get("follower_count", item.get("followerCount", ""))
    following = item.get("following_count", item.get("followingCount", ""))
    notes = item.get("note_count", item.get("noteCount", ""))
    if follower:
        lines.append(f"Followers: {follower}  Following: {following}  Notes: {notes}")

    # Type
    note_type = item.get("note_type", item.get("type", ""))
    if note_type:
        lines.append(f"Type: {note_type}")

    # URL
    share_url = item.get("share_url", item.get("url", ""))
    if share_url:
        lines.append(f"URL: {share_url}")


def main():
    parser = argparse.ArgumentParser(description="TikHub 小红书 API CLI")
    sub = parser.add_subparsers(dest="command", required=True)

    # search-notes
    sn = sub.add_parser("search-notes", help="搜索小红书笔记")
    sn.add_argument("--keyword", required=True, help="搜索关键词")
    sn.add_argument("--page", type=int, default=1, help="页码 (从1开始)")
    sn.add_argument("--sort-type", default="general", choices=["general", "most_popular", "latest", "most_commented"],
                    help="排序方式")
    sn.add_argument("--note-type", default="不限", choices=["不限", "video", "image", "图文", "视频"],
                    help="笔记类型")
    sn.add_argument("--time-filter", default="不限", choices=["不限", "one_day", "one_week", "one_month", "three_months", "six_months", "one_year"],
                    help="时间过滤")
    sn.add_argument("--search-id", default="", help="翻页search_id")
    sn.add_argument("--search-session-id", default="", help="翻页search_session_id")
    sn.add_argument("--source", default="explore_feed", help="来源")
    sn.add_argument("--ai-mode", type=int, default=0, help="AI模式 (0/1)")
    sn.add_argument("--raw", action="store_true", default=False, help="输出原始JSON")

    # search-users
    su = sub.add_parser("search-users", help="搜索小红书用户")
    su.add_argument("--keyword", required=True, help="搜索关键词")
    su.add_argument("--page", type=int, default=1, help="页码 (从1开始)")
    su.add_argument("--search-id", default="", help="翻页search_id")
    su.add_argument("--source", default="explore_feed", help="来源")
    su.add_argument("--raw", action="store_true", default=False, help="输出原始JSON")

    # get-image-note
    gin = sub.add_parser("get-image-note", help="获取图文笔记详情")
    gin.add_argument("--note-id", default="", help="笔记ID")
    gin.add_argument("--share-text", default="", help="分享链接")
    gin.add_argument("--raw", action="store_true", default=False, help="输出原始JSON")

    # get-video-note
    gvn = sub.add_parser("get-video-note", help="获取视频笔记详情")
    gvn.add_argument("--note-id", default="", help="笔记ID")
    gvn.add_argument("--share-text", default="", help="分享链接")
    gvn.add_argument("--raw", action="store_true", default=False, help="输出原始JSON")

    args = parser.parse_args()
    raw = getattr(args, "raw", False)

    if args.command == "search-notes":
        params = {
            "keyword": args.keyword,
            "page": args.page,
            "sort_type": args.sort_type,
            "note_type": args.note_type,
            "time_filter": args.time_filter,
            "search_id": args.search_id,
            "search_session_id": args.search_session_id,
            "source": args.source,
            "ai_mode": args.ai_mode,
        }
        data = do_get("search_notes", params)
        print(format_result(data, raw))

    elif args.command == "search-users":
        params = {
            "keyword": args.keyword,
            "page": args.page,
            "search_id": args.search_id,
            "source": args.source,
        }
        data = do_get("search_users", params)
        print(format_result(data, raw))

    elif args.command == "get-image-note":
        if not args.note_id and not args.share_text:
            print("Error: need --note-id or --share-text", file=sys.stderr)
            sys.exit(1)
        params = {"note_id": args.note_id, "share_text": args.share_text}
        data = do_get("get_image_note_detail", params)
        if raw:
            print(json.dumps(data, indent=2, ensure_ascii=False))
        else:
            print(format_result(data, raw))

    elif args.command == "get-video-note":
        if not args.note_id and not args.share_text:
            print("Error: need --note-id or --share-text", file=sys.stderr)
            sys.exit(1)
        params = {"note_id": args.note_id, "share_text": args.share_text}
        data = do_get("get_video_note_detail", params)
        if raw:
            print(json.dumps(data, indent=2, ensure_ascii=False))
        else:
            print(format_result(data, raw))


if __name__ == "__main__":
    main()
