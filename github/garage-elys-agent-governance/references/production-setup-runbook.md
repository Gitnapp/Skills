# garage-elys governance production setup runbook

This reference captures the operational setup for Issue → Context → Project/Milestone → Agent → PR → Review governance.

## Required repository artifacts

The repo should contain:

- `.github/AGENT_GOVERNANCE.md` — human-readable policy
- `.github/agent-routing.yml` — routing rules used by steward agents
- `.github/ISSUE_TEMPLATE/*.yml` — issue forms with `Agent Context` marker
- `.github/PULL_REQUEST_TEMPLATE.md` — PR hygiene checklist

The `Agent Context` block is the only issue body section agents should edit automatically.

## Required labels

State labels:

- `agent:needs-context`
- `agent:ready`
- `agent:in-progress`
- `agent:needs-review`
- `agent:blocked`
- `agent:done`

Execution labels:

- `agent-eligible`
- `human-only`
- `needs-triage`
- `no-milestone`

Also ensure type/area/priority labels exist, including:

- `priority:urgent`
- `area:design`
- `area:product`

## Required milestones

Recommended garage-elys milestones:

- `Moments MVP`
- `Leaderboard MVP`
- `Identity Architecture`
- `IM / Messaging`
- `Mobile Quality`
- `Product UX`

## Steward cron agents

Coding profile should run these recurring jobs:

1. `garage-elys-issue-context-steward` — every 5m
   - Enriches open issues.
   - Adds/repairs labels, milestones, Agent Context.
   - Marks ready/needs-context/blocked.

2. `garage-elys-pr-steward` — every 5m
   - Parses PR linked issues.
   - Updates issue PR/CI/review state.
   - Comments on missing linked issues or CI failures.

3. `garage-elys-milestone-project-steward` — every 30m
   - Repairs drift across labels, milestones, agent state, and Project status.

All three should run with `profile: coding`, `workdir: /Users/eric/dev/garage-elys`, and load this skill.

## GitHub Project OAuth scope

`gh project` commands require scopes not included in normal repo auth.

If project sync fails with missing scopes, ask the user to run:

```bash
gh auth refresh --hostname github.com -s project -s read:project
```

Until that is done, steward agents should still maintain labels, milestones, issue body, PR comments, and CI summaries. Do not fail the whole run just because Project sync is unavailable.

## GitHub Actions billing / spending limit

If PR checks fail with:

```text
The job was not started because recent account payments have failed or your spending limit needs to be increased.
```

This is not a code/test failure. Steward behavior:

1. Comment on the PR explaining that CI did not start due to billing/spending limit.
2. Mention local validation already performed.
3. Keep PR/Issue state as blocked or needs-review depending on policy.
4. Ask the user to restore GitHub Actions billing/spending limit before expecting CI green.

Do not create code changes to fix this class of failure.

## Open issue triage pattern

For each open issue:

- If it is clear and implementable: set `agent:ready` + `agent-eligible`.
- If it is broad/ambiguous: set `agent:needs-context` + `needs-triage`.
- If it requires native credentials, signing, billing, product decision, or private access: set `human-only` and usually `agent:blocked`.
- If no milestone can be inferred, use `no-milestone` only when explicitly appropriate; otherwise `needs-triage`.
