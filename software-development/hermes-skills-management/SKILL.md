---
name: hermes-skills-management
description: "Manage Hermes skills collection: add, delete, sync, and troubleshoot skills across profiles and git repos."
version: 1.0.0
author: Hermes Agent
---

# Hermes Skills Management

Manage the skills collection within a Hermes profile — adding, deleting, syncing with git, and troubleshooting.

## Trigger

Use when: listing skills, cleaning up skills, syncing skills to a repo, adding skills from external paths, or troubleshooting skill delete/add failures.

## Distinguishing Built-in vs Hub Skills

Check the SKILL.md frontmatter `author` field:

- **Hermes 自带**: `author: "Hermes Agent"` or `author: "Hermes"`, usually with a `version` field
- **Hub/external**: typically no `author` or `version`, may have a `license` field

```bash
head -5 SKILL.md  # check name, author, version
```

## Deleting Skills

### The name field matters

`skill_manage(action='delete', name=...)` uses the SKILL.md `name` field, NOT the directory name. They can differ (e.g., directory `vercel-deploy-claimable/` but displayed as "vercel-deploy").

If delete fails with "not found", check the actual SKILL.md name:

```bash
head -3 <skill-dir>/SKILL.md | grep '^name:'
```

### When skills live in a git repo

`skill_manage delete` removes files from disk. If you later `git checkout` a different branch, deleted files are restored. After deleting skills:
1. `git add -A` and commit immediately, OR
2. Do deletions directly via `rm -rf` + `git commit` to keep filesystem and git in sync

## Adding Skills From External Paths

Copy the entire skill directory into the profile's skills category:

```bash
cp -r /path/to/source/skills/<skill-name> \
  ~/.hermes/profiles/<profile>/skills/<category>/
```

Then run `hermes /reload-skills` to make Hermes pick it up (or start a new session).

## Git Sync Repo: Direct Push Only (No Branches, No PRs)

If the skills directory is a git repo used purely for sync (e.g., Gitnapp/Skills), **never create branches or PRs**. Always commit and push directly to `main`:

```bash
cd ~/.hermes/profiles/<profile>/skills/<category>
git add -A .
git commit -m "..."
git push origin main
```

The user's explicit rule: "不要创建分支，不要创建PR，直接Push和Pull就好了，这个仓库就是用来同步用的"

### Setting Up Bidirectional Sync

Create a sync script at `~/.hermes/scripts/sync-skills.sh`. Uses `git merge` with YAML semantic merge driver for `*.yaml` files (no more rebase, no more conflict markers):

```bash
#!/bin/bash
set -e
SKILLS_DIR="$HOME/.hermes/profiles/hermes-default/skills/software-development"
cd "$SKILLS_DIR"
git add -A && ! git diff --cached --quiet && git commit -m "sync: auto-commit"
git fetch origin main
if [ "$(git rev-parse HEAD)" != "$(git rev-parse origin/main)" ]; then
    git merge origin/main -m "sync: auto-merge" || true
fi
UNPUSHED=$(git rev-list origin/main..HEAD --count)
[ "$UNPUSHED" -gt 0 ] && git push origin main
```

Then create a cron job via `cronjob` tool: `no_agent=true, script="sync-skills.sh", schedule="every 5m"`. **The script must live under the profile's scripts directory** (`~/.hermes/profiles/<profile>/scripts/`), NOT `~/.hermes/scripts/`. Cron resolves script paths relative to the active profile and blocks symlinks pointing outside. Copy scripts, don't symlink.

## Advanced Sync: YAML Smart Merge (No Conflicts)

Full sync script at `~/.hermes/scripts/sync-skills.sh` (and versioned in the repo):

```bash
#!/bin/bash
# Bi-directional sync for Gitnapp/Skills repo
# Uses YAML semantic merge driver for *.yaml files
set -eo pipefail

SKILLS_DIR="$HOME/.hermes/profiles/hermes-default/skills/software-development"
MERGE_DRIVER="$HOME/.hermes/scripts/yaml-merge-driver.py"
cd "$SKILLS_DIR"

# Clean up old conflict flag
rm -f "$HOME/.hermes/skills/.sync-conflict"

# Ensure YAML merge driver is configured
if ! git config merge.yaml-merge.driver >/dev/null 2>&1; then
    git config merge.yaml-merge.name "YAML semantic merge driver"
    git config merge.yaml-merge.driver "python3 $MERGE_DRIVER %O %A %B %P"
fi

if [ ! -f .gitattributes ] || ! grep -q "merge=yaml-merge" .gitattributes 2>/dev/null; then
    echo "*.yaml merge=yaml-merge" >> .gitattributes
    git add .gitattributes 2>/dev/null || true
fi

# Phase 1: Commit local changes
git add -A
if ! git diff --cached --quiet; then
    git commit -m "sync: auto-commit $(date -u +%Y%m%dT%H%M%S)"
fi

# Phase 2: Fetch & merge
git fetch origin main
LOCAL=$(git rev-parse HEAD)
REMOTE=$(git rev-parse origin/main)

if [ "$LOCAL" != "$REMOTE" ]; then
    if git merge origin/main -m "sync: auto-merge" 2>/dev/null; then
        echo "Merge succeeded."
    else
        echo "Non-YAML conflicts, keeping local..."
        for f in $(git diff --name-only --diff-filter=U 2>/dev/null); do
            git checkout --ours -- "$f" 2>/dev/null || true
            git add "$f" 2>/dev/null || true
        done
        git commit -m "sync: auto-merge (conflicts resolved)" 2>/dev/null || true
    fi
fi

# Phase 3: Push
UNPUSHED=$(git rev-list origin/main..HEAD --count 2>/dev/null || echo 0)
[ "$UNPUSHED" -gt 0 ] && git push origin main
```

The YAML smart merge driver (`~/.hermes/scripts/yaml-merge-driver.py`) performs 3-way semantic deep merge:
- Both sides' new dict keys are preserved (no data loss)
- Conflicting scalars prefer local
- No more conflict markers — the driver resolves everything structurally

### Cron Summary

| Job | Type | Schedule | What it does |
|-----|------|----------|--------------|
| `skills-bidirectional-sync` | no_agent (script) | every 5m | commit → merge (YAML driver) → push |
| `sync-profile-{name}` × N | no_agent (script) | every 5m | per-profile config + skills sync (YAML driver) |
| `env-health-guard` | no_agent (script) | every 60m | .env health check + auto-recovery from snapshots |

The old `skills-conflict-resolver` cron is **deleted** — conflicts are now auto-resolved by the YAML merge driver.

## .env Health Guard

Deploy `~/.hermes/scripts/env-guard.sh` to monitor .env integrity and auto-recover:

```bash
#!/bin/bash
# Check .env health: missing, too small (<100 bytes), or symlink loop → restore from latest snapshot
set -eo pipefail

ENV_PATH="$HOME/.hermes/profiles/hermes-default/.env"
SNAPSHOT_DIR="$HOME/.hermes/profiles/hermes-default/state-snapshots"

# Detect if .env is a self-referencing symlink loop
if [ -L "$ENV_PATH" ]; then
    ENV_REAL=$(python3 -c "import os; print(os.path.realpath(os.path.expanduser('$ENV_PATH')))" 2>/dev/null)
    if [ "$ENV_REAL" = "$ENV_PATH" ]; then
        echo "SYMLINK LOOP DETECTED: $ENV_PATH -> itself"; BROKEN=true
    elif [ ! -f "$ENV_REAL" ]; then
        echo "BROKEN SYMLINK: $ENV_PATH -> $ENV_REAL (missing)"; BROKEN=true
    fi
elif [ ! -f "$ENV_PATH" ]; then
    echo "MISSING: $ENV_PATH"; BROKEN=true
else
    SIZE=$(wc -c < "$ENV_PATH" 2>/dev/null || echo 0)
    [ "$SIZE" -lt 100 ] && { echo "TOO SMALL: $ENV_PATH ($SIZE bytes)"; BROKEN=true; }
fi

if [ "${BROKEN:-false}" = true ]; then
    LATEST=$(ls -td "$SNAPSHOT_DIR"/*/ 2>/dev/null | head -1)
    [ -z "$LATEST" ] && { echo "FATAL: No snapshots found"; exit 1; }
    SNAPSHOT_ENV="$LATEST.env"
    [ ! -f "$SNAPSHOT_ENV" ] && { echo "FATAL: Snapshot not found at $SNAPSHOT_ENV"; exit 1; }
    cp "$SNAPSHOT_ENV" "$ENV_PATH" && chmod 600 "$ENV_PATH"
    [ -L "$HOME/.hermes/.env" ] && rm -f "$HOME/.hermes/.env"
    [ ! -f "$HOME/.hermes/.env" ] && ln -sf "$ENV_PATH" "$HOME/.hermes/.env"
    echo ".env recovered ($(wc -c < "$ENV_PATH") bytes)"
else
    echo ".env healthy ($(wc -c < "$ENV_PATH") bytes)"
fi
```

Register as `no_agent` cron: `every 1h`, script `env-guard.sh`.

## Profile-Level Sync (Entire Profile → GitHub)

Beyond syncing a single skills category, you can sync an entire Hermes profile (config.yaml, .env, skills/, AGENTS.md, SOUL.md, profile.yaml, memories/) to a dedicated GitHub repo.

### Repo Naming Convention

`hermes-profile-<name>` (e.g., `hermes-profile-ctf`, `hermes-profile-finance`)

### Setup Steps

1. Create private GitHub repo: `gh repo create Gitnapp/hermes-profile-<name> --private`
2. Init git in profile dir with proper `.gitignore`
3. Commit and push to main
4. Set up bidirectional sync cron (same pattern as skills sync)

### .gitignore for Profile Repos

```gitignore
# Runtime state
state.db*
*.log
*.lock
*.pid

# Cache
cache/
audio_cache/
image_cache/
context_length_cache.yaml
models_dev_cache.json
ollama_cloud_models_cache.json

# Sessions (too much noise)
sessions/
sandboxes/

# Temp/transient
interrupt_debug.log
processes.json
pasties/

# Workspace (user repos)
workspace/

# Binaries
bin/

# Pairing
pairing/
auth.lock
auth.json

# Memories
memories/

# Hermes runtime
.hermes_history
.update_check

# Hooks (may contain secrets)
hooks/

# Skins (visual only)
skins/

# Gateway state
gateway.lock
gateway.pid
gateway_state.json
channel_directory.json

# Cron runtime
cron/.tick.lock
cron/output/
cron/jobs.json

# LSP (auto-installed)
lsp/

# State snapshots (too heavy for git)
state-snapshots/

# Home (symlinks)
home/
```

### Sync Script Pattern

Use a parameterized script at `~/.hermes/scripts/sync-profile.sh` with per-profile wrappers:

```bash
# ~/.hermes/scripts/sync-<profile>.sh
#!/bin/bash
export SYNC_PROFILE=<profile>
exec bash ~/.hermes/scripts/sync-profile.sh
```

The main script reads `$SYNC_PROFILE` and operates on `~/.hermes/profiles/$SYNC_PROFILE/`.

### Cron Setup

One cron job per profile: `no_agent=true, script="sync-<profile>.sh", schedule="every 5m"`

## .env Encryption

`.env` files contain API keys and secrets. **Never push plaintext .env to GitHub**, even for private repos.

### User Preference: Bitwarden + base64 (DEFAULT)

The user has an established pattern of storing .env as base64-encoded secure notes in Bitwarden. **This is the default — use it unless explicitly told otherwise.**

See `references/bitwarden-env-pattern.md` for the full workflow:
- Store: base64 encode .env → create secure note named `hermes-profile-<name>-env`
- Retrieve: `bw get notes` → base64 decode → write to .env with `chmod 600`
- Update: re-encode → `bw edit item` → `bw sync`

**Do NOT default to git-crypt or other encryption methods** — the user expects Bitwarden + base64. If you're unsure, ask.

### git-crypt (Alternative — Only If Explicitly Requested)

If the user explicitly asks for git-crypt:
1. `git-crypt init` in the repo
2. Add `.env filter=git-crypt diff=git-crypt` to `.gitattributes`
3. Export key: `git-crypt export-key ~/.hermes/keys/hermes-profile-<name>.key`
4. Re-add .env: `git add .gitattributes .env && git commit`
5. On new machine: `git-crypt unlock ~/.hermes/keys/hermes-profile-<name>.key`

### Rewriting History

If .env was pushed in plaintext before encryption was added, use `git-filter-repo` to rewrite history and force-push. This removes secrets from all past commits.

## Common Pitfalls

- **Name mismatch on delete**: displayed name ≠ SKILL.md name → check frontmatter
- **Git restore after delete**: switching branches restores deleted files → commit first before changing branches
- **Plugin/global skills can't be deleted from profile**: some skills live outside the profile directory
- **Never branch/PR on sync repos**: the user uses the repo only for sync — direct push to main only, no branching, no PRs
- **Use HTTPS remotes, never SSH**: cron runs without SSH agent. `git@github.com:` remotes fail with "Permission denied (publickey)". Always use `https://github.com/...`. Fix: `git remote set-url origin https://github.com/Gitnapp/...`.
- **.env corruption via sync**: if .env is committed (especially as a symlink), it can become a self-referencing loop. Always add `.env` to `.gitignore`. Deploy `env-guard.sh` (see .env Health Guard section above) for hourly auto-recovery. Manual recovery: `cp ~/.hermes/profiles/hermes-default/state-snapshots/<latest>/.env ~/.hermes/profiles/hermes-default/.env`.
- **.env encryption method**: user's default is Bitwarden + base64 (see `references/bitwarden-env-pattern.md`). Do NOT default to git-crypt — only use it if explicitly requested. If unsure, ask.
- **Plaintext .env in history**: if .env was pushed before encryption, rewrite history with `git-filter-repo` to remove secrets from all commits
- **Check for existing patterns first**: before choosing a tool/approach (encryption, sync, naming), check if the user has an established pattern in other profiles or prior sessions. Reusing existing patterns avoids rework and user frustration.
- **Cron script path is profile-scoped**: `no_agent` cron jobs resolve scripts relative to `~/.hermes/profiles/<profile>/scripts/`, NOT `~/.hermes/scripts/`. Symlinks pointing outside the profile scripts dir are blocked ("Blocked: script path resolves outside"). Always copy scripts into the profile scripts dir — never symlink.
