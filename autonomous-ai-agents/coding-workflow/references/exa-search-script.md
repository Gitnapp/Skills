# Exa Search Script

A CLI wrapper for the [Exa search API](https://exa.ai) lives at `~/.hermes/scripts/exa_search.py`.

## Configuration

Requires `EXA_API_KEY` in environment or `~/.hermes/.env`:

```bash
# In ~/.hermes/.env (or profile-specific .env):
EXA_API_KEY=your_key_here
```

**Common issue:** the key may be **commented out** (`# EXA_API_KEY=...`). Check both `~/.hermes/.env` and `~/.hermes/profiles/<name>/.env`.

## Usage

```bash
# Basic search
python ~/.hermes/scripts/exa_search.py --query "latest AI agents" --num-results 5

# Deep research
python ~/.hermes/scripts/exa_search.py --query "quantization techniques 2025" --type deep --num-results 10 --summary

# Fetch specific URLs
python ~/.hermes/scripts/exa_search.py --urls "https://example.com/article" "https://example.com/other"

# Structured output
python ~/.hermes/scripts/exa_search.py --query "GPU companies" --output-schema '{"type":"object","properties":{"companies":{"type":"array"}}}'

# Fresh content only (livecrawl)
python ~/.hermes/scripts/exa_search.py --query "news" --max-age-hours 0

# Raw JSON
python ~/.hermes/scripts/exa_search.py --query "RAG papers" --raw | jq .
```

## Search Types

| Type | Use Case |
|------|----------|
| `auto` | Default — let Exa decide |
| `fast` | Quick results, low latency |
| `deep` | Deep research, high quality |
| `deep-reasoning` | Deep + chain-of-thought |
| `instant` | Instant results via cache |
| `deep-lite` | Lightweight deep search |
