# TikHub Community Search Skill

Portable Hermes skill saved on Desktop.

Install later if needed:

```bash
mkdir -p ~/.hermes/skills/research/tikhub-community-search
cp -R ~/Desktop/tikhub-community-search-skill/* ~/.hermes/skills/research/tikhub-community-search/
```

Local use:

```bash
cd ~/Desktop/tikhub-community-search-skill
python3 scripts/tikhub_search.py platforms
python3 scripts/tikhub_search.py find "搜索" --platform xiaohongshu --limit 20
python3 scripts/tikhub_search.py call GET /api/v1/tiktok/web/fetch_general_search --param keyword="TikTok" --param offset=0 --param search_id=""
```

Security:

- `scripts/.env.local` stores the provided TikHub API key locally with `0600` permissions.
- Do not commit or paste `scripts/.env.local`.
