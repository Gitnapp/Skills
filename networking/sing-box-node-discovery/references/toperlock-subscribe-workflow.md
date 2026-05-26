# Toperlock/sing-box-subscribe App Structure

Source: https://github.com/Toperlock/sing-box-subscribe

## Architecture

Flask app that takes subscription URLs and generates sing-box JSON configs. No database — all state is in-memory and ephemeral (shared across visitors, overwritten on each save).

## Key Endpoints

| Endpoint | Method | Purpose |
|----------|--------|---------|
| `/` | GET | Main page with textarea form + config template selector |
| `/edit_temp_json` | POST | Save providers JSON (subscription URLs) to memory |
| `/generate_config` | POST | Generate sing-box config using saved providers + selected template |
| `/config/<URL>` | GET | Direct generation: download subscription from URL and generate config |

## /generate_config Parameters

`template_index` (form-encoded, not JSON):
- `0` — `config_template_groups_rule_set_tun` (most complete, 26 outbounds: selector groups + servers)
- `1` — `config_template_groups_rule_set_tun_fakeip` (same as 0 with fakeip DNS)
- `2` — `config_template_no_groups_tun_VN` (minimal, 3 outbounds)
- `3` — `sb-config-1.12` (same structure as 0 but for sing-box 1.12)

The template files are in the repo's `config_templates/` directory. The app substitutes `{{subscribes_parsed}}` with actual proxy nodes from the saved providers.

## Response Format

Returns raw sing-box JSON config. Success pattern:

```json
{
  "log": {...},
  "inbounds": [...],
  "outbounds": [
    ...selector groups...,
    ...actual proxy servers (vless, hysteria2, shadowsocks, etc.)...,
    {"type": "direct", "tag": "direct"}
  ],
  "route": {...}
}
```

## Known Instances (2026-05 session)

All on Japanese IPs, running identical code:

Core servers (166966/177966/511966 domain family):
- 47.74.34.63:5000 — main server, hosts most *.155966.xyz and *.177966.xyz domains
- Various subdomains: www.abm.my.155966.xyz, awake.my.155966.xyz, agitgub.my.155966.xyz, aba.177966.xyz, acg.177966.xyz, abc.177966.xyz, acn.177966.xyz, anzjk.my.155966.xyz

Carrionlee domain family:
- 8.209.234.62:5005 — ck.carrionlee.xyz, bark.carrionlee.xyz

Others:
- 138.2.4.58:5000
- 8.211.133.223:50000
- 193.123.167.2:3002
- 141.147.176.210:5000 (timeout at time of testing)

## Node Family: 177966.xyz (Discovered 2026-05-23)

Single provider configuration spread across 6+ instances. All share the same UUID.

Server domains:
- `aba.177966.xyz` — HK (21000, 25000)
- `sab.511966.xyz` — US (21000, 25000)
- `abc.177966.xyz` — KR (21000, 25000, 31000 HY2, 35000 HY2)
- `acg.177966.xyz` — SG (21000, 25000, 31000 HY2, 35000 HY2)
- `acn.177966.xyz` — SG secondary/坡西 (21000, 25000, 31000 HY2, 35000 HY2)
- `sbt.177966.xyz` — CN 联通免流 WS (85, 8082)
- `baa.177966.xyz` — CN 联通免流 WS (85, 8082)

Protocols: VLESS + REALITY (xtls-rprx-vision), Hysteria2
VLESS TLS: insecure=true, server_name=images.apple.com, fingerprint=chrome
Hysteria2 TLS: server_name matches domain, insecure=false, alpns=h3

UUID was identical across all nodes — suggests leaked/shared airport config.
