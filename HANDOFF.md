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

The user has decided to use **dedicated GitHub Pages as the production host and the standard GitHub Pages URL as the current production URL**.

### Current production

- Production URL: `https://oosaka0123-sudo.github.io/50plus/`
- Production host: dedicated GitHub Pages for `oosaka0123-sudo/50plus`
- Source of truth: current `oosaka0123-sudo/50plus` `main`
- Production workflow: `.github/workflows/deploy-pages.yml`
- Production artifact is indexable and does not contain preview-only `noindex,nofollow`
- canonical URLs, `og:url`, `robots.txt` and `sitemap.xml` must match the current GitHub Pages production URL
- Lolipop is not the normal production host for this project

### Dedicated Pages activation evidence

Observed on 2026-09-06 JST:

- Repository `Settings -> Pages` is authenticated and accessible.
- Pages publishing `Source` is **GitHub Actions**.
- production workflow build and deploy have completed successfully.
- GitHub reported the environment URL as `https://oosaka0123-sudo.github.io/50plus/`.
- Browser-level live verification confirmed that URL renders the 50PLUS home page and navigation.

Dedicated GitHub Pages is active and operational.

### Optional future custom domain

`https://50plus.rss7.net` may be attached later as an optional custom domain while keeping GitHub Pages as the host. It is not a blocker for current production.

If the user explicitly chooses that migration later, treat it as a deliberate URL migration: configure GitHub Pages custom domain + DNS, update canonical/OG/robots/sitemap URLs in the same reviewed change, verify HTTPS, and live-verify the custom domain before calling that migration complete.

Do not change unrelated `rss7.net` DNS records.

### Temporary preview bridge

- Preview URL: `https://oosaka0123-sudo.github.io/ai-agent/50plus/`
- Preview host: existing `ai-agent` GitHub Pages bridge
- Preview source: current public `50plus/main`
- Preview remains `noindex,nofollow`
- Preview is not another source of truth and may be retired later if no longer useful

## Current incomplete handoff

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
- use `https://oosaka0123-sudo.github.io/50plus/` for current live production verification
- use the `ai-agent` URL only as the temporary noindex preview bridge
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
