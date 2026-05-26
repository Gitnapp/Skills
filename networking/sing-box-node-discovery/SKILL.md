---
name: sing-box-node-discovery
description: Discover proxy nodes from FOFA results, sing-box-subscribe instances, and other sources; verify node connectivity with sing-box binary + clash API.
---

# sing-box Node Discovery & Verification

## Triggers

- Testing or verifying sing-box proxy nodes
- Extracting nodes from FOFA search results pointing to sing-box config generators
- Probing Toperlock/sing-box-subscribe instances for pre-configured proxy configurations
- Programmatically testing proxy node connectivity via the sing-box clash API

## Workflow

### Phase 1: Discover nodes from Toperlock/sing-box-subscribe instances

When FOFA results show Flask instances with title "生成sing-box配置", these are Toperlock/sing-box-subscribe config generators.

**Pitfall**: Do NOT check the textarea content on the front page — it almost always shows the empty template with `"url": "URL"`. The user explicitly corrected this: "你错了，需要在每个网页上选择config selector，然后点击'select and generate'才可以".

**Correct approach**: POST to `/generate_config` with `template_index` parameter:

```bash
# template_index values found so far:
# 0 = config_template_groups_rule_set_tun (most likely to have pre-filled nodes)
# 1 = config_template_groups_rule_set_tun_fakeip
# 2 = config_template_no_groups_tun_VN
# 3 = sb-config-1.12

curl -sS --max-time 30 -X POST "http://HOST:PORT/generate_config" \
  -d "template_index=0"
```

The response is a full sing-box JSON config. Extract server-type outbounds by filtering out types `selector`, `urltest`, `direct`, `block`, `dns`, `fakeip`, `tun`.

**Multiple instances**: These config generators are stateless and share a backend. If one instance has nodes, many others on the same server/domain family usually do too. Check all reachable instances to confirm, but the nodes are likely identical.

### Phase 2: Quick TCP port check (optional)

VLESS+REALITY and Hysteria2 nodes will NOT respond to raw TCP connections — this is expected behavior. A TCP timeout does NOT mean the node is dead. Skip this step if the node uses TLS/REALITY/Hysteria2.

For plain HTTP/WS nodes only, TCP checks are meaningful but may still fail due to firewall rules.

### Phase 3: Verify with sing-box binary + clash API

This is the authoritative test. It validates full protocol handshakes.

**Step 1: Create minimal test config** — no TUN, just mixed inbound + clash API:

```json
{
  "log": {"level": "warn"},
  "experimental": {
    "clash_api": {
      "external_controller": "127.0.0.1:19090",
      "secret": ""
    }
  },
  "inbounds": [{
    "type": "mixed",
    "tag": "mixed-in",
    "listen": "127.0.0.1",
    "listen_port": 11080
  }],
  "outbounds": [
    {"tag": "test_group", "type": "selector", "outbounds": ["node1", "node2", ...]},
    ...server_outbounds...,
    {"tag": "direct", "type": "direct"}
  ],
  "route": {"rules": [{"outbound": "test_group"}]}
}
```

**Critical**: Strip TUN inbound. Running sing-box with TUN on macOS will override system routes and can break the current SSH/network connection. Use only mixed (HTTP+SOCKS) inbound on a high port like 11080.

**Step 2: Start sing-box in background**:

```bash
# Use terminal(background=true) — never use `&` in foreground terminal()
sing-box run -c /tmp/singbox_test_config.json

# Verify it started
curl -s http://127.0.0.1:19090/version
```

**Step 3: Test each node via clash API**:

```bash
# Switch to node
curl -s -X PUT http://127.0.0.1:19090/proxies/test_group \
  -H 'Content-Type: application/json' \
  -d '{"name":"node_tag_name"}'

# Test delay (primary method)
curl -s "http://127.0.0.1:19090/proxies/NODE_NAME/delay?url=https://www.gstatic.com/generate_204&timeout=10000"

# Fallback: curl through proxy
curl -s -x http://127.0.0.1:11080 -o /dev/null -w '%{http_code}|%{time_total}' \
  "https://www.gstatic.com/generate_204"
```

The clash API `/proxies/:name/delay` endpoint is the primary test. If it returns `{"delay": N}`, the node is working. If it returns empty or errors, fall back to direct curl through the proxy.

**Step 4: Kill sing-box after testing**:

```bash
process(action="kill", session_id="proc_...")
```

Never leave sing-box running — it binds ports and may conflict with later operations.

### Phase 4: Save results

Always produce a verified CSV with these columns:
- `tag`, `type`, `server`, `port`, `region`, `uuid`(truncated), `password`(truncated), `flow`, `sni`, `reality_pk`, `reality_sid`, `delay_ms`, `status`, `note`

Flag duplicates (nodes sharing the same server:port with different tags) and note special requirements (e.g., 中国免流 nodes need China Unicom network).

## Pitfalls

1. **Textarea vs POST**: NEVER check the textarea for subscription URLs. The nodes come from POSTing to `/generate_config` with a template_index. The textarea shows the user-editable subscription template, not the generated config.

2. **TUN kills connection**: Never include TUN inbound in test configs on remote/SSH sessions. Use mixed inbound only.

3. **TCP timeout is normal**: VLESS+REALITY, Hysteria2, and most modern proxy protocols will NOT respond to raw TCP — the server requires a protocol handshake first. A TCP timeout is NOT a failure signal.

4. **中国免流 nodes**: Nodes tagged with "免流" (free data) and WS transport targeting Chinese IPs (sbt.177966.xyz, baa.177966.xyz) require China Unicom mobile network. They will NEVER work from overseas VPS/macOS — don't waste time testing them.

5. **Same-UUID nodes**: When all nodes share the same UUID, they come from a single subscription/provider. The config is likely a leaked/shared airport configuration. Test them, but note they may be revoked at any time.

6. **`discover_models: false` for aggregator APIs**: When configuring sing-box or proxy providers that use aggregator APIs (returning hundreds of models), set `discover_models: false` to avoid polluting the model list.

## References

- `references/toperlock-subscribe-workflow.md` — Detailed Toperlock/sing-box-subscribe app structure and API endpoints
- `references/clash-api-testing.md` — Clash API endpoints for programmatic node testing
