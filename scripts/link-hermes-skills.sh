#!/usr/bin/env bash
set -euo pipefail

# Links all skills in this repository to ~/.hermes/skills/<category>/<name>,
# so they can be used by Hermes CLI. Handles both default and named profiles.
#
# Usage:
#   ./scripts/link-hermes-skills.sh              # link default profile
#   ./scripts/link-hermes-skills.sh --all        # link all profiles
#   ./scripts/link-hermes-skills.sh --profile foo  # link specific profile

REPO="$(cd "$(dirname "$0")/.." && pwd)"
SKILLS_SRC="$REPO"
MODE="default"
PROFILE_NAME=""

while [[ $# -gt 0 ]]; do
  case "$1" in
    --all)   MODE="all"; shift ;;
    --profile) MODE="profile"; PROFILE_NAME="$2"; shift 2 ;;
    *) echo "Unknown flag: $1"; exit 1 ;;
  esac
done

link_into() {
  local dest="$1"
  echo "=== Linking into $dest ==="

  # Safety: if dest itself is a symlink into this repo, bail
  if [ -L "$dest" ]; then
    resolved="$(readlink -f "$dest" 2>/dev/null || readlink "$dest")"
    case "$resolved" in
      "$REPO"|"$REPO"/*)
        echo "error: $dest is a symlink into this repo. Remove it first: rm \"$dest\"" >&2
        return 1
        ;;
    esac
  fi

  mkdir -p "$dest"

  # Walk each category directory, link each skill
  find "$SKILLS_SRC" -mindepth 2 -name SKILL.md -not -path '*/node_modules/*' -not -path '*/deprecated/*' -print0 | \
  while IFS= read -r -d '' skill_md; do
    src="$(dirname "$skill_md")"
    # category = grandparent, name = parent
    name="$(basename "$src")"
    category="$(basename "$(dirname "$src")")"

    target="$dest/$category/$name"
    mkdir -p "$dest/$category"

    if [ -e "$target" ] && [ ! -L "$target" ]; then
      echo "  removing existing dir: $target"
      rm -rf "$target"
    fi

    ln -sfn "$src" "$target"
    echo "  linked $category/$name"
  done
  echo ""
}

case "$MODE" in
  default)
    link_into "$HOME/.hermes/skills"
    ;;
  profile)
    link_into "$HOME/.hermes/profiles/$PROFILE_NAME/skills"
    ;;
  all)
    link_into "$HOME/.hermes/skills"
    for prof_dir in "$HOME/.hermes/profiles"/*/; do
      [ -d "$prof_dir" ] || continue
      prof_name="$(basename "$prof_dir")"
      link_into "$prof_dir/skills"
    done
    ;;
esac

echo "Done. Run /reload-skills in Hermes, or restart the CLI."
