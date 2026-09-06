# 50PLUS — HANDOFF

Updated: 2026-09-06 JST

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

The user has decided to use **dedicated GitHub Pages as the primary production host** while keeping the production URL `https://50plus.rss7.net`.

### Primary production

- Production URL: `https://50plus.rss7.net`
- Production host: dedicated GitHub Pages for `oosaka0123-sudo/50plus`
- Source of truth: current `oosaka0123-sudo/50plus` `main`
- Production workflow: `.github/workflows/deploy-pages.yml`
- Production must be indexable and must not contain preview-only `noindex,nofollow`
- `robots.txt` and `sitemap.xml` are production artifacts
- Lolipop is no longer the normal production host

### Temporary preview while activation is incomplete

- Preview URL: `https://oosaka0123-sudo.github.io/ai-agent/50plus/`
- Preview host: existing `ai-agent` GitHub Pages bridge
- Preview source: current public `50plus/main`
- Preview remains `noindex,nofollow`
- Preview evidence must not be reported as production evidence

### Activation progress

Observed on 2026-09-06 JST:

- Repository `Settings -> Pages` is authenticated and accessible.
- Pages publishing `Source` was changed from `Deploy from a branch` to **GitHub Actions** and GitHub displayed the saved confirmation.
- This completes the one-time repository source-selection step.

Remaining activation / production verification:

1. trigger or allow a fresh `Deploy 50PLUS GitHub Pages` run after the source change and require actual build + deploy success
2. verify the default dedicated Pages URL becomes live
3. configure custom domain `50plus.rss7.net`
4. configure DNS CNAME for `50plus` to `oosaka0123-sudo.github.io`
5. complete GitHub custom-domain/DNS verification and HTTPS enablement
6. live-verify the custom domain and SEO files

Until these are observed, do not claim final production activation is complete.

## Current incomplete handoff

### Dedicated Pages deployment / custom-domain live verification

The repository-side production workflow and Pages source selection are complete. The next required evidence is a fresh workflow run in which the production build and `deploy-pages` jobs actually execute successfully. After that, configure and verify `50plus.rss7.net` and its DNS/HTTPS state.

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

### Google Media MCP

A current blocker Issue tracks the Claude Code environment egress/client-token requirements for the existing Google Media MCP connection. Do not recreate the Cloud Run/Vertex infrastructure unless a later verified preflight proves a server-side blocker.

## Current development rule

After reconciliation:

- continue ordinary development through Issue -> Branch -> checks -> PR -> Merge
- treat this 50PLUS repository as the sole source of truth
- use Browser QA as repository-native rendered evidence
- use the `ai-agent` URL only as the temporary noindex preview until dedicated production is live-verified
- use the repository-local Pages workflow as the normal production publishing path
- keep Lolipop workflows only as manual fallback; do not request Lolipop secrets for routine publishing
- if Claude authentication becomes available, verify the analysis-only Claude task according to its current Issue

## Do not store here

Do not copy into this file:
- raw chat transcripts
- secret values or credentials
- rolling lists of PR numbers, Merge SHAs or Actions run IDs
- duplicated specifications already owned by `PROJECT_SPEC.md`
- duplicated repeatable procedures already owned by `RUNBOOK.md`

Keep this file focused on unresolved cross-session constraints and resume decisions.
