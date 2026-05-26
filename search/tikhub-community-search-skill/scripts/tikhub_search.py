#!/usr/bin/env python3
"""TikHub community experience search helper.

- Lists supported platforms from references/supported-platforms.json
- Searches endpoint catalog locally
- Calls TikHub endpoints with Bearer auth

No third-party dependencies; Python stdlib only.
"""
import argparse
import json
import os
import sys
import urllib.parse
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
REF = ROOT / "references"
ENV_LOCAL = Path(__file__).resolve().parent / ".env.local"


def load_env_file(path: Path) -> None:
    if not path.exists():
        return
    for line in path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        k, v = line.split("=", 1)
        os.environ.setdefault(k.strip(), v.strip())


def load_json(name: str):
    return json.loads((REF / name).read_text(encoding="utf-8"))


def norm(text: str) -> str:
    return (text or "").lower()


def endpoint_blob(e: dict) -> str:
    parts = [e.get("tag", ""), e.get("summary", ""), e.get("path", ""), e.get("description", "")]
    for p in e.get("parameters") or []:
        parts += [p.get("name", ""), p.get("description", "")]
    return " ".join(parts)


def cmd_platforms(args):
    rows = load_json("supported-platforms.json")
    for r in rows:
        print(f"{r['platform']}\tendpoints={r['endpoint_count']}\tsearch_like={r['search_endpoint_count']}\ttags={', '.join(r['tags'])}")


def cmd_find(args):
    catalog = load_json("community-search-endpoints.json" if args.community_only else "endpoint-catalog.json")
    terms = [norm(t) for t in args.query]
    platform = norm(args.platform or "")
    matches = []
    for e in catalog:
        blob = norm(endpoint_blob(e))
        if platform and platform not in norm(e.get("tag", "") + " " + e.get("path", "")):
            continue
        if all(t in blob for t in terms):
            matches.append(e)
    for i, e in enumerate(matches[: args.limit], 1):
        required = [p["name"] for p in e.get("parameters") or [] if p.get("required")]
        optional = [p["name"] for p in e.get("parameters") or [] if not p.get("required")]
        print(f"[{i}] {e['tag']} | {e['method']} {e['path']}")
        print(f"    {e.get('summary','')}")
        print(f"    required: {', '.join(required) if required else '-'}")
        print(f"    optional: {', '.join(optional[:12]) if optional else '-'}")
        if e.get("deprecated"):
            print("    deprecated: true")
    print(f"\nmatched={len(matches)} shown={min(len(matches), args.limit)}")


def parse_kv(items):
    data = {}
    for item in items or []:
        if "=" not in item:
            raise SystemExit(f"Invalid --param {item!r}; use key=value")
        k, v = item.split("=", 1)
        if v.lower() == "true":
            v = True
        elif v.lower() == "false":
            v = False
        else:
            try:
                if v.isdigit() or (v.startswith("-") and v[1:].isdigit()):
                    v = int(v)
                else:
                    v = float(v)
            except ValueError:
                pass
        data[k] = v
    return data


def request_json(method: str, url: str, api_key: str, params: dict):
    method = method.upper()
    headers = {"Authorization": f"Bearer {api_key}", "User-Agent": "tikhub-community-search-skill/1.0"}
    data = None
    if method == "GET":
        if params:
            sep = "&" if "?" in url else "?"
            url += sep + urllib.parse.urlencode(params, doseq=True)
    else:
        data = json.dumps(params, ensure_ascii=False).encode("utf-8")
        headers["Content-Type"] = "application/json"
    req = urllib.request.Request(url, data=data, headers=headers, method=method)
    with urllib.request.urlopen(req, timeout=60) as resp:
        raw = resp.read().decode("utf-8", errors="replace")
        try:
            return resp.status, json.loads(raw)
        except json.JSONDecodeError:
            return resp.status, raw


def cmd_call(args):
    load_env_file(ENV_LOCAL)
    api_key = os.environ.get("TIKHUB_API_KEY")
    if not api_key:
        raise SystemExit("Missing TIKHUB_API_KEY. Export it or put it in scripts/.env.local")
    base = args.base_url or os.environ.get("TIKHUB_BASE_URL") or "https://api.tikhub.io"
    params = parse_kv(args.param)
    status, body = request_json(args.method, base.rstrip("/") + args.path, api_key, params)
    print(json.dumps({"http_status": status, "data": body}, ensure_ascii=False, indent=2))


def cmd_refresh_openapi(args):
    url = args.url
    with urllib.request.urlopen(url, timeout=60) as resp:
        raw = resp.read().decode("utf-8")
    (REF / "openapi.latest.json").write_text(raw, encoding="utf-8")
    spec = json.loads(raw)
    print(f"saved {REF / 'openapi.latest.json'} paths={len(spec.get('paths', {}))}")


def main():
    p = argparse.ArgumentParser(description="TikHub community/search endpoint helper")
    sub = p.add_subparsers(dest="cmd", required=True)

    sp = sub.add_parser("platforms", help="List supported platforms and API tags")
    sp.set_defaults(func=cmd_platforms)

    sf = sub.add_parser("find", help="Find endpoints locally")
    sf.add_argument("query", nargs="+", help="Search terms, AND matched")
    sf.add_argument("--platform", help="Filter by tag/path substring, e.g. douyin, xiaohongshu, reddit")
    sf.add_argument("--limit", type=int, default=30)
    sf.add_argument("--all", dest="community_only", action="store_false", default=True, help="Search all endpoints, not only community/search-like endpoints")
    sf.set_defaults(func=cmd_find)

    sc = sub.add_parser("call", help="Call a TikHub endpoint")
    sc.add_argument("method", choices=["GET", "POST", "PUT", "DELETE", "PATCH"])
    sc.add_argument("path", help="Endpoint path, e.g. /api/v1/douyin/web/fetch_general_search")
    sc.add_argument("--param", action="append", default=[], help="key=value; repeatable")
    sc.add_argument("--base-url", help="Default: TIKHUB_BASE_URL or https://api.tikhub.io")
    sc.set_defaults(func=cmd_call)

    sr = sub.add_parser("refresh-openapi", help="Download latest OpenAPI to references/openapi.latest.json")
    sr.add_argument("--url", default="https://api.tikhub.io/openapi.json")
    sr.set_defaults(func=cmd_refresh_openapi)

    args = p.parse_args()
    args.func(args)


if __name__ == "__main__":
    main()
