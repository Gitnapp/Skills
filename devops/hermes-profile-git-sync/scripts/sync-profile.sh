#!/bin/bash
# Bi-directional sync for Hermes profile repos
# Uses YAML semantic merge driver for config.yaml
# Usage: SYNC_PROFILE=ctf bash sync-profile.sh
set -eo pipefail

PROFILE="${SYNC_PROFILE:?SYNC_PROFILE not set}"
PROFILE_DIR="$HOME/.hermes/profiles/$PROFILE"
MERGE_DRIVER="$HOME/.hermes/scripts/yaml-merge-driver.py"

cd "$PROFILE_DIR"

echo "[sync-profile:$PROFILE] $(date -u +%Y-%m-%dT%H:%M:%SZ)"

# Ensure YAML merge driver is configured for this repo
if ! git config merge.yaml-merge.driver >/dev/null 2>&1; then
    git config merge.yaml-merge.name "YAML semantic merge driver"
    git config merge.yaml-merge.driver "python3 $MERGE_DRIVER %O %A %B %P"
fi

if [ ! -f .gitattributes ] || ! grep -q "merge=yaml-merge" .gitattributes 2>/dev/null; then
    echo "config.yaml merge=yaml-merge" >> .gitattributes
    git add .gitattributes 2>/dev/null || true
fi

# --- Phase 1: Commit local changes ---
git add -A
if ! git diff --cached --quiet; then
    echo "[sync-profile:$PROFILE] Committing local changes..."
    git commit -m "sync: auto-commit $(date -u +%Y%m%dT%H%M%S)"
fi

# --- Phase 2: Fetch & merge ---
git fetch origin main
LOCAL=$(git rev-parse HEAD)
REMOTE=$(git rev-parse origin/main)

if [ "$LOCAL" = "$REMOTE" ]; then
    echo "[sync-profile:$PROFILE] Already up to date."
else
    echo "[sync-profile:$PROFILE] Merging remote..."
    if git merge origin/main -m "sync: auto-merge" 2>/dev/null; then
        echo "[sync-profile:$PROFILE] Merge succeeded."
    else
        echo "[sync-profile:$PROFILE] Non-YAML conflicts detected, keeping local version..."
        # Resolve remaining non-YAML conflicts: keep local version
        for f in $(git diff --name-only --diff-filter=U 2>/dev/null); do
            echo "  Resolving: $f (local wins)"
            git checkout --ours -- "$f" 2>/dev/null || true
            git add "$f" 2>/dev/null || true
        done
        git commit -m "sync: auto-merge (conflicts resolved)" 2>/dev/null || true
    fi
fi

# --- Phase 3: Push ---
UNPUSHED=$(git rev-list origin/main..HEAD --count 2>/dev/null || echo 0)
if [ "$UNPUSHED" -gt 0 ]; then
    echo "[sync-profile:$PROFILE] Pushing $UNPUSHED local commit(s)..."
    git push origin main
fi

echo "[sync-profile:$PROFILE] Done."
