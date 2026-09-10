# COUNCIL.md — 50PLUS 3-Agent Council Operating System

## Purpose

This file defines a realistic, non-stalling operating model for three
cooperating AI agents working on 50PLUS through GitHub as the single source
of truth (SSOT). It assumes none of the three agents run continuously or
forever. Any agent, in any session, must be able to read current GitHub
state plus this file and determine the single correct next action without
guessing at unseen chat history.

This file is the canonical definition of the council process. `AGENTS.md`,
`RUNBOOK.md` and `HANDOFF.md` reference it and must not redefine it
differently. `.github/autopilot-policy.json` is the machine-readable mirror
of the state machine, priorities and limits defined here; if they ever
disagree, treat that as a bug and reconcile them in the same change.

## Roles

| Role | Agent | Responsibility | Cannot do |
|---|---|---|---|
| PM / Orchestrator | ChatGPT | Prioritizes backlog, writes/refines Issues, requests council review, decides what ships next, escalates to human | Cannot be the sole implementer of a task it is orchestrating |
| Implementer | Claude (single owner) | Owns exactly one active implementation task at a time: branch, code, local checks, PR, fixes its own CI failures | Must not start a second active task while one is unresolved; must not silently hand its branch to another agent |
| Reviewer / Red-team | Gemini | Independent review of PRs for correctness, safety-boundary and security concerns; may flag risk the implementer missed | Must not implement fixes directly on the implementer's branch; may only comment/request changes |

None of the three agents is assumed to be online continuously. Each may run
only when invoked (chat session, scheduled workflow, Issue comment trigger).
The system must stay correct across arbitrary gaps between agent turns.

## Single-owner rule

- At most one Issue may be in an active implementation state (`active`,
  `ci`, `review`) with a given implementer at a time, per implementer.
- Before starting new implementation work, the implementer must check for
  its own open PRs / branches referencing other Issues. If one exists and
  is unresolved, that work takes priority over starting anything new.
- If two branches/PRs are found for the same Issue (duplicate active task),
  do not silently pick one. Record it and route to `needs-human` unless the
  duplicate is trivially resolvable (e.g. one branch has no commits ahead
  of `main` and can be safely abandoned by the same owner). This detection
  must happen before any per-PR resolution (fix CI / request review / etc.)
  is attempted on either duplicate — an implementer or the resolver script
  must never resolve one of the duplicate PRs' state first and flag the
  duplication as an afterthought.
- Competing implementation is only acceptable when the PM explicitly labels
  an Issue for intentional competition mode; this is expected to be rare
  and is out of scope for the default autopilot flow.

## State machine

```
ready -> council -> active -> ci -> review -> merge -> deploy -> live-verify -> done
```

Side states reachable from any of the above: `retry`, `blocked`, `needs-human`.

| State | Meaning | Entered when | Exited when |
|---|---|---|---|
| `ready` | Issue is scoped, acceptance criteria exist, no implementer assigned yet | PM finishes writing/refining the Issue | Implementer starts a branch |
| `council` | PM has requested pre-implementation council input (design/risk) before code starts | Issue is ambiguous, risky, or explicitly requests council-first review | Council concurs on approach, or PM decides low-risk and proceeds without full council |
| `active` | Implementer is writing code on a dedicated branch | Implementer begins work | PR opened and checks triggered |
| `ci` | PR exists, automated checks (PR checks / Browser QA / etc.) are running or have failed and await a fix | PR opened or checks re-run after a push | All required checks pass |
| `review` | Checks are green; awaiting Gemini (or documented-unavailable) review, and PM sign-off for merge readiness | CI passes | Review completed (or recorded unavailable for low-risk) and no unresolved change requests |
| `merge` | PR is approved/ready and awaiting a human or an explicitly authorized action to merge | Review complete | PR is merged into `main` |
| `deploy` | Merge landed on `main`; production deploy workflow is expected to run | PR merged | `Deploy 50PLUS GitHub Pages` run concludes |
| `live-verify` | Deploy workflow succeeded; production URL/content must be confirmed live | Deploy workflow reports success | Production URL/content verified to reflect the change |
| `done` | Change is implemented, merged, deployed and live-verified | Live verification confirmed | (terminal) |
| `retry` | A bounded, same-owner retry is in progress after a transient failure | A check fails and retry budget remains | Retry succeeds (return to prior state) or budget is exhausted (`blocked`) |
| `blocked` | Retry budget exhausted, or an external dependency is not ready | Retry limit hit, or a declared dependency Issue is still open | Blocker is resolved and work resumes from the state it was blocked in |
| `needs-human` | A condition in "Human-only escalation" is met | Any agent detects such a condition | A human takes the required action and updates GitHub state |

This repository never auto-merges. `merge` always ends with a human or an
explicitly authorized human-approved action, never an autonomous agent
action.

## Priority order on resume

Any agent (or the scheduled watcher) resuming work must evaluate, in this
exact order, and act on the first match:

1. **Sensitive/ambiguous state already flagged** — if any open Issue/PR is
   already labeled `needs-human`, do not act on it; only a human resolves it.
2. **Unfinished PR in `ci`/`review`/`merge`/`deploy`/`live-verify`** — an
   existing open PR always outranks starting a new Issue. Resume it,
   in this internal order: fix failing CI myself (if I am the PR owner) >
   confirm/request review > confirm merge readiness > verify deploy >
   verify live production. **Exception:** if an Issue currently has more
   than one open PR (duplicate active task), none of that Issue's PRs are
   resolved here — resolving any single one of them would mean silently
   picking a winner, which the single-owner rule forbids. Those PRs fall
   through to step 3 instead.
3. **Stale or duplicate active work** — an Issue/PR with no activity beyond
   the policy's stale TTL, or more than one active branch/PR for the same
   Issue, must be surfaced (comment + label) before anything else proceeds
   on that Issue. Duplicate detection runs before any of the duplicate
   Issue's individual PRs are picked and acted on (see the exception in
   step 2) — detection must happen strictly before selection.
4. **`retry`/`blocked` Issues whose blocker is now resolved** — resume from
   the state they were blocked in.
5. **Next `ready` Issue by declared priority** — only when nothing above
   applies. Pick by: explicit `priority` field (high > medium > low), then
   dependency order (an Issue depending on another open Issue is not
   started), then oldest `ready` Issue first.
6. **Nothing to do** — report clean status; do not invent work.

A new implementation task must never be started while step 2 or 3 has an
unresolved match. This is the core anti-stalling, anti-duplication rule.

## Council checkpoints

Council (multi-agent) input is required at these points, not continuously:

1. **Before `active`** for any Issue marked `risk: medium` or `risk: high`,
   or where acceptance criteria are ambiguous — PM confirms scope, Claude
   confirms approach is implementable, Gemini flags foreseeable risk before
   code is written.
2. **Before `merge`** for any Issue marked `risk: medium` or `risk: high` —
   Gemini review must be recorded (approval or documented change requests
   resolved) before merge proceeds.
3. **On any `needs-human` trigger** — council agents stop and hand off; they
   do not attempt to route around a human-only condition.

`risk: low` Issues do not require a pre-implementation council checkpoint
and may proceed straight from `ready`/`council`(skipped) to `active`.

## Reviewer-unavailable rule

- `risk: low` work may continue through `merge` if Gemini (or another
  designated reviewer) is temporarily unavailable, **provided** the
  unavailability is recorded on the PR (comment or label,
  e.g. `review-unavailable`) so the gap is visible in GitHub history.
- `risk: medium` and `risk: high` work must NOT merge without a recorded
  council review. If the reviewer is unavailable, the Issue/PR moves to
  `blocked` (reviewer dependency) rather than being merged unreviewed.

## Bounded retries

- Each check failure gets at most **3** automated same-owner retry attempts
  (matches `retry_limit` in `.github/autopilot-policy.json`) before moving
  to `blocked`.
- A retry means: the same Claude owner investigates the failure, pushes a
  fix to the same branch, and re-triggers checks. It does not mean blindly
  re-running the same failing check without a code change.
- Retries are counted per PR, not per Issue, and reset only when a new root
  cause fix changes the failing check's outcome category (e.g. moving from
  a lint failure to a genuinely new, different failure does not reset the
  counter; it is still bounded by the same PR's total).
- When the retry budget is exhausted, the PR moves to `blocked` and must be
  surfaced (comment + label), not silently retried forever.

## Human-only escalation conditions

Any of the following stops autonomous progress immediately and moves the
Issue/PR to `needs-human`. No agent may act around these:

- Secrets, credentials, tokens, API keys, or any GitHub Actions secret
  configuration or rotation.
- Billing, spend limits, or paid-usage configuration for any external
  service.
- Destructive production or data changes (irreversible deletes, force
  pushes to `main`, disabling/deleting the production Pages site, mirror
  `--delete` style operations).
- Permissions, repository visibility, or access-control changes.
- DNS or domain ownership changes (including the optional
  `50plus.rss7.net` custom domain migration).
- Legal or safety-relevant content or policy decisions.
- Materially ambiguous business/product decisions that acceptance criteria
  do not already resolve (e.g. conflicting product-boundary interpretation).

Human-only escalation is deliberately narrow and must not be triggered by
file path alone for ordinary changes. `.github/autopilot-policy.json`
separates two distinct mechanisms so risk tier and human-only escalation
never get conflated:

- `human_only_path_patterns` — paths that are unambiguously one of the
  categories above regardless of content (actual secret/credential-looking
  filenames, `CNAME`). A match forces `needs-human` directly.
- `risk_elevating_path_patterns` — paths that matter for safety but are
  ordinary engineering/content changes (`.github/workflows/*`,
  `.github/autopilot-policy.json` itself, `robots.txt`, `sitemap.xml`,
  preflight scripts). A match only raises the PR's risk tier to the
  pattern's `min_risk`, which in turn requires council review before merge
  via the existing risk-based checkpoints — it does **not** by itself stop
  autonomous progress or require a human.
- An explicit `human_only_reason` (set by the PM or implementer when a
  change is genuinely one of the seven categories above, e.g. it turns out
  a "workflow" change also rotates a secret) always forces `needs-human`,
  independent of path.

A `.github/workflows/*` or `robots.txt`/`sitemap.xml` change is therefore
`risk: high`/`risk: medium` requiring recorded council review before merge —
not an automatic human stop — unless it also matches a human-only pattern
or is explicitly flagged.

## GitHub as SSOT / HANDOFF as cache only

- Open Issues, open PRs, check runs and deployments in GitHub are the
  actual state of the system. This file, `HANDOFF.md`, and any local memory
  are caches that can go stale the moment GitHub changes.
- `HANDOFF.md` may record unresolved cross-session context (e.g. "PR #80 is
  mid-retry, blocked on X") but must never be treated as authoritative over
  a conflicting current GitHub state.
- `scripts/autopilot_status.py` computes the next action purely from a
  GitHub-shaped state snapshot (issues/PRs/checks/deployments), never from
  chat memory, so its output is reproducible by any agent or by the
  scheduled workflow.

## Non-goals

- This system does not make ChatGPT, Claude or Gemini run continuously or
  in the background between invocations.
- The scheduled watcher (`.github/workflows/autopilot-watch.yml`) does not
  call any paid LLM API. It only inspects GitHub state and posts a status
  summary; it never merges, deletes branches, or changes secrets/billing/
  DNS/permissions.
- Nothing here authorizes auto-merge. A human (or an explicitly authorized
  human action) always performs the actual merge.
