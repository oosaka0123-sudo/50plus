# 50PLUS — HANDOFF

Updated: 2026-09-05 JST

## Purpose

This file is the project-local transient handoff for safely resuming 50PLUS work across ChatGPT / Claude Code / Jules / other approved agents.

GitHub is the SSOT. **Current `main`, Issues, Pull Requests, Actions and current repository files always override this handoff if anything has changed since it was written.**

Do not turn this file into a manual history log. Completed PR / commit / Actions history should be recovered from GitHub itself.

## Resume order

Before doing new work:

1. Read current `oosaka0123-sudo/ai-master` `README.md`, `AGENTS.md`, `PROJECTS.md`.
2. Confirm the current default branch of `oosaka0123-sudo/50plus`.
3. Read `AGENTS.md`, `README.md`, `PROJECT_SPEC.md`, `RUNBOOK.md` and this `HANDOFF.md`.
4. Claude Code also reads `CLAUDE.md`.
5. Reconcile current Open Issues, Open PRs, latest Actions and current code before acting.
6. If this handoff conflicts with current GitHub evidence, follow current GitHub evidence and update or retire this handoff as needed.

## Stable project foundation

The repository-side MVP foundation is in place:

- six primary public pages plus the project 404 page
- responsive static HTML / CSS / vanilla JavaScript
- adult friendship / community discovery positioning; not a dating, pickup or sexual-service product
- verified listing facts use `data/verified-listings.json` as canonical data
- `scripts/render_listings.py` deterministically keeps the generated listing block in `listings.html` synchronized with canonical JSON
- CI validates local links, common secret patterns, listing schema, JSON-to-HTML sync and stale verified event dates
- repository-native Browser QA uses pinned Playwright / Chromium against checked-out files served locally on the GitHub Actions runner
- Browser QA covers HOME, Activities, Listings, Guides, About, Contact and 404 at desktop and mobile viewports, including horizontal-overflow and navigation interaction checks plus screenshot artifacts
- mobile navigation prevents focus entering a closed menu and restores focus to the trigger when Escape closes an open menu
- Claude Issue automation supports two task modes: explicit ANALYSIS-ONLY MODE and normal IMPLEMENTATION MODE
- Lolipop deployment remains manual-only and does not use destructive mirror-delete behavior

Detailed durable behavior belongs in `PROJECT_SPEC.md` and `RUNBOOK.md`; do not duplicate those documents here unnecessarily.

## Current incomplete handoff

### Human configuration blocker

The remaining configuration involving secret values is intentionally human-owned and tracked by the current human-setup Issue.

At the last verified state:

- Claude authentication still required one supported repository secret to be configured by the human owner
- first Lolipop deployment still required the expected Lolipop repository secrets and verified dedicated server directory
- no secret values were exposed or stored in repository files
- production deployment had not been performed

**Never invent, retrieve, copy into chat, commit, log or modify secret values.** Re-check the current human-setup Issue and `RUNBOOK.md` before any authentication or deployment step.

### Claude independent review

A current open meta-review Issue is intended for Claude after authentication is available.

That task is explicitly **ANALYSIS ONLY**:

- repository reads are allowed
- repository file changes are forbidden
- no Branch / Commit / Pull Request should be created
- Claude should return only the requested analysis in the Issue conversation

The Claude workflow has been updated so explicit analysis-only task directives override the default implementation flow. Always re-read the current Issue body before triggering it.

## Before first production deployment

Do not treat repository readiness as production launch approval.

Before first deployment, verify the current `RUNBOOK.md` and require the current equivalent of all of these safeguards:

1. human confirms the `50plus.rss7.net` target and dedicated Lolipop public directory
2. required repository secrets are configured by the human owner without exposing values
3. Lolipop deployment preflight passes
4. current `main` passes PR/static checks as applicable
5. Browser QA is run on the intended current `main` release and screenshot evidence is reviewed
6. deployment remains a deliberate manual action
7. after deployment, verify the public site and required pages / 404 behavior

## Next-session decision rule

After reconciliation:

- if the human configuration blocker is still unresolved, do not attempt to bypass it; continue only independent safe work
- if Claude authentication is ready, verify the analysis-only Claude task according to its current Issue instructions
- if deployment configuration is ready, follow the current preflight and manual deploy sequence in `RUNBOOK.md`
- if new Issues / PRs / Actions have appeared, treat them as newer evidence than this handoff

## Do not store here

Do not copy into this file:

- raw chat transcripts
- secret values or credentials
- rolling lists of PR numbers, Merge SHAs or Actions run IDs
- duplicated specifications already owned by `PROJECT_SPEC.md`
- duplicated repeatable procedures already owned by `RUNBOOK.md`

Keep this file focused on information that a new session could not safely infer from completed GitHub history alone, especially unresolved handoff constraints and resume order.
