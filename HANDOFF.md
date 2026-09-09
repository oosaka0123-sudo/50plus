# 50PLUS — HANDOFF

Updated: 2026-09-09 JST

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
5. Reconcile current Open Issues, Open PRs, latest Actions and current code before choosing work.
6. If this handoff conflicts with current GitHub evidence, follow current GitHub evidence and update or retire this handoff as needed.

## Stable project foundation

The repository-side production foundation is in place:

- six primary public pages plus the project 404 page
- responsive static HTML / CSS / vanilla JavaScript
- adult friendship / community discovery positioning; not a dating, pickup or sexual-service product
- verified listing facts use `data/verified-listings.json` as canonical data
- `scripts/render_listings.py` deterministically keeps generated listing markup synchronized with canonical JSON
- CI validates local links, common secret patterns, listing schema, JSON-to-HTML sync and stale verified event dates
- repository-native Browser QA uses pinned Playwright / Chromium against checked-out files served locally on the GitHub Actions runner
- Browser QA covers HOME, Activities, Listings, Guides, About, Contact and 404 at desktop and 390px mobile viewports
- mobile navigation prevents focus entering a closed menu and restores focus to the trigger when Escape closes an open menu
- the visual system includes committed optimized lifestyle stills and two MP4 loops under `assets/media/`
- the home hero has a static poster/fallback and honors `prefers-reduced-motion`
- secondary video is user-controlled and not eagerly loaded
- generated-media provenance is kept in `assets/media/PROVENANCE.md`; no credentials belong in provenance or repository files
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

Dedicated GitHub Pages is active and operational. Do not call a release complete until the Pages workflow succeeds and live production is verified.

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

## Current cross-session state

There is **no active implementation task designated by this handoff**.

After the resume-order reconciliation, choose the next task from current GitHub evidence rather than from a completed task recorded in an old chat or handoff.

Important current constraints:

- Respect any Issue explicitly marked `ANALYSIS ONLY`: do not create or modify repository files, branches, commits, PRs or production for that Issue.
- Human-owned authentication/setup must never be assumed complete from an old note; verify the current Issue and current runtime state first.
- Google Media MCP has been verified end-to-end for 50PLUS. For future media work, reuse the existing infrastructure and repository-local MCP configuration; do not recreate Cloud Run / Vertex AI infrastructure merely because a stale note says approval is pending.
- Before future Google Media generation, follow current `CLAUDE.md` and repository preflight guidance. Never expose or persist bearer tokens or other secrets.
- Finished production media must remain static committed assets; page viewing must not depend on live AI generation.

### Re-entry message

`Read current ai-master and 50PLUS main, then reconcile current Open Issues, Open PRs and latest Actions before choosing work. HANDOFF has no active implementation task; use current GitHub evidence as the source of truth.`

## Current development rule

After reconciliation:

- continue ordinary development through Issue -> Branch -> checks -> PR -> Merge
- treat this 50PLUS repository as the sole project source of truth
- use Browser QA as repository-native rendered evidence
- use `https://oosaka0123-sudo.github.io/50plus/` for current live production verification
- use the `ai-agent` URL only as the temporary noindex preview bridge
- use the repository-local Pages workflow as the normal production publishing path
- keep Lolipop workflows only as manual fallback; do not request Lolipop secrets for routine publishing
- keep factual listing changes behind `data/verified-listings.json` and deterministic rendering

## Do not store here

Do not copy into this file:
- raw chat transcripts
- secret values or credentials
- rolling lists of PR numbers, Merge SHAs or Actions run IDs
- duplicated specifications already owned by `PROJECT_SPEC.md`
- duplicated repeatable procedures already owned by `RUNBOOK.md`

Keep this file focused on unresolved cross-session constraints and resume decisions.
