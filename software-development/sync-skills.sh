#!/bin/bash
# Bi-directional sync for Gitnapp/Skills repo
set -eo pipefail

SKILLS_DIR="$HOME/.hermes/profiles/hermes-default/skills/software-development"
cd "$SKILLS_DIR"

echo "[sync-skills] $(date -u +%Y-%m-%dT%H:%M:%SZ)"

# Stash any uncommitted local changes before pulling
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
    if git pull --rebase=merges -X theirs origin main 2>&1; then
        echo "[sync-skills] Pull succeeded."
    else
        echo "[sync-skills] CONFLICT: rebase failed. Aborting and restoring..."
        git rebase --abort 2>/dev/null || true
        # Restore stash if any
        if git stash list | grep -q "sync-skills auto-stash"; then
            git stash pop 2>/dev/null || true
        fi
        echo "[sync-skills] ERROR: unable to sync. Manual intervention required."
        exit 1
    fi
else
    echo "[sync-skills] Already up to date."
fi

# Restore stashed local changes on top of pulled state
if git stash list | grep -q "sync-skills auto-stash"; then
    echo "[sync-skills] Restoring stashed changes..."
    if git stash pop 2>&1; then
        echo "[sync-skills] Stash applied cleanly."
    else
        echo "[sync-skills] CONFLICT: stash pop failed. Manual intervention required."
        exit 1
    fi
fi

# Commit any uncommitted changes (from stash restore)
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
