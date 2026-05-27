---
name: hermes-profile-git-sync
description: Sync Hermes Agent profiles to private GitHub repos with bidirectional cron jobs — push config, skills to Gitnapp/hermes-profile-{name}, auto-merge remote changes every 5 minutes using YAML semantic merge driver (no conflicts, no takeover needed). .env is gitignored (secrets).
version: 1.1.0
author: Hermes Agent
---

# Hermes Profile Git Sync

Sync Hermes profile configurations to GitHub repos for backup and cross-machine portability. Each profile gets its own private repo `hermes-{profile-name}` with bidirectional syncing via cron jobs.

## Trigger

Use when the user wants to:
- Sync Hermes profiles to GitHub
- Set up bidirectional profile sync
- Backup/restore Hermes profile configs across machines

## Setup (per profile)

### 1. Create GitHub repo

```bash
gh repo create Gitnapp/hermes-{name} --private -d "Hermes profile: {name}" --push=false
```

### 2. Init git in profile directory

```bash
cd ~/.hermes/profiles/{name}

cat > .gitignore <<'EOF'
# Secrets (CRITICAL: .env MUST be in .gitignore — committed .env gets corrupted)
.env

# Runtime state
state.db*
*.log
*.lock
*.pid
cache/
audio_cache/
image_cache/
context_length_cache.yaml
models_dev_cache.json
ollama_cloud_models_cache.json
sessions/
sandboxes/
interrupt_debug.log
processes.json
pasties/
workspace/
bin/
pairing/
auth.lock
hooks/
skins/
home/
cron/output/
lsp/
EOF

git init
git remote add origin https://github.com/Gitnapp/hermes-{name}.git
git add .gitignore config.yaml skills/ AGENTS.md SOUL.md profile.yaml plans/ memories/ 2>/dev/null
git commit -m "init: hermes-{name} profile"
git push -u origin main
```

### 3. Create sync script (YAML smart merge driver)

First, deploy the YAML smart merge driver that handles config.yaml conflicts semantically:

```bash
# The merge driver lives in ~/.hermes/scripts/yaml-merge-driver.py
# It does 3-way YAML deep-merge: both sides' new keys are kept, conflicting scalars prefer local
```

Write `~/.hermes/scripts/sync-profile.sh` (shared library):

```bash
#!/bin/bash
# Bi-directional sync for Hermes profile repos
# Uses YAML semantic merge driver for config.yaml
# Usage: SYNC_PROFILE=ctf bash sync-profile.sh
set -eo pipefail

PROFILE="${SYNC_PROFILE:?SYNC_PROFILE not set}"
PROFILE_DIR="$HOME/.hermes/profiles/$PROFILE"
MERGE_DRIVER="$HOME/.hermes/scripts/yaml-merge-driver.py"

cd "$PROFILE_DIR"

# Configure git merge driver for YAML files
if ! git config merge.yaml-merge.driver >/dev/null 2>&1; then
    git config merge.yaml-merge.name "YAML semantic merge driver"
    git config merge.yaml-merge.driver "python3 $MERGE_DRIVER %O %A %B %P"
fi

# Configure .gitattributes
if [ ! -f .gitattributes ] || ! grep -q "merge=yaml-merge" .gitattributes 2>/dev/null; then
    echo "config.yaml merge=yaml-merge" >> .gitattributes
    git add .gitattributes 2>/dev/null || true
fi

# Phase 1: Commit local changes
git add -A
if ! git diff --cached --quiet; then
    git commit -m "sync: auto-commit $(date -u +%Y%m%dT%H%M%S)"
fi

# Phase 2: Fetch & merge (YAML driver handles config.yaml semantically)
git fetch origin main
LOCAL=$(git rev-parse HEAD)
REMOTE=$(git rev-parse origin/main)

if [ "$LOCAL" != "$REMOTE" ]; then
    if git merge origin/main -m "sync: auto-merge" 2>/dev/null; then
        echo "Merge succeeded."
    else
        echo "Non-YAML conflicts, keeping local version..."
        for f in $(git diff --name-only --diff-filter=U 2>/dev/null); do
            git checkout --ours -- "$f" 2>/dev/null || true
            git add "$f" 2>/dev/null || true
        done
        git commit -m "sync: auto-merge (conflicts resolved)" 2>/dev/null || true
    fi
fi

# Phase 3: Push
UNPUSHED=$(git rev-list origin/main..HEAD --count 2>/dev/null || echo 0)
if [ "$UNPUSHED" -gt 0 ]; then
    git push origin main
fi
```

Per-profile wrapper (e.g., `~/.hermes/scripts/sync-ctf.sh`):

```bash
#!/bin/bash
export SYNC_PROFILE=ctf
exec bash /Users/admin/.hermes/scripts/sync-profile.sh
```

### 4. Register cron job (no_agent)

**Copy** (not symlink) the sync scripts into the profile's scripts directory:

```bash
cp ~/.hermes/scripts/sync-{name}.sh ~/.hermes/profiles/<profile>/scripts/
chmod +x ~/.hermes/profiles/<profile>/scripts/sync-{name}.sh
```

Then register:
```bash
hermes cron create "every 5m" --name sync-profile-{name} --script sync-{name}.sh --no-agent
```

> **Why copy, not symlink?** Cron resolves script paths relative to `~/.hermes/profiles/<profile>/scripts/` and **blocks any symlink that resolves outside that directory** ("Blocked: script path resolves outside the scripts directory"). Symlinks will silently fail with a path-resolution error.

## Git Workflow Rules

- **No branches** — always commit and push directly to `main`
- **No PRs** — repos are sync endpoints, not development repos
- **Use `git merge` (not rebase) with YAML smart merge driver** — config.yaml is deep-merged semantically: both sides' new keys are preserved, conflicting scalars prefer local. Non-YAML conflicts: local wins.
- **Configure `.gitattributes`** — `config.yaml merge=yaml-merge` in every sync repo
- **Use `.gitignore`** to exclude runtime state (state.db, sessions, cache, logs). CRITICAL: `.env` MUST be in .gitignore.
- **Use `git config merge.yaml-merge.driver`** — per-repo, pointing to `~/.hermes/scripts/yaml-merge-driver.py`

## What Gets Synced

| Include | Exclude |
|---------|---------|
| config.yaml | .env (secrets — MUST be in .gitignore) |
| skills/ | state.db (SQLite runtime) |
| AGENTS.md | sessions/ |
| SOUL.md | sandboxes/ |
| profile.yaml | cache/ |
| memories/ | logs/ |
| plans/ | workspace/ |
|  | skins/ |
|  | hooks/ |
|  | pairing/ |
|  | cron/output/ |
|  | lsp/ |

## References

- `references/yaml-merge-driver.md` — how the YAML 3-way deep-merge driver works, with test examples
- `references/merge-conflict-recovery.md` — recovering from git merge conflicts
- `scripts/sync-profile.sh` — the canonical sync script (used by all profile sync cron jobs)
- `scripts/yaml-merge-driver.py` — Python merge driver for config.yaml semantic merging

## Pitfalls

- **.env MUST be in .gitignore** — if .env is committed to git (especially as a symlink), sync may corrupt it into a self-referencing symlink loop: `~/.hermes/.env -> ~/.hermes/profiles/hermes-default/.env -> ~/.hermes/profiles/hermes-default/.env` (points to itself). This destroys all API keys. Always add `.env` to `.gitignore` before first sync. If corrupted, restore from snapshot: `cp ~/.hermes/profiles/hermes-default/state-snapshots/<latest>/.env ~/.hermes/profiles/hermes-default/.env`.
- **Profile .env files are symlinks** — ctf, finance, ppt, researcher profile `.env` files are symlinks to `hermes-default/.env`. Sync handles these through the hermes-default cron. Do NOT create real .env files in profile subdirectories — they will be out of sync.
- **config.yaml merge is semantic** — YAML driver deep-merges dicts from both sides. New keys from both branches survive. Don't manually resolve config.yaml conflicts — the driver handles them.
- **Non-YAML conflicts keep local** — if SKILL.md or other files conflict, the sync script auto-resolves to the local version. Manual review may still be needed for complex structural conflicts in non-YAML files.
- **Merge driver must be in git config** — each sync repo needs `git config merge.yaml-merge.driver` pointing to the Python driver. The sync script auto-configures this on first run.
- **.gitattributes is required** — without `config.yaml merge=yaml-merge` in `.gitattributes`, git falls back to line-based merge for config.yaml and will produce conflict markers.
- **Cron script path is profile-scoped** — `no_agent` cron jobs resolve scripts relative to `~/.hermes/profiles/<profile>/scripts/`, NOT `~/.hermes/scripts/`. Symlinks pointing outside the profile scripts dir are blocked. Always copy scripts into the profile scripts dir.
- **Dual-location maintenance** — canonical scripts live in `~/.hermes/scripts/` and are copied to profile scripts dirs. After editing the canonical, re-copy to all profile dirs.
- **Never edit a profile repo's config.yaml on GitHub** — the local Hermes instance is the source of truth. GitHub edits will be merged back (semantically), but expect surprises if both sides edit the same key.
- **First git init can be large** — skills directories contain many files. Expect 300-600 files in initial commit.
