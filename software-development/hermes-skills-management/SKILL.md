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

Create a sync script at `~/.hermes/scripts/sync-skills.sh`:

```bash
#!/bin/bash
set -e
SKILLS_DIR="$HOME/.hermes/profiles/hermes-default/skills/software-development"
cd "$SKILLS_DIR"
echo "[sync-skills] $(date -u +%Y-%m-%dT%H:%M:%SZ)"
# Pull remote first
git fetch origin main
LOCAL=$(git rev-parse HEAD)
REMOTE=$(git rev-parse origin/main)
if [ "$LOCAL" != "$REMOTE" ]; then
    echo "[sync-skills] Pulling remote changes..."
    git pull --rebase origin main
fi
# Push local commits
UNPUSHED=$(git rev-list origin/main..HEAD --count)
if [ "$UNPUSHED" -gt 0 ]; then
    echo "[sync-skills] Pushing $UNPUSHED local commit(s)..."
    git push origin main
fi
echo "[sync-skills] Done."
```

Then create a cron job via `cronjob` tool: `no_agent=true, script="sync-skills.sh", schedule="every 5m"`. The script must live under `~/.hermes/scripts/` (cron enforces this). Keep a copy in the repo for versioning.

## Advanced Sync: Conflict Handling with Hermes Takeover

Full sync script at `~/.hermes/scripts/sync-skills.sh` (and versioned in the repo):

```bash
#!/bin/bash
set -eo pipefail
SKILLS_DIR="$HOME/.hermes/profiles/hermes-default/skills/software-development"
CONFLICT_FILE="$HOME/.hermes/skills/.sync-conflict"
cd "$SKILLS_DIR"

# Check for pending conflict flag (avoid stomping on Hermes mid-resolution)
[ -f "$CONFLICT_FILE" ] && echo "[sync-skills] Pending conflict, deferring..." && exit 0

# 1. Stash uncommitted changes
git add -A
if ! git diff --cached --quiet; then
    git stash push -m "sync-skills auto-stash $(date -u +%Y%m%dT%H%M%S)"
fi

# 2. Pull with -X theirs (auto-resolve trivial conflicts, prefer remote)
git fetch origin main
if [ "$(git rev-parse HEAD)" != "$(git rev-parse origin/main)" ]; then
    if git pull --rebase=merges -X theirs origin main 2>.pull-err; then
        rm -f .pull-err
    else
        # Rebase failed → write conflict report for Hermes
        git rebase --abort 2>/dev/null || true
        cat > "$CONFLICT_FILE" <<HEREDOC
{"type":"rebase_conflict","repo":"$SKILLS_DIR","error":"$(head -20 .pull-err | tr '\n' ' ')"}
HEREDOC
        git stash pop 2>/dev/null || true
        exit 2  # Triggers Hermes takeover
    fi
fi

# 3. Restore stash → auto-commit → push
git stash pop 2>/dev/null && git add -A && git diff --cached --quiet || git commit -m "sync: auto-commit"
UNPUSHED=$(git rev-list origin/main..HEAD --count)
[ "$UNPUSHED" -gt 0 ] && git push origin main
```

### Hermes Conflict Resolver (cron, LLM-driven)

A second cron job runs every 6 minutes (offset from sync) and checks for `~/.hermes/skills/.sync-conflict`:

- `no_agent=false` (Hermes reasons about the conflict)
- `toolsets=["terminal","file","web"]`
- Prompt instructs: read conflict report → `git status` + `git log` both sides → merge intelligently (prefer remote, backup local to `.local-backup`) → commit + push → remove flag file
- If truly stuck, write to `.sync-conflict.unresolved`

### Cron Summary

| Job | Type | Schedule | What it does |
|-----|------|----------|--------------|
| `skills-bidirectional-sync` | no_agent (script) | every 5m | pull + push, flag conflicts |
| `skills-conflict-resolver` | LLM-driven | every 6m | read conflict flag, resolve, commit |

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

# Hooks (may contain secrets)
hooks/

# Skins (visual only)
skins/

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
- **.env encryption method**: user's default is Bitwarden + base64 (see `references/bitwarden-env-pattern.md`). Do NOT default to git-crypt — only use it if explicitly requested. If unsure, ask.
- **Plaintext .env in history**: if .env was pushed before encryption, rewrite history with `git-filter-repo` to remove secrets from all commits
- **Check for existing patterns first**: before choosing a tool/approach (encryption, sync, naming), check if the user has an established pattern in other profiles or prior sessions. Reusing existing patterns avoids rework and user frustration.
