---
name: hermes-profile-git-sync
description: Sync Hermes Agent profiles to private GitHub repos with bidirectional cron jobs — push config, skills, .env to Gitnapp/hermes-{name}, auto-pull remote changes every 5 minutes, Hermes agent takeover on conflicts.
version: 1.0.0
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
EOF

git init
git remote add origin https://github.com/Gitnapp/hermes-{name}.git
git add .gitignore config.yaml .env skills/ AGENTS.md SOUL.md profile.yaml plans/ memories/ 2>/dev/null
git commit -m "init: hermes-{name} profile"
git push -u origin main
```

### 3. Create sync script

Write `~/.hermes/scripts/sync-profile.sh` (shared library):

```bash
#!/bin/bash
set -eo pipefail

PROFILE="${SYNC_PROFILE:?SYNC_PROFILE not set}"
PROFILE_DIR="$HOME/.hermes/profiles/$PROFILE"
cd "$PROFILE_DIR"

git add -A
if ! git diff --cached --quiet; then
    git stash push -m "sync-profile auto-stash $(date -u +%Y%m%dT%H%M%S)"
fi

git fetch origin main
LOCAL=$(git rev-parse HEAD)
REMOTE=$(git rev-parse origin/main)

if [ "$LOCAL" != "$REMOTE" ]; then
    if git pull --rebase=merges -X theirs origin main 2>&1; then
        echo "Pull succeeded."
    else
        git rebase --abort 2>/dev/null || true
        git stash pop 2>/dev/null || true
        exit 1
    fi
fi

if git stash list | grep -q "sync-profile auto-stash"; then
    git stash pop 2>&1 || true
fi

git add -A
if ! git diff --cached --quiet; then
    git commit -m "sync: auto-commit from bidirectional sync"
fi

UNPUSHED=$(git rev-list origin/main..HEAD --count)
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
- **Always `git pull --rebase=merges -X theirs` before push** — prefer remote on conflict
- **Use `.gitignore`** to exclude runtime state (state.db, sessions, cache, logs)

## What Gets Synced

| Include | Exclude |
|---------|---------|
| config.yaml | state.db (SQLite runtime) |
| .env | sessions/ |
| skills/ | sandboxes/ |
| AGENTS.md | cache/ |
| SOUL.md | logs/ |
| profile.yaml | workspace/ |
| memories/ | skins/ |
| plans/ | hooks/ |
|  | pairing/ |

## References

- `references/merge-conflict-recovery.md` — recovery steps when `git pull --rebase` leaves conflict markers in config.yaml

## Pitfalls

- **Never edit a profile repo's config.yaml on GitHub** — the local Hermes instance is the source of truth. GitHub edits will be overwritten on next sync.
- **Check .env before pushing** — confirm no production secrets are exposed. Use `hermes config env-path` to locate.
- **First git init can be large** — skills directories contain many files. Expect 300-600 files in initial commit.
- **Cron script path is profile-scoped** — `no_agent` cron jobs resolve scripts relative to `~/.hermes/profiles/<profile>/scripts/`, NOT `~/.hermes/scripts/`. Symlinks to outside paths are blocked. Always copy scripts into the profile scripts dir.
- **Dual-location maintenance** — if you keep canonical scripts in `~/.hermes/scripts/` and copy them to profile dirs, remember to re-copy after edits. Consider making the profile scripts dir the single source of truth.
- **`rebase=merges -X theirs` can still leave conflict markers** — the `-X theirs` strategy resolves content-level conflicts but structural conflicts (e.g., same provider block defined differently in both histories) can leave `<<<<<<<` / `=======` / `>>>>>>>` markers embedded in the file. When this happens, the config becomes invalid YAML. Fix with a Python regex that strips conflict markers and keeps the "ours" (stashed) side:
  ```python
  import re
  raw = open('config.yaml').read()
  raw = re.sub(r'<<<<<<<[ \w]+\n(.*?)\n=======\n(.*?)\n>>>>>>>[ \w]+\n',
               lambda m: m.group(2), raw, flags=re.DOTALL)
  open('config.yaml', 'w').write(raw)
  ```
  Then manually rebuild any malformed YAML blocks. The `skills-conflict-resolver` cron job watches for `~/.hermes/skills/.sync-conflict` flag files but may not catch config-level conflicts — check all profile configs with `grep -rn "<<<<<<" ~/.hermes/profiles/*/config.yaml` after a sync cycle.
