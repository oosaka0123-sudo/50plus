# 50PLUS RUNBOOK

## Purpose

This file is the operational handoff for one-time setup and repeatable remote operation. GitHub is the SSOT; do not rely on chat memory when this file and current repository state are available.

## Council autopilot resume order

Before starting any new implementation task, read `COUNCIL.md` and resolve
priority in this order: an already-flagged `needs-human` Issue/PR, then any
unfinished PR of the current implementer (failing CI to fix, review to
request/confirm, merge readiness to confirm, deploy to verify, live
production to verify), then duplicate/stale active work, then blocked
Issues whose dependency resolved, then the next `ready` Issue by priority.
`scripts/autopilot_status.py` implements this precedence deterministically
from a GitHub-state snapshot; `.github/workflows/autopilot-watch.yml` runs
hourly to surface duplicate/stale active work without ever calling an LLM
or merging/deploying/deleting anything. Never start a second active
implementation task while an unfinished PR of your own exists.

## Publishing architecture

### Primary production — dedicated GitHub Pages

- Source repository / SSOT: `oosaka0123-sudo/50plus`
- Production URL: `https://oosaka0123-sudo.github.io/50plus/`
- Production host: dedicated GitHub Pages for this repository
- Production workflow: `.github/workflows/deploy-pages.yml`
- Source revision: approved `main`
- Search policy: production is indexable; preview-only `noindex,nofollow` must not ship

The production workflow runs on every `main` push and by manual dispatch. Dedicated Pages is already enabled.

The production artifact contains:
- `index.html`
- `activities.html`
- `listings.html`
- `guides.html`
- `about.html`
- `contact.html`
- `learning.html`
- `volunteering.html`
- `sports.html`
- `culture-library.html`
- `404.html`
- `assets/`
- `robots.txt`
- `sitemap.xml`
- `.nojekyll`

Before upload, the workflow verifies:
1. generated Listings HTML matches canonical JSON
2. production HTML does not contain preview-only `noindex,nofollow`
3. primary HTML carries the expected `https://oosaka0123-sudo.github.io/50plus` production origin
4. `robots.txt` references the production sitemap
5. `sitemap.xml` contains the production origin

### Optional future custom domain

`https://50plus.rss7.net` is not required for current GitHub Pages production. It may be added later as an optional custom domain while keeping GitHub Pages as the host.

If the user explicitly chooses that migration later:
1. Repository `Settings` -> `Pages`.
2. Set custom domain to `50plus.rss7.net`.
3. At the authoritative DNS provider for `rss7.net`, configure subdomain `50plus` as a CNAME to `oosaka0123-sudo.github.io`.
4. Wait for GitHub custom-domain/DNS verification.
5. Enable HTTPS when GitHub makes the option available.
6. Change canonical / OG / robots / sitemap production URLs in the same reviewed migration.
7. Live-verify the custom domain before declaring the migration complete.

Do not change unrelated `rss7.net` DNS records. Do not add a repository `CNAME` file merely to compensate for a custom Actions deployment.

### Temporary preview bridge

The existing `oosaka0123-sudo/ai-agent` GitHub Pages site may remain as a temporary preview bridge:

- Preview URL: `https://oosaka0123-sudo.github.io/ai-agent/50plus/`
- Source: current public `oosaka0123-sudo/50plus` `main`
- Search policy: generated preview HTML receives `noindex,nofollow`

The bridge is a publishing mechanism only. It does not become another source of truth, and preview deployment evidence must not be reported as production deployment evidence.

### Lolipop fallback

Existing workflows:
- `.github/workflows/deploy-preflight.yml`
- `.github/workflows/deploy-lolipop.yml`

These are retained as manual emergency fallback paths only. They are not the normal production route.

Do not request or configure Lolipop secrets for ordinary development or GitHub Pages production. Never enable destructive `mirror --delete` without a separately reviewed recovery/migration plan and explicit approval.

## Production deployment verification

For a production release, require:
1. intended changes are merged to `main`
2. relevant PR/static checks passed
3. Browser QA evidence is current when UI behavior/layout changed
4. `Deploy 50PLUS GitHub Pages` build succeeds
5. Pages artifact upload succeeds
6. `deploy-pages` succeeds
7. GitHub reports the expected deployment URL
8. browser/live verification confirms `https://oosaka0123-sudo.github.io/50plus/` and relevant SEO files

Do not claim a release complete from a merge alone.

## Claude Code Issue automation

### Observed live state

The repository contains `.github/workflows/claude-issue.yml`.

Live verification completed on 2026-09-04:
- an OWNER Issue comment containing `@claude` triggered the GitHub Actions workflow
- repository checkout succeeded
- the workflow stopped at the explicit authentication check
- Claude Code Action itself was skipped because no supported Anthropic authentication was configured in this repository

Therefore the trigger path is verified; the remaining blocker is authentication.

### Supported authentication inputs already wired

Configure **one** supported GitHub Actions repository secret:

Option A:
- `ANTHROPIC_API_KEY`

Option B:
- `CLAUDE_CODE_OAUTH_TOKEN`

Never write either secret value into Issues, PRs, commits, README, RUNBOOK, logs or chat screenshots.

### Human setup path in GitHub

Repository -> Settings -> Secrets and variables -> Actions -> New repository secret

After authentication is configured:
1. Open the target GitHub Issue.
2. Confirm no other Agent is actively working on the same Issue.
3. Read the Issue task mode before triggering Claude.
4. The repository OWNER posts a new comment containing `@claude`.
5. Confirm `Claude Code Issue Task` starts and authentication passes.
6. For `ANALYSIS ONLY`, Claude must not create/modify files, branches, commits or PRs.
7. For implementation tasks, Claude uses a dedicated branch, relevant checks and a PR.
8. Do not auto-merge implementation PRs without reviewing evidence.

## Rendered browser QA

### Workflow

`.github/workflows/browser-qa.yml`

Purpose:
- provide repeatable rendered desktop/mobile evidence without requiring a local browser
- test checked-out repository files through a local HTTP server on the GitHub Actions runner
- never depend on either the preview or production URL

Current coverage:
- HOME
- Activities
- Listings
- Guides
- About
- Contact
- Learning
- Volunteering
- Sports
- Culture/Library
- 404

Viewports:
- desktop: `1440x900`
- mobile: `390x844`

Checks include:
- successful local page response
- visible primary H1
- no horizontal page overflow
- desktop navigation state
- mobile menu closed/open state, keyboard Tab entry, Escape close and focus restoration
- reveal elements reaching their settled visible state before screenshots

Each run attempts to upload `browser-qa-screenshots` with full-page PNG evidence.

For UI-affecting PRs:
1. Wait for both `PR checks` and `Browser QA`.
2. Require both to pass before merge.
3. Review screenshots when layout/navigation/typography/spacing/interaction can change.

## Verified listings maintenance

### Source of truth

`data/verified-listings.json` is the canonical source for factual listing data.

Do not hand-edit the generated verified-listing cards in `listings.html`. The generated block is bounded by:
- `VERIFIED_LISTINGS_GENERATED_START`
- `VERIFIED_LISTINGS_GENERATED_END`

`scripts/render_listings.py` also owns the generated per-topic listing blocks in the four topic hub pages, filtered by each listing's `topics` field. Do not hand-edit these blocks either. Each is bounded by its own marker pair:
- `learning.html`: `TOPIC_LEARNING_GENERATED_START` / `TOPIC_LEARNING_GENERATED_END`
- `volunteering.html`: `TOPIC_VOLUNTEERING_GENERATED_START` / `TOPIC_VOLUNTEERING_GENERATED_END`
- `sports.html`: `TOPIC_SPORTS_GENERATED_START` / `TOPIC_SPORTS_GENERATED_END`
- `culture-library.html`: `TOPIC_CULTURE_GENERATED_START` / `TOPIC_CULTURE_GENERATED_END`

`python3 scripts/render_listings.py --check` validates that all five generated surfaces (`listings.html` plus the four topic hub pages) are in sync with `data/verified-listings.json`; it is run in PR checks and in the Pages deploy workflow.

### Update sequence

1. Re-check the official source before changing a listing.
2. Update only verified facts in `data/verified-listings.json`, including the `topics` field used to route listings to topic hub pages.
3. Update `verified_at` only when actually re-verified.
4. For events, maintain `start_date` and `end_date` in `YYYY-MM-DD`.
5. Run `python3 scripts/render_listings.py`.
6. Review the generated diff in `listings.html` and in any affected topic hub pages.
7. Run or wait for PR checks.
8. Merge only after JSON validation, HTML sync, local-link and secret-pattern checks pass.

### Automatic stale-event guard

The PR/static-check workflow also runs daily at `21:00 UTC` (06:00 JST).

A scheduled stale-event failure is a review signal only. Verify the official source, then deliberately remove, replace, archive or reclassify the record.

## Project boundary

50PLUS is an adult friendship/community discovery product, not a pickup, sexual-service, dating-optimization or matchmaking product.

Never fabricate live venue/event facts, schedules, prices, ratings, participant demographics, gender ratios, attendance, reviews or success rates.

## Operational rule

For implementation tasks prefer:
Issue -> Active Owner -> Branch -> Implementation -> Test -> PR -> Review -> Merge.

Before opening a new branch, check for an existing open PR/branch of your own per `COUNCIL.md`'s resume order; an unfinished PR (CI, review, merge, deploy, live-verify) always outranks starting new work.

For analysis-only tasks, follow the Issue's requested output without repository mutations.

For long AI sessions, update `HANDOFF.md` instead of depending on conversation history. `HANDOFF.md` remains a cache of unresolved cross-session context, not SSOT or history; current GitHub Issues/PRs/Actions always override it when they disagree.
