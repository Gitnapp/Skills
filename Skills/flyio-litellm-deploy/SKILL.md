---
name: flyio-litellm-deploy
description: Deploy LiteLLM proxy to Fly.io with external PostgreSQL (Supabase). Use when deploying an LLM gateway/proxy, setting up LiteLLM on Fly.io, configuring multi-provider model routing (OpenAI, Anthropic, etc.), or managing Fly.io Docker-based deployments with pre-built images.
metadata:
  author: Gitnapp
  version: "1.0.0"
---

# Fly.io LiteLLM Deployment

Deploy a LiteLLM proxy server to Fly.io using a pre-built Docker image with Supabase PostgreSQL as the database backend.

## Architecture

```
Client --> Fly.io (LiteLLM Proxy) --> Provider APIs (OpenAI, Anthropic, etc.)
                  |
                  v
            Supabase PostgreSQL (data persistence)
```

## Key Lessons & Gotchas

### 1. Image Selection

- `litellm/litellm-database` - includes database drivers (psycopg2, Prisma), does NOT include PostgreSQL server
- `litellm/litellm` - base image without database support
- Use specific version tags (e.g., `v1.82.3-stable`), NOT `main-stable` (doesn't exist on Docker Hub)

### 2. fly.toml Configuration

```toml
app = 'my-litellm'
primary_region = 'sin'

[build]
  image = 'litellm/litellm-database:v1.82.3-stable'

[env]
  LITELLM_CONFIG_FILE_PATH = '/app/config.yaml'

[processes]
  app = '--config /app/config.yaml --port 4000 --num_workers 1'

[http_service]
  internal_port = 4000
  force_https = true
  auto_stop_machines = 'off'
  auto_start_machines = true
  min_machines_running = 1
  processes = ['app']

[[files]]
  guest_path = '/app/config.yaml'
  local_path = 'litellm_config.yaml'

[[vm]]
  memory = '2gb'
  cpu_kind = 'shared'
  cpus = 1
```

**Critical points:**
- `[processes]` value must NOT include `litellm` command — the image ENTRYPOINT is already `litellm`, so only pass arguments. Otherwise you get `Error: Got unexpected extra argument (litellm)`.
- `[build] image` skips Docker build entirely, pulling pre-built image from Docker Hub. This is the most reliable deploy method when local Docker or remote builders fail.
- `[[files]]` injects local config file into the container at deploy time.
- Set `auto_stop_machines = 'off'` and `min_machines_running = 1` to prevent the machine from auto-stopping during idle periods. The default `auto_stop_machines = 'stop'` with `min_machines_running = 0` will shut down the machine when idle, causing cold-start delays (~60s for database migration).

### 3. LiteLLM Config (litellm_config.yaml)

#### OpenAI Models
```yaml
- model_name: router/gpt-4o
  litellm_params:
    model: openai/gpt-4o          # openai/ prefix
    api_key: your-api-key
    api_base: https://provider.com/v1  # WITH /v1
```

#### Anthropic Models
```yaml
- model_name: router/claude-sonnet-4-6
  litellm_params:
    model: anthropic/claude-sonnet-4-6  # anthropic/ prefix
    api_key: your-api-key
    api_base: https://provider.com      # WITHOUT /v1
```

**Why the difference:** LiteLLM automatically appends `/v1/messages` to Anthropic api_base. If you include `/v1`, the actual request goes to `/v1/v1/messages` (broken).

#### Settings
```yaml
litellm_settings:
  master_key: your-master-key
  database_url: postgresql://user:pass@host:5432/dbname
  drop_params: true
  set_verbose: false
```

### 4. Secrets & Credentials

Two approaches:
- **Fly secrets** (production): `fly secrets set KEY=VALUE` — injected as env vars at runtime
- **Explicit in config** (simpler): Write credentials directly in `litellm_config.yaml`, add to `.gitignore`

If using explicit config, ensure `.gitignore` includes:
```
.env
litellm_config.yaml
```

### 5. Startup Behavior

LiteLLM with database takes ~60-90 seconds to start due to Prisma database migrations. During this time:
- Health check `/health/liveliness` returns connection refused
- Fly proxy shows "instance refused connection" errors
- This is normal — wait for `Uvicorn running on http://0.0.0.0:4000` in logs

### 6. Common Deploy Issues

| Issue | Cause | Fix |
|-------|-------|-----|
| `Got unexpected extra argument (litellm)` | `[processes]` includes `litellm` command | Remove `litellm` from process command, keep only args |
| Models list empty (`/v1/models` returns `[]`) | Missing `--config` flag at startup | Add `[processes]` with `--config /app/config.yaml` |
| `Could not find image "...main-stable"` | Wrong Docker tag | Check Docker Hub for actual tags (e.g., `v1.82.3-stable`) |
| Remote builder timeout | Depot/remote builder issues | Use `[build] image` with pre-built image instead |
| Machine auto-stops | `auto_stop_machines = 'stop'` | Set to `'off'` and `min_machines_running = 1` |
| Anthropic models fail | `api_base` includes `/v1` | Remove `/v1` from Anthropic api_base |

### 7. Useful Commands

```bash
# Deploy
fly deploy

# Check status
fly status
fly machines list

# View logs
fly logs --no-tail | tail -30

# SSH into container
fly ssh console -C "cat /app/config.yaml"
fly ssh console -C "ps aux | grep litellm"

# Manage secrets
fly secrets list
fly secrets set DATABASE_URL="postgresql://..."

# Health check
curl https://your-app.fly.dev/health/liveliness
curl https://your-app.fly.dev/v1/models -H "Authorization: Bearer your-master-key"
```

### 8. Optional: Zero-Downtime Deploys (Dual Instance)

Deploy two machines so rolling updates keep one running while the other restarts (~60-90s migration time).

Changes to `fly.toml`:

```toml
[http_service]
  min_machines_running = 2   # was 1

  [http_service.checks]
    [http_service.checks.readiness]
      interval = '10s'
      timeout = '5s'
      grace_period = '120s'  # allow time for Prisma migration
      method = 'GET'
      path = '/health/readiness'
```

Rolling deploy flow:
1. Machine A stays running, receives traffic
2. Machine B updates → starts → passes readiness check
3. Machine B receives traffic
4. Machine A updates → starts → passes readiness check
5. Both running — zero downtime

**Trade-off:** VM costs double (2x `shared-cpu-1x:2048MB`). Only enable when uptime matters more than cost.

### 9. Auto-Import Models from Provider

To dynamically fetch and import models from an OpenAI-compatible provider:

```bash
curl -s https://provider.com/v1/models \
  -H "Authorization: Bearer API_KEY" \
  | python3 -c "
import json, sys
data = json.load(sys.stdin)
for m in data['data']:
    mid = m['id']
    if mid.startswith(('gpt-', 'o1', 'o3', 'o4', 'chatgpt-')):
        print(f'OpenAI: {mid}')
    elif mid.startswith('claude-'):
        print(f'Anthropic: {mid}')
"
```

Then generate `litellm_config.yaml` entries with appropriate prefixes and api_base values per provider type.
