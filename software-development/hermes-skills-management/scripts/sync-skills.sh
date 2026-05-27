#!/bin/bash
# Bi-directional sync for Gitnapp/Skills repo
# Uses YAML semantic merge driver for *.yaml files
set -eo pipefail

SKILLS_DIR="$HOME/.hermes/profiles/hermes-default/skills/software-development"
CONFLICT_FILE="$HOME/.hermes/skills/.sync-conflict"
MERGE_DRIVER="$HOME/.hermes/scripts/yaml-merge-driver.py"

cd "$SKILLS_DIR"

echo "[sync-skills] $(date -u +%Y-%m-%dT%H:%M:%SZ)"

# Clean up old conflict flag (legacy)
rm -f "$CONFLICT_FILE"

# Ensure YAML merge driver is configured for this repo
if ! git config merge.yaml-merge.driver >/dev/null 2>&1; then
    git config merge.yaml-merge.name "YAML semantic merge driver"
    git config merge.yaml-merge.driver "python3 $MERGE_DRIVER %O %A %B %P"
fi

if [ ! -f .gitattributes ] || ! grep -q "merge=yaml-merge" .gitattributes 2>/dev/null; then
    echo "*.yaml merge=yaml-merge" >> .gitattributes
    git add .gitattributes 2>/dev/null || true
fi

# --- Phase 1: Commit local changes ---
git add -A
if ! git diff --cached --quiet; then
    echo "[sync-skills] Committing local changes..."
    git commit -m "sync: auto-commit $(date -u +%Y%m%dT%H%M%S)"
fi

# --- Phase 2: Fetch & merge ---
git fetch origin main
LOCAL=$(git rev-parse HEAD)
REMOTE=$(git rev-parse origin/main)

if [ "$LOCAL" = "$REMOTE" ]; then
    echo "[sync-skills] Already up to date."
else
    echo "[sync-skills] Merging remote..."
    if git merge origin/main -m "sync: auto-merge" 2>/dev/null; then
        echo "[sync-skills] Merge succeeded."
    else
        echo "[sync-skills] Non-YAML conflicts detected, keeping local version..."
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
    echo "[sync-skills] Pushing $UNPUSHED local commit(s)..."
    git push origin main
fi

echo "[sync-skills] Done."
