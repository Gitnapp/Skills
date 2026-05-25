---
name: garage-elys-agent-governance
description: "garage-elys agent governance: maintain GitHub Issue, Project, Milestone, PR hygiene before declaring work complete."
version: 1.0.0
author: Eric + Hermes
platforms: [macos, linux]
metadata:
  hermes:
    tags: [garage-elys, github, issues, projects, milestones, pr, governance]
    related_skills: [github-issues, github-pr-workflow, linear, kanban-orchestrator]
---

# garage-elys Agent Governance

Use this skill for any `garage-elys` coding or triage work. The goal is to keep GitHub Issues, Projects, Milestones, and PRs synchronized automatically.

## Non-negotiable rule

A coding task is NOT done when code is written. It is done only when:

1. PR is created and linked with `Closes #ISSUE` or a clearly documented exception.
2. Linked Issue's `Agent Context` block is updated.
3. Issue has correct type / area / priority / agent-state labels.
4. Issue has a milestone or an explicit `no-milestone` note.
5. Project status is updated, or the agent states that GitHub Project scope is missing.
6. CI status is checked and summarized.
7. Review state is checked and summarized.

## Source files

In the repo:

- `.github/AGENT_GOVERNANCE.md` — human-readable policy
- `.github/agent-routing.yml` — machine-readable routing rules
- `.github/ISSUE_TEMPLATE/*.yml` — issue forms with agent context marker
- `.github/PULL_REQUEST_TEMPLATE.md` — PR hygiene checklist

Additional operational setup notes live in `references/production-setup-runbook.md` — read it when bootstrapping labels/milestones/cron agents, handling missing GitHub Project scopes, or interpreting GitHub Actions billing failures.

Always read `.github/agent-routing.yml` before classifying issues.

## Issue state labels

Use exactly one main agent state label whenever possible:

- `agent:needs-context` — Issue lacks enough context or acceptance criteria.
- `agent:ready` — Issue is enriched and ready for implementation.
- `agent:in-progress` — Agent or human is actively implementing.
- `agent:needs-review` — PR exists or implementation is ready for review.
- `agent:blocked` — Waiting on user/external service/missing access.
- `agent:done` — PR merged / issue resolved.

Execution labels:

- `agent-eligible` — Agent can work on it.
- `human-only` — Do not start autonomous coding.
- `needs-triage` — Steward couldn't classify confidently.

## Agent Context block

Agents only update content between:

```md
<!-- agent-context:start -->
...
<!-- agent-context:end -->
```

If the block is missing, append it to the issue body.

Required sections:

```md
<!-- agent-context:start -->
## Agent Context

### Classification
- Type:
- Area:
- Priority:
- Project:
- Milestone:
- Agent eligible:

### Problem Summary

### Source Context
- Relevant files:
- Related issues:
- Related PRs:
- Design links / docs:

### Acceptance Criteria
- [ ]

### Implementation Plan
1.

### PR / Execution
- Branch:
- PR:
- CI:
- Review:

### Agent Notes
<!-- agent-managed-log:start -->
<!-- agent-managed-log:end -->
<!-- agent-context:end -->
```

Never overwrite user-authored requirement text outside this block.

## Context Steward workflow

For each open issue that is missing context, has `needs-triage`, has `agent:needs-context`, or lacks type/area/priority labels:

1. Read issue title/body/comments.
2. Read `.github/agent-routing.yml`.
3. Search the repo for referenced files, symbols, routes, screens, services.
4. Search related GitHub issues/PRs by keywords.
5. Update labels and milestone.
6. Add/update Agent Context block.
7. Comment only when a human decision is needed or when a material classification happened.
8. If ready for agent work, set `agent:ready`; if not, set `agent:needs-context` or `needs-triage`.

## PR Steward workflow

For each open PR:

1. Parse linked issue from PR body (`Closes #N`, `Fixes #N`, `Resolves #N`, or `Refs #N`).
2. If missing linked issue, comment and mark as not ready.
3. Update linked issue:
   - `agent:in-progress` or `agent:needs-review`
   - PR link in Agent Context
   - CI/review status in Agent Context
4. Check CI via `gh pr view --json statusCheckRollup,mergeable,reviews`.
5. If CI failed, summarize failures and keep issue in progress.
6. If PR merged, set linked issue to `agent:done`, close if not auto-closed, and update project status if possible.

## GitHub Project access limitation

`gh project` requires OAuth scopes `read:project` and `project`. If those scopes are missing, do not fail the whole stewardship run. Instead:

1. Do all Issue/PR/Milestone/Label maintenance.
2. Comment or report: `GitHub Project sync skipped: gh token missing project/read:project scope`.
3. Ask the user to run:

```bash
gh auth refresh --hostname github.com -s project -s read:project
```

Then retry project sync.

## Milestone routing

Default routing:

- Moments / 朋友圈 → `Moments MVP`
- Leaderboard / 达人榜 → `Leaderboard MVP`
- identity / 双身份 / community_profiles → `Identity Architecture`
- IM / messaging / TUIKit / PushKit / CallKit → `IM / Messaging`
- mobile quality / haptics / Sentry / runtime flags → `Mobile Quality`
- UI / UX / 微信 / design → `Product UX`

If uncertain, leave milestone empty and mark `needs-triage`.

## PR body hygiene

Agent-created PRs must include:

```md
## Linked issue
Closes #N

## Project Hygiene
- [ ] Linked Issue Agent Context updated
- [ ] GitHub Project status updated to PR Open / Review, or blocked by missing project scope and noted in the Issue
- [ ] Milestone set on linked Issue, or explicitly marked no-milestone
- [ ] Labels updated: type / area / priority / agent state
- [ ] CI status checked and summarized
- [ ] Review requested or explicitly not needed
```

## Current repo details

Repo: `Gitnapp/garage-elys`
Local path: `/Users/eric/dev/garage-elys`
Base branch: `dev`
