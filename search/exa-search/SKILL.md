---
name: exa-search
description: "Exa Search API — deep research, structured outputs, content extraction. Use alongside Tavily for heavy-duty web research."
version: 1.0.0
author: Hermes Agent
metadata:
  related_skills: []
  requires_env: ["EXA_API_KEY"]
---

# Exa Search

Exa is a neural search engine optimized for LLM agents. Use it when Tavily's results aren't deep enough, or when you need structured outputs with citations (`outputSchema`).

## Setup

```bash
# Add to ~/.hermes/.env
EXA_API_KEY=your_key_here
```

Script installed at `~/.hermes/scripts/exa_search.py`.

## Usage

### Quick search
```bash
python ~/.hermes/scripts/exa_search.py --query "latest RAG techniques 2026" --type auto --num-results 5
```

### Deep search (research-grade)
```bash
python ~/.hermes/scripts/exa_search.py --query "multi-agent LLM orchestration patterns" --type deep --num-results 10
```

### Deep reasoning (complex synthesis)
```bash
python ~/.hermes/scripts/exa_search.py --query "compare and contrast RLHF vs DPO for LLM alignment" --type deep-reasoning
```

### Structured outputs (grounded JSON)
```bash
python ~/.hermes/scripts/exa_search.py \
  --query "companies developing AI agents 2026" \
  --output-schema '{"type":"object","properties":{"companies":{"type":"array","items":{"type":"object","properties":{"name":{"type":"string"},"product":{"type":"string"},"funding":{"type":"string"}}}}}}'
```

### Get content from known URLs
```bash
python ~/.hermes/scripts/exa_search.py \
  --urls "https://arxiv.org/abs/2501.00001" "https://example.com/article" \
  --text-max-chars 5000
```

## Search Types

| Type | Latency | Best For |
|------|---------|----------|
| auto | ~1s | General — balanced |
| fast | ~450ms | Latency-sensitive |
| instant | ~250ms | Chat, autocomplete |
| deep-lite | ~4s | Cheap synthesis |
| deep | 4-15s | Research, enrichment |
| deep-reasoning | 12-40s | Complex multi-step reasoning |

## Key Parameters

- `--highlights` (default: on) — token-efficient excerpts
- `--text-max-chars N` — full content extraction (set cap!)
- `--summary` / `--summary-query "?"` — LLM summary per result
- `--output-schema JSON` — grounded structured output with citations
- `--max-age-hours 0` — always livecrawl (freshness)
- `--max-age-hours -1` — cache only (speed)
- `--include-domains` / `--exclude-domains` — domain filter

## Important Notes

⚠️ **Do NOT use `includeDomains` with `category: "company"` or `category: "people"`** — 400 error.
⚠️ **Tavily is still the default `web_search`** — Exa is for on-demand deep searches.
⚠️ Text content without `maxCharacters` cap can blow up tokens. Prefer `--highlights` for agent workflows.

## When to Use Exa vs Tavily

- **Tavily** (default `web_search`): quick lookups, general questions, chat context
- **Exa**: deep research, structured data extraction, content enrichment, grounded answers with citations

## Raw JSON

Pass `--raw` to get the full API response as JSON for programmatic use.

## Reference

See `references/exa-api-guide.md` for the full API spec, common 400 error patterns, and endpoint reference.
