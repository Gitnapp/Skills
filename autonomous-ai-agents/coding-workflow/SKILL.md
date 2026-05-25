---
name: coding-workflow
description: "Optimize Hermes Agent for coding/vibecoding — profile setup, approvals mode, SOUL.md, model selection, toolset config, and developer environment preflight."
version: 1.0.0
author: user
tags: [hermes, coding, vibecoding, profile, configuration, dev-environment]
---

# Coding Workflow (Vibecoding) Setup

How to configure Hermes Agent for frictionless "vibecoding" — describe what you want in natural language and let the agent ship it. Covers profile creation, command-approval policy, personality, model choice, and environment preflight tasks like Node/nvm migration that make coding sessions smoother.

## Prerequisites

- Hermes Agent installed
- At least one API key configured (OpenRouter, DeepSeek, Anthropic, etc.)
- `terminal` toolset enabled (enabled by default on CLI)

## Steps

### 1. Create a Dedicated Profile

Isolate coding configuration from your default profile so vibecoding settings don't leak into other use cases.

```bash
# Clone from default
hermes profile create coding --clone-from default \
  --description "Vibecoding / full-autonomy coding profile"

# A wrapper script is created at ~/.local/bin/<profile_name>
# Use it directly: `coding chat`
```

The wrapper (`~/.local/bin/coding`) auto-selects the profile — no need for `-p coding` on every invocation.

### 2. Set Approvals Mode

Three levels — pick based on your risk tolerance:

| Mode | Behavior | When to Use |
|------|----------|-------------|
| `off` | Approve everything automatically, never prompts | Full vibecoding, solo projects |
| `smart` | Use an auxiliary LLM to auto-approve low-risk commands, prompt on high-risk | Good middle ground |
| `manual` | Always prompt before dangerous commands (default) | Learning or sensitive environments |

```bash
coding config set approvals.mode off    # full YOLO
coding config set approvals.mode smart  # recommended compromise
```

Also usable per-invocation: `coding --yolo chat` or `HERMES_YOLO_MODE=1`.

### 3. Write SOUL.md for Coding Persona

`~/.hermes/profiles/<name>/SOUL.md` defines the agent's personality and tone in that profile.

Recommended coding persona traits:
- **Action first** — when you say you'll do something, do it immediately with a tool call
- **Ship mentality** — finished is better than perfect, iterate after
- **Show output** — after writing code, run it and show results
- **Concise** — terminal output, no fluff
- **Practical** — solve the problem, don't discuss edge cases nobody will hit
- **Self-improving** — save tricky solutions as skills

### 4. Choose a Coding Model

```bash
coding model   # interactive picker
```

Good coding models (as of 2025-2026):
- **Claude Sonnet 4** (`anthropic/claude-sonnet-4`) — best all-round coder
- **DeepSeek V4 Flash** (`deepseek/deepseek-v4-flash`) — fast, good quality
- **GPT-4o** (`openai/gpt-4o`) — solid generalist
- **Claude Haiku** — fast for quick iterations

### 5. Verify Toolsets

Enable the toolsets that matter for coding:

```bash
coding tools
```

Recommended enabled for coding:
- ✅ `terminal` — shell commands, builds, git, installs
- ✅ `file` — read/write/patch/search files
- ✅ `web` — search docs, fetch APIs
- ✅ `vision` — read screenshots, diagrams
- ✅ `code_execution` — run Python snippets
- ✅ `delegation` — parallel subagents
- ✅ `skills` — load and save skills
- ✅ `todo` — multi-step task tracking

The coding profile's config also has `delegation.default_toolsets: [terminal, file, web]` — these are the tools subagents get by default.

### 6. Consider Worktree Mode

For running multiple coding agents on the same repo without git conflicts:

```bash
hermes -w chat    # creates an isolated git worktree per session
```

## SOUL.md Example

Save to `~/.hermes/profiles/<name>/SOUL.md`:

```markdown
You are a senior full-stack engineer and technical co-pilot.
- Action first. Do it, don't plan doing it.
- Ship mentality. Working > perfect.
- Show output. Run code and prove it works.
- Concise. Terminal-native, no fluff.
- Practical. Solve the current problem.
- Debug like a pro. Read errors, trace root cause, fix it.
```

## Toolchain Preflight Checklist

Before starting a coding session, verify key tools are ready:

```bash
# 1. Node version — should be LTS
node -v

# 2. Codex CLI — check auth, no Homebrew/nvm shadowing
which codex            # should not be /opt/homebrew/bin/codex
codex login status     # "Logged in using OpenAI" or similar

# 3. Global packages — verify codex, typescript, etc.
npm ls -g --depth=0 2>/dev/null

# 4. Git repo — Codex and many tools require one
git status 2>/dev/null || echo "⚠ Not in a git repo"
```

**Common toolchain issues to watch for:**

| Issue | Detection | Fix |
|-------|-----------|-----|
| Homebrew shadows nvm tool | `which codex` → `/opt/homebrew/bin/codex` | `brew uninstall --force codex` |
| Codex not logged in | `codex login status` → "Not logged in" | `codex login --device-auth` or pipe API key |
| nvm not available | `nvm ls` → "command not found" | Source `$NVM_DIR/nvm.sh` first |
| Exa search API key commented out | Script returns 401 on search | Uncomment `EXA_API_KEY` in `~/.hermes/.env` |

## Config Pitfalls

- **`hermes config set` with YAML-reserved words.** Values like `off`, `on`, `true`, `false`, `yes`, `no` are parsed as YAML booleans, not strings. Example: `hermes config set approvals.mode off` sets `mode: false` (YAML boolean), not `mode: off` (string). The fix is to edit the YAML directly:

  ```bash
  # After `coding config set approvals.mode off` wrongly sets `mode: false`:
  grep -A2 "approvals:" ~/.hermes/profiles/coding/config.yaml
  # → mode: false
  
  # Fix with patch:
  patch --mode replace --path ~/.hermes/profiles/coding/config.yaml \
    --old-string "  mode: false" \
    --new-string "  mode: off"
  ```

  Or use `hermes config edit` to fix it manually. Always verify after setting:
  ```bash
  grep -A2 "approvals:" ~/.hermes/profiles/<name>/config.yaml
  ```

- **Profile wrapper commands** (`coding chat`, `coding config set`) use the profile's own config.yaml, not the default profile's.

## Shell Environment Inheritance

A common confusion: **Hermes terminal sessions are non-interactive, non-login shells.** They do NOT load `.zshrc`, `.bashrc`, `.bash_profile`, or shell hooks. This means:

| What works (file-based) | What does NOT work (shell-function-based) |
|-------------------------|------------------------------------------|
| `gh` CLI (token in `~/.config/gh/`) | `nvm` (shell function in `.zshrc`) |
| `aws configure` (credentials in `~/.aws/`) | `direnv` (shell hook) |
| `gcloud auth` (token on disk) | `eval "$(rbenv init -)"` |
| `.npmrc` / `~/.netrc` | `source venv/bin/activate` |
| `npm ls -g` (node_modules on disk) | Any shell alias or function |

**Workarounds:**

- **nvm** — always source it explicitly before commands:
  ```bash
  export NVM_DIR="$HOME/.nvm"
  [ -s "$NVM_DIR/nvm.sh" ] && \. "$NVM_DIR/nvm.sh"
  nvm use lts/krypton
  ```

- **venv/conda** — activate inline:
  ```bash
  source ~/project/.venv/bin/activate && python -m pytest
  ```

- **Auth tokens for interactive CLIs** — prefer file-based credential storage (`gh auth login`, `aws configure`, etc.) rather than shell-script token injection. Token files survive across shell sessions.

- **PTY mode** — for interactive tools like `codex` or `claude-code` that need a pseudo-terminal, use `pty=true` in terminal calls. This still won't load shell configs, but gives the tool a proper TTY.

See `references/shell-environment-inheritance.md` for full details.

## Related Skills

- `hermes-agent` — full CLI reference for profiles, config, toolsets
- `writing-plans` — when tasks need a structured plan before execution
- `github-pr-workflow` — PR lifecycle automation
- `test-driven-development` — TDD workflow for coding sessions

## References

- `references/nvm-node-migration.md` — nvm Node LTS upgrade + global package migration (macOS/Linux)
- `references/exa-search-script.md` — Exa AI search API wrapper (`~/.hermes/scripts/exa_search.py`): config, usage, search types
- `references/shell-environment-inheritance.md` — why shell functions (nvm, direnv, venv) don't inherit in Hermes terminal sessions, and workarounds
