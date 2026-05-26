# Clash API for Programmatic Node Testing

sing-box's experimental clash_api exposes REST endpoints for managing and testing proxy nodes.

## API Base

`http://127.0.0.1:{external_controller_port}` (configured in sing-box config under `experimental.clash_api`)

## Key Endpoints

### GET /version
Check if sing-box is running.
```bash
curl http://127.0.0.1:19090/version
# {"meta":true,"premium":true,"version":"sing-box 1.13.12"}
```

### GET /proxies
List all proxies (outbounds). The response includes selector groups with their `all` member list.
```bash
curl http://127.0.0.1:19090/proxies | python3 -m json.tool
```
Structure:
```json
{
  "proxies": {
    "selector_name": {
      "type": "Selector",
      "now": "current_selection",
      "all": ["node1", "node2", ...]
    },
    "node_name": {
      "type": "Vless",  // or Hysteria2, Shadowsocks, etc.
      ...
    }
  }
}
```

### PUT /proxies/{group_name}
Switch a selector group to a specific node. Body: `{"name": "node_tag"}`.
```bash
curl -s -X PUT http://127.0.0.1:19090/proxies/test_group \
  -H 'Content-Type: application/json' \
  -d '{"name":"🇭🇰 香港|TCP|21000"}'
```
Returns 204 on success. Node names with emoji/special chars must be exact matches from the `/proxies` response.

### GET /proxies/{node_name}/delay
Test node connectivity by measuring delay to a URL. This performs the actual protocol handshake.
```bash
curl -s "http://127.0.0.1:19090/proxies/🇭🇰%20香港|TCP|21000/delay?url=https://www.gstatic.com/generate_204&timeout=10000"
```
- `url` — must be URL-encoded
- `timeout` — in milliseconds
- Returns `{"delay": 290}` on success (ms), empty response on failure
- For VLESS+REALITY/Hysteria2, this is the only reliable test (raw TCP will always fail)

### Fallback: curl through proxy
When the delay API returns empty (e.g., for nodes that need additional negotiation), fall back to curl through the mixed inbound:
```bash
curl -s -x http://127.0.0.1:11080 \
  -o /dev/null -w '%{http_code}|%{time_total}' \
  "https://www.gstatic.com/generate_204"
```
HTTP 204 = working, 000 = failure/timeout.

## Script Pattern

```python
import urllib.parse, json, time

nodes = [...]  # from /proxies response
PROXY_PORT = 11080
API_URL = "http://127.0.0.1:19090"
TEST_URL = "https://www.gstatic.com/generate_204"

for node_name in nodes:
    # 1. Switch
    payload = json.dumps({"name": node_name})
    subprocess.run(["curl", "-s", "-X", "PUT", f"{API_URL}/proxies/test_group",
                    "-H", "Content-Type: application/json", "-d", payload])
    time.sleep(0.5)
    
    # 2. Test delay
    encoded = urllib.parse.quote(node_name, safe='')
    result = subprocess.run(["curl", "-s", "--max-time", "15",
        f"{API_URL}/proxies/{encoded}/delay?url={urllib.parse.quote(TEST_URL)}&timeout=10000"],
        capture_output=True, text=True)
    
    # 3. Parse
    try:
        data = json.loads(result.stdout)
        if data.get('delay', 0) > 0:
            print(f"✅ {node_name}: {data['delay']}ms")
            continue
    except: pass
    
    # 4. Fallback
    result2 = subprocess.run(["curl", "-s", "-x", f"http://127.0.0.1:{PROXY_PORT}",
        "-o", "/dev/null", "-w", "%{http_code}|%{time_total}", TEST_URL],
        capture_output=True, text=True)
    code = result2.stdout.split('|')[0]
    print(f"{'✅' if code in ('204','200') else '❌'} {node_name}: HTTP {code}")
```
