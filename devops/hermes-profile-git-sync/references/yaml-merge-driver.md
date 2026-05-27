# YAML Smart Merge Driver

`yaml-merge-driver.py` is a git merge driver that performs semantic 3-way deep merge of YAML config files, replacing git's default line-based merge.

## Why

Git's line-based merge produces conflict markers when both sides modify the same file. For config.yaml, this is especially problematic because:
- Two sides may add different providers/models — both should survive
- Two sides may change different scalar values within the same dict — both changes should be tracked
- Line-based merge treats the entire file as text and can't reason about structure

The YAML driver parses all three versions (base, ours, theirs) and merges them structurally.

## Merge Strategy

| Scenario | Behavior |
|----------|----------|
| Dict key added by ours only | Keep ours |
| Dict key added by theirs only | Keep theirs |
| Dict key in both, both same value | Keep (no conflict) |
| Scalar changed by ours only | Take ours |
| Scalar changed by theirs only | Take theirs |
| Scalar changed by both | Prefer ours |
| List changed by one side | Take changed side |
| List changed by both | Concatenate (ours + unique theirs items) |
| Non-dict/non-list conflict | Prefer ours |
| File is not valid YAML | Exit 1 (let git handle normally) |

## Test Example

```
Base:    providers.yunwu.models = {deepseek-v4-flash, qwen3.7-max}
Ours:    + gpt-5.5, deepseek-v4-flash context_length changed to 1048576
Theirs:  + mimo-v2.5-pro

Result:  {deepseek-v4-flash (ours' 1048576), qwen3.7-max, gpt-5.5 (ours), mimo-v2.5-pro (theirs)}
```

## Setup

### Per-repo git config

```bash
git config merge.yaml-merge.name "YAML semantic merge driver"
git config merge.yaml-merge.driver "python3 /Users/admin/.hermes/scripts/yaml-merge-driver.py %O %A %B %P"
```

### .gitattributes

```
config.yaml merge=yaml-merge
```

### Prerequisites

- Python 3 with `pyyaml` installed: `pip3 install pyyaml`

## Integration with Sync Cron

The `sync-profile.sh` and `sync-skills.sh` scripts auto-configure the merge driver and `.gitattributes` on first run. The flow:

1. Commit local changes (`git commit`)
2. Fetch remote
3. `git merge origin/main` — git invokes yaml-merge-driver.py for config.yaml automatically
4. For any remaining non-YAML conflicts: auto-resolve to local (`git checkout --ours`)
5. Push

This replaces the old `git pull --rebase=merges -X theirs` approach which could still leave structural conflict markers.
