---
name: hermes-profile-config
description: Batch-manage Hermes Agent profile configurations — migrate providers, update models, sync .env API keys, and clean up old references across multiple profiles.
version: 1.0.0
author: Hermes Agent
---

# Hermes Profile Config Management

Batch-update config.yaml and .env across multiple Hermes profiles. Use when migrating providers, changing default models, adding/removing API keys, or cleaning up stale provider references.

## Trigger

Use when the user wants to:
- Switch all (or some) profiles to a new provider
- Add/remove models across profiles
- Sync API keys in .env files to match config.yaml providers
- Clean up old provider references after a migration

## Profile Layout

```
~/.hermes/profiles/
├── hermes-default/    ← usually the "source of truth" / most up-to-date
│   ├── config.yaml    ← model, providers, fallback_providers blocks
│   └── .env           ← API keys (KEY_ENV=value)
├── ctf/
├── finance/
├── ppt/
└── researcher/
```

## Workflow: Batch Provider Migration

### 1. Identify source and targets

```bash
# List all profiles
ls ~/.hermes/profiles/

# Read source provider config (usually hermes-default)
grep -A 20 "yunwu" ~/.hermes/profiles/hermes-default/config.yaml
```

### 2. Replace model + providers blocks via Python regex

Use Python (not sed/awk) for multi-line YAML block replacement — regex with `re.MULTILINE | re.DOTALL` is reliable for structured YAML sections.

```python
import re

profiles = ['ctf', 'finance', 'ppt', 'researcher']
base = '/Users/admin/.hermes/profiles'

new_model_block = """model:
  default: qwen3.7-max
  provider: yunwu
  api_mode: chat_completions
  context_length: 1000000"""

new_providers_block = """providers:
  yunwu:
    key_env: YUNWU_API_KEY
    base_url: https://yunwu.ai/v1
    api_mode: chat_completions
    discover_models: false
    default_model: qwen3.7-max
    models:
      qwen3.7-max:
        context_length: 1000000
      gpt-5.5:
        context_length: 1000000"""

for p in profiles:
    path = f'{base}/{p}/config.yaml'
    with open(path, 'r') as f:
        content = f.read()
    
    # Replace model block: from "model:" to the line before "providers:"
    content = re.sub(
        r'^model:.*?(?=^providers:)',
        new_model_block + '\n',
        content,
        flags=re.MULTILINE | re.DOTALL
    )
    
    # Replace providers block: from "providers:" to "fallback_providers:"
    content = re.sub(
        r'^providers:.*?(?=^fallback_providers:)',
        new_providers_block + '\n',
        content,
        flags=re.MULTILINE | re.DOTALL
    )
    
    with open(path, 'w') as f:
        f.write(content)
```

### 3. Sync .env API keys

After updating config.yaml, check which profiles are missing the new provider's API key:

```bash
for p in ctf finance ppt researcher hermes-default; do
  echo "=== $p ==="
  grep -i "YUNWU\|DEEPSEEK\|BLT" ~/.hermes/profiles/$p/.env 2>/dev/null || echo "(no matching keys)"
done
```

Copy the key from the source profile to targets that are missing it:

```bash
for p in ctf finance ppt researcher; do
  echo "" >> ~/.hermes/profiles/$p/.env
  echo "# yunwu.ai custom provider" >> ~/.hermes/profiles/$p/.env
  echo "YUNWU_API_KEY=sk-xxx" >> ~/.hermes/profiles/$p/.env
done
```

### 4. Clean up old provider references

Remove old API keys from .env after migration:

```bash
for p in ctf finance ppt researcher; do
  sed -i '' '/^OLD_PROVIDER_KEY=/d' ~/.hermes/profiles/$p/.env
done
```

Also remove stale comments:

```bash
sed -i '' '/# old-provider custom provider/d' ~/.hermes/profiles/hermes-default/.env
```

### 5. Verify

```bash
# Check config.yaml headers
for p in ctf finance ppt researcher; do
  echo "=== $p ==="
  head -25 ~/.hermes/profiles/$p/config.yaml
done

# Check .env is clean
for p in ctf finance ppt researcher hermes-default; do
  echo "=== $p ==="
  grep -i "old_provider" ~/.hermes/profiles/$p/.env ~/.hermes/profiles/$p/config.yaml 2>/dev/null || echo "(clean)"
done
```

## Pitfalls

- **config.yaml and .env are separate** — updating providers in config.yaml does NOT auto-update .env. Always check both.
- **key_env must match** — the `key_env` field in config.yaml providers (e.g., `YUNWU_API_KEY`) must have a corresponding entry in .env.
- **fallback_providers is preserved** — the regex pattern `(?=^fallback_providers:)` stops before the fallback section, so it's not touched.
- **Don't use sed for multi-line YAML** — sed is line-oriented and fragile for block replacement. Python regex with DOTALL is reliable.
- **hermes-default is usually the source of truth** — it gets updated first via `hermes config set`, then other profiles are batch-synced from it.
- **Old .env keys are harmless but clutter** — leaving DEEPSEEK_API_KEY after migrating to yunwu won't break anything, but cleaning up avoids confusion.
- **`hermes config set` treats dots as nesting separators** — model names with dots like `mimo-v2.5-pro` will be split into nested YAML keys (`mimo-v2:` → `5-pro:`). Use Python/yaml.dump instead for provider blocks with dotted model names. A simple wrapper: `python3 -c "import yaml; config=yaml.safe_load(open('config.yaml')); config['providers']['yunwu']={...}; yaml.dump(config, open('config.yaml','w'), sort_keys=False)"`. Install pyyaml first: `pip3 install pyyaml`.
- **`hermes config set` writes to the active profile's config.yaml** (e.g., `~/.hermes/profiles/hermes-default/config.yaml`), NOT the top-level `~/.hermes/config.yaml`. When running under a named profile, always check which file was actually modified.
- **Profile .env files are symlinks** — ctf, finance, ppt, researcher profiles' `.env` files are symlinks to `hermes-default/.env`. Do NOT create standalone .env files in profile subdirectories or they will be out of sync. After any config change, only `hermes-default/.env` needs updating.
- **Restore .env from snapshot if corrupted** — if .env becomes a symlink loop during sync, restore from `~/.hermes/profiles/hermes-default/state-snapshots/<latest>/.env`. See `hermes-profile-git-sync` skill's env-symlink-loop-recovery reference for full procedure.
