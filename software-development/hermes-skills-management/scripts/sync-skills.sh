#!/bin/bash
# Bi-directional sync for Gitnapp/Skills repo
# Hermes takes over on conflict via .sync-conflict flag
set -eo pipefail

SKILLS_DIR="$HOME/.hermes/profiles/hermes-default/skills/software-development"
CONFLICT_FILE="$HOME/.hermes/skills/.sync-conflict"
cd "$SKILLS_DIR"

# Check for pending conflict flag
[ -f "$CONFLICT_FILE" ] && echo "[sync-skills] Pending conflict, deferring to Hermes..." && exit 0

echo "[sync-skills] $(date -u +%Y-%m-%dT%H:%M:%SZ)"

# Stash any uncommitted local changes
git add -A
if ! git diff --cached --quiet; then
    echo "[sync-skills] Stashing uncommitted changes..."
    git stash push -m "sync-skills auto-stash $(date -u +%Y%m%dT%H%M%S)"
fi

# Pull remote with auto-resolution: prefer remote on conflict
git fetch origin main
LOCAL=$(git rev-parse HEAD)
REMOTE=$(git rev-parse origin/main)

if [ "$LOCAL" != "$REMOTE" ]; then
    echo "[sync-skills] Pulling remote changes..."
    if git pull --rebase=merges -X theirs origin main 2>"$CONFLICT_FILE.pull"; then
        echo "[sync-skills] Pull succeeded."
        rm -f "$CONFLICT_FILE.pull"
    else
        echo "[sync-skills] CONFLICT: rebase failed."
        git rebase --abort 2>/dev/null || true
        cat > "$CONFLICT_FILE" <<EOF
{
  "type": "rebase_conflict",
  "local_sha": "$LOCAL",
  "remote_sha": "$REMOTE",
  "repo": "$SKILLS_DIR",
  "error": "$(head -20 "$CONFLICT_FILE.pull" | tr '\n' ' ' | sed 's/"/\\"/g')",
  "timestamp": "$(date -u +%Y-%m-%dT%H:%M:%SZ)"
}
EOF
        rm -f "$CONFLICT_FILE.pull"
        if git stash list | grep -q "sync-skills auto-stash"; then
            git stash pop 2>/dev/null || true
        fi
        echo "[sync-skills] Conflict flagged for Hermes resolution."
        exit 2
    fi
else
    echo "[sync-skills] Already up to date."
fi

# Restore stashed local changes
if git stash list | grep -q "sync-skills auto-stash"; then
    echo "[sync-skills] Restoring stashed changes..."
    if git stash pop 2>&1; then
        echo "[sync-skills] Stash applied cleanly."
    else
        cat > "$CONFLICT_FILE" <<EOF
{
  "type": "stash_conflict",
  "repo": "$SKILLS_DIR",
  "error": "stash pop failed; local and remote changes overlap",
  "timestamp": "$(date -u +%Y-%m-%dT%H:%M:%SZ)"
}
EOF
        echo "[sync-skills] Stash conflict flagged for Hermes resolution."
        exit 2
    fi
fi

# Commit any uncommitted changes
git add -A
if ! git diff --cached --quiet; then
    echo "[sync-skills] Committing synced changes..."
    git commit -m "sync: auto-commit from bidirectional sync"
fi

# Push local commits
UNPUSHED=$(git rev-list origin/main..HEAD --count)
if [ "$UNPUSHED" -gt 0 ]; then
    echo "[sync-skills] Pushing $UNPUSHED local commit(s)..."
    git push origin main
fi

echo "[sync-skills] Done."
