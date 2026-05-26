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

## Common Pitfalls

- **Name mismatch on delete**: displayed name ≠ SKILL.md name → check frontmatter
- **Git restore after delete**: switching branches restores deleted files → commit first
- **Plugin/global skills can't be deleted from profile**: some skills live outside the profile directory
