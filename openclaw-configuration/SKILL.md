---
name: openclaw-configuration
description: Configure OpenClaw AI agent CLI — built-in providers, custom providers, secrets, default models, and troubleshooting
category: software-development
---

# OpenClaw Configuration

Configure OpenClaw (`openclaw`) — an AI agent CLI similar to Hermes — with model providers, API keys, and default model selection.

## Using Built-in Providers (Recommended)

OpenClaw ships **built-in provider catalogs** for many providers (DeepSeek, OpenAI, Anthropic, etc.). These have pre-defined model lists, correct API adapters, and proper thinking/tool support — **no custom provider definition needed**.

### How to Use a Built-in Provider

1. Set the API key via `~/.openclaw/.env` (OpenClaw auto-loads this file):
   ```bash
   echo "DEEPSEEK_API_KEY=sk-xxx..." >> ~/.openclaw/.env
   ```

2. Set the default model:
   ```bash
   openclaw config set agents.defaults.model.primary "deepseek/deepseek-v4-flash"
   ```

3. Verify models are available:
   ```bash
   openclaw models list --all --provider deepseek
   ```

That's it — no custom provider definition under `models.providers` needed.

### Built-in Provider Benefits

- Pre-configured model lists with correct context windows, max tokens, and API adapters
- Proper handling of provider-specific features (e.g. DeepSeek V4 thinking/tool replay contract)
- Automatic updates when OpenClaw adds new models
- No risk of schema conflicts or manual model definition errors

### Built-in DeepSeek Provider

| Property | Value |
|---|---|
| Provider ID | `deepseek` |
| Auth key | `DEEPSEEK_API_KEY` |
| Base URL | `https://api.deepseek.com` (pre-configured, no `baseUrl` needed) |
| API | OpenAI-compatible |

Built-in model refs: `deepseek/deepseek-v4-flash`, `deepseek/deepseek-v4-pro`, `deepseek/deepseek-chat`, `deepseek/deepseek-reasoner`.

### When to Use Custom Providers Instead

Only define `models.providers.<name>` when you need to:
- Route through a proxy/gateway with a different `baseUrl` (e.g. LiteLLM, OpenRouter)
- Add a model that doesn't exist in the built-in catalog
- Use a non-standard API adapter

For direct provider connections (DeepSeek, OpenAI, Anthropic), the built-in catalog is always preferred.

## Adding a Custom Provider

OpenClaw expects model providers under `models.providers.<name>` in `~/.openclaw/openclaw.json`. Each provider needs:

| Field | Description | Example |
|---|---|---|
| `baseUrl` | API endpoint URL | `https://api.deepseek.com/v1` |
| `apiKey` | Credential (inline, env ref, or file ref) | `{"source": "file", "provider": "default", "id": "/DEEPSEEK_API_KEY"}` |
| `api` | API protocol adapter | `openai-completions` (DeepSeek, OpenAI), `anthropic-messages` (Claude) |
| `models` | Array of model definitions | See below |

### API Key: File Secret Reference (Recommended)

1. Add the key to `~/.openclaw/credentials/secrets.json`:
   ```json
   {
     "DEEPSEEK_API_KEY": "sk-xxx..."
   }
   ```

2. Reference it in the provider config as a JSON pointer:
   ```json
   "apiKey": {
     "source": "file",
     "provider": "default",
     "id": "/DEEPSEEK_API_KEY"
   }
   ```

   The `id` must be an absolute JSON pointer. For a flat JSON secrets file `{"KEY": "val"}`, use `"/KEY"`. For nested files `{"providers": {"openai": {"apiKey": "..."}}}`, use `"/providers/openai/apiKey"`.

### Model Entry Format

```json
{
    "id": "deepseek-v4-flash",
    "name": "DeepSeek V4 Flash",
    "api": "openai-completions",
    "reasoning": true,
    "input": ["text"],
    "cost": {"input": 0, "output": 0, "cacheRead": 0, "cacheWrite": 0},
    "contextWindow": 1000000,
    "maxTokens": 32768
}
```

## Setting the Default Model

```bash
openclaw config set agents.defaults.model.primary "deepseek/deepseek-v4-flash"
```

Or edit `~/.openclaw/openclaw.json` directly:

```json
"agents": {
  "defaults": {
    "model": {
      "primary": "deepseek/deepseek-v4-flash",
      "fallbacks": []
    }
  }
}
```

Model IDs are referenced as `<provider>/<model-id>` (e.g. `deepseek/deepseek-v4-flash`, `litellm/gpt-5.4`).

## Adding Model Aliases

Under `agents.defaults.models`, add display aliases:

```json
"agents": {
  "defaults": {
    "models": {
      "deepseek/deepseek-v4-flash": { "alias": "DeepSeek V4 Flash" },
      "deepseek/deepseek-v4-pro": { "alias": "DeepSeek V4 Pro" }
    }
  }
}
```

## API Key Storage Options

| Method | How | Best for |
|---|---|---|
| `~/.openclaw/.env` | Add `KEY=val` line | Built-in providers, daemon-friendly |
| `~/.openclaw/credentials/secrets.json` | JSON file referenced by `openclaw config set` with `--ref-provider` | Custom providers, vault-like isolation |
| `env.vars` in `openclaw.json` | Plain string values only | Quick local dev, NOT for secrets |

`env.vars` only accepts plain strings (schema rejects object refs), so don't use it for API keys.

## Verification

```bash
# Validate config
openclaw config validate

# Check default model
openclaw config get agents.defaults.model.primary

# List built-in models for a provider
openclaw models list --all --provider deepseek

# Check provider details (custom providers only)
openclaw config get models.providers.deepseek
```

## Pitfalls

- **Custom provider definitions override built-in ones** — if you define `models.providers.deepseek` (even with correct models), it overrides the built-in deepseek provider, causing "no models available". Remove the custom definition and use `~/.openclaw/.env` for the API key instead.
- **`openclaw config patch --stdin` fails on nested objects** — the CLI's JSON5 validation rejects complex provider configs. Use direct JSON file editing (`write_file`/`patch`) instead.
- **File secret `id` must be a JSON pointer** — if the secrets provider is in `mode: "json"`, the `id` must be an absolute JSON pointer like `/KEY_NAME`, not just `"KEY_NAME"`.
- **`config set` with `--ref-provider` flag** — use `openclaw config set <path> --ref-provider default --ref-source file --ref-id <pointer>` for a CLI-native approach, but JSON pointer format still applies.
- **`env.vars` only accepts plain strings** — the schema rejects object refs. For API keys that shouldn't live in `openclaw.json`, use `~/.openclaw/.env` instead.
- **Config validation** — always run `openclaw config validate` after edits to catch schema errors early.
- **Duplicated plugin warnings** (like `memos-cloud-openclaw-plugin` or `openclaw-weixin`) are harmless — they just mean the plugin is installed both as a global npm package and in the config.
- **Restart needed** — TUI sessions (Crestodian) cache config at startup. After changing providers or models, exit and re-enter the TUI for changes to take effect.
