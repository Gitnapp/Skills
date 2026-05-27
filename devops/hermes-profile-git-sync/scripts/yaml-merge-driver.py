#!/usr/bin/env python3
"""
Git merge driver for YAML config files.
Does a semantic 3-way deep merge instead of line-based merge.

Usage (called by git):
  yaml-merge-driver.py %O %A %B %P

  %O = ancestor (base)
  %A = current branch (ours)
  %B = other branch (theirs)
  %P = result path to write

Strategy:
- Scalar values: if changed on one side, take that; if both changed, prefer ours
- Dicts: recursively deep-merge — both sides' keys are kept
- Lists: if both changed, concatenate (ours first, then unique items from theirs)
- Non-YAML files: fall through with exit 1 (let git handle normally)
"""
import sys
import yaml
from copy import deepcopy


def deep_merge(base, ours, theirs):
    """3-way deep merge. Returns (merged, has_conflict)."""
    has_conflict = False

    # Both sides are dicts
    if isinstance(ours, dict) and isinstance(theirs, dict):
        result = {}
        all_keys = set(ours.keys()) | set(theirs.keys())

        for key in all_keys:
            in_ours = key in ours
            in_theirs = key in theirs
            in_base = isinstance(base, dict) and key in base

            if in_ours and in_theirs:
                if isinstance(ours[key], dict) and isinstance(theirs[key], dict):
                    base_val = base.get(key, {}) if isinstance(base, dict) else {}
                    result[key], conflict = deep_merge(base_val, ours[key], theirs[key])
                    has_conflict = has_conflict or conflict
                elif ours[key] == theirs[key]:
                    result[key] = ours[key]
                elif in_base and ours[key] == base.get(key):
                    # Ours unchanged, theirs changed → take theirs
                    result[key] = theirs[key]
                elif in_base and theirs[key] == base.get(key):
                    # Theirs unchanged, ours changed → take ours
                    result[key] = ours[key]
                else:
                    # Both changed → prefer ours
                    result[key] = ours[key]
            elif in_ours:
                result[key] = ours[key]
            else:
                result[key] = theirs[key]

        return result, has_conflict

    # Both sides are lists
    if isinstance(ours, list) and isinstance(theirs, list):
        if ours == theirs:
            return ours, False
        # Concatenate: ours first, then unique items from theirs
        result = list(ours)
        for item in theirs:
            if item not in result:
                result.append(item)
        return result, False

    # Scalars or different types
    if ours == theirs:
        return ours, False
    if base is not None and ours == base:
        return theirs, False
    if base is not None and theirs == base:
        return ours, False
    # Both changed → prefer ours
    return ours, False


def main():
    if len(sys.argv) != 5:
        print("Usage: yaml-merge-driver.py %O %A %B %P", file=sys.stderr)
        sys.exit(1)

    base_path, ours_path, theirs_path, result_path = sys.argv[1:5]

    try:
        with open(base_path) as f:
            base = yaml.safe_load(f) or {}
        with open(ours_path) as f:
            ours = yaml.safe_load(f) or {}
        with open(theirs_path) as f:
            theirs = yaml.safe_load(f) or {}
    except yaml.YAMLError as e:
        # Not valid YAML — let git handle it normally
        print(f"yaml-merge-driver: YAML parse error, falling through: {e}", file=sys.stderr)
        sys.exit(1)

    merged, has_conflict = deep_merge(base, ours, theirs)

    with open(result_path, 'w') as f:
        yaml.dump(merged, f, default_flow_style=False, allow_unicode=True, sort_keys=False)

    if has_conflict:
        print("yaml-merge-driver: merged with conflicts (ours preferred)", file=sys.stderr)
    else:
        print("yaml-merge-driver: clean merge", file=sys.stderr)

    sys.exit(0)


if __name__ == "__main__":
    main()
