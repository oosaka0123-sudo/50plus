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
- `scripts/render_listings.py` deterministically keeps generated listing markup synchronized with canonical JSON
- CI validates local links, common secret patterns, listing schema, JSON-to-HTML sync and stale verified event dates
- repository-native Browser QA uses pinned Playwright / Chromium against checked-out files served locally on the GitHub Actions runner
- Browser QA covers HOME, Activities, Listings, Guides, About, Contact and 404 at desktop and mobile viewports
- mobile navigation prevents focus entering a closed menu and restores focus to the trigger when Escape closes an open menu
- Claude Issue automation supports explicit ANALYSIS-ONLY MODE and normal IMPLEMENTATION MODE

## Publishing decision

The user has set a two-stage publishing plan.

### Stage A — now / during development

- Active public preview: `https://oosaka0123-sudo.github.io/ai-agent/50plus/`
- Preview host: the already-enabled GitHub Pages site of `oosaka0123-sudo/ai-agent`
- Source of truth: current `oosaka0123-sudo/50plus` `main`
- The ai-agent Pages build clones current public 50PLUS `main` read-only and generates only the runtime preview copy under its Pages artifact
- copied 50PLUS files are not committed into `ai-agent`
- all seven generated preview HTML pages are required to contain `noindex,nofollow`
- the bridge refreshes periodically from current 50PLUS `main`
- dedicated Pages for the `50plus` repository remains disabled; its local Pages workflow is retained as manual-only and is not the normal preview path
- Lolipop configuration is **not** a blocker during this stage

The bridge has been successfully deployed by the already-enabled ai-agent Pages workflow from both a review branch and merged ai-agent `main`, including seven HTML pages, CSS/JS validation, noindex verification, Pages artifact upload and deploy-pages success.

### Stage B — after completion

- Final production URL: `https://50plus.rss7.net`
- Final hosting: Lolipop
- Migration is performed only after the user explicitly considers 50PLUS complete and moves it to final production
- Existing manual Lolipop deployment/preflight paths are retained for that future stage
- retire the temporary ai-agent Pages bridge after successful final production unless the user explicitly wants to keep it

Do not prematurely switch the project back to Lolipop during normal development.

## Current incomplete handoff

### Browser-level preview observation

GitHub Actions deployment evidence for the active bridge is verified. If a task specifically requires browser-level live verification of a newly refreshed preview, distinguish that from Actions deployment evidence and use an available browser/web path rather than inventing visual confirmation.

### Claude authentication

Claude Issue automation still requires one supported repository authentication secret configured by the human owner before Claude can run.

Never invent, retrieve, copy into chat, commit, log or modify secret values.

### Claude independent review

A current open meta-review Issue is intended for Claude after authentication is available.

That task is explicitly **ANALYSIS ONLY**:
- repository reads are allowed
- repository file changes are forbidden
- no Branch / Commit / Pull Request should be created
- Claude should return only the requested analysis in the Issue conversation

## Current development rule

After reconciliation:

- continue ordinary development through Issue → Branch → checks → PR → Merge
- use `https://oosaka0123-sudo.github.io/ai-agent/50plus/` as the active development preview
- treat this 50PLUS repository as the sole source of truth; do not edit generated preview copies elsewhere
- use Browser QA as repository-native rendered evidence
- if Claude authentication becomes available, verify the analysis-only Claude task according to its current Issue
- do not request Lolipop secrets or trigger Lolipop deploy merely to continue development

## Future final migration rule

Only when the user explicitly says the site is complete / ready for final production:

1. confirm intended final `main`
2. require current PR/static checks and Browser QA evidence
3. human verifies the dedicated `50plus.rss7.net` Lolipop directory
4. human configures required Lolipop repository secrets
5. run Lolipop preflight
6. perform deliberate manual Lolipop deployment
7. verify final domain pages, SEO files and 404 behavior
8. retire the temporary ai-agent Pages bridge unless explicitly retained

## Do not store here

Do not copy into this file:
- raw chat transcripts
- secret values or credentials
- rolling lists of PR numbers, Merge SHAs or Actions run IDs
- duplicated specifications already owned by `PROJECT_SPEC.md`
- duplicated repeatable procedures already owned by `RUNBOOK.md`

Keep this file focused on unresolved cross-session constraints and resume decisions.
