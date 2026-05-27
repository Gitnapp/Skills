#!/bin/bash
# Bi-directional sync for Hermes profile repos
# Usage: SYNC_PROFILE=ctf bash sync-profile.sh
set -eo pipefail

PROFILE="${SYNC_PROFILE:?SYNC_PROFILE not set}"
PROFILE_DIR="$HOME/.hermes/profiles/$PROFILE"
cd "$PROFILE_DIR"

echo "[sync-profile:$PROFILE] $(date -u +%Y-%m-%dT%H:%M:%SZ)"

# Stash any uncommitted changes
git add -A
if ! git diff --cached --quiet; then
    git stash push -m "sync-profile auto-stash $(date -u +%Y%m%dT%H%M%S)"
fi

git fetch origin main
LOCAL=$(git rev-parse HEAD)
REMOTE=$(git rev-parse origin/main)

if [ "$LOCAL" != "$REMOTE" ]; then
    if git pull --rebase=merges -X theirs origin main 2>&1; then
        echo "[sync-profile:$PROFILE] Pull succeeded."
    else
        echo "[sync-profile:$PROFILE] CONFLICT: rebase failed. Aborting."
        git rebase --abort 2>/dev/null || true
        git stash pop 2>/dev/null || true
        exit 1
    fi
else
    echo "[sync-profile:$PROFILE] Already up to date."
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
    echo "[sync-profile:$PROFILE] Pushing $UNPUSHED local commit(s)..."
    git push origin main
fi

echo "[sync-profile:$PROFILE] Done."
