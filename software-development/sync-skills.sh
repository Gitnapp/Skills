#!/bin/bash
# Bi-directional sync for Gitnapp/Skills repo
# Run from: ~/.hermes/profiles/hermes-default/skills/software-development

set -e
cd "$(dirname "$0")"

echo "[sync-skills] $(date -u +%Y-%m-%dT%H:%M:%SZ)"

# Pull remote changes first
git fetch origin main
LOCAL=$(git rev-parse HEAD)
REMOTE=$(git rev-parse origin/main)

if [ "$LOCAL" != "$REMOTE" ]; then
    echo "[sync-skills] Pulling remote changes..."
    git pull --rebase origin main
else
    echo "[sync-skills] Already up to date."
fi

# Push any local unpushed commits
UNPUSHED=$(git rev-list origin/main..HEAD --count)
if [ "$UNPUSHED" -gt 0 ]; then
    echo "[sync-skills] Pushing $UNPUSHED local commit(s)..."
    git push origin main
fi

echo "[sync-skills] Done."
