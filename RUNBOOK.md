# 50PLUS RUNBOOK

## Purpose

This file is the operational handoff for one-time setup and repeatable remote operation. GitHub is the SSOT; do not rely on chat memory when this file and current repository state are available.

## Publishing stages

### Current development preview

- Source repository / SSOT: `oosaka0123-sudo/50plus`
- Active preview URL: `https://oosaka0123-sudo.github.io/ai-agent/50plus/`
- Preview host: the already-enabled GitHub Pages site of `oosaka0123-sudo/ai-agent`
- Preview source: current public `oosaka0123-sudo/50plus` `main`
- Search policy: generated preview HTML is deployed with `noindex,nofollow`

The ai-agent Pages workflow is a **temporary publishing bridge only**. It reads 50PLUS `main` during the Actions run, generates the runtime preview under the Pages artifact, and does not commit copied 50PLUS website files into ai-agent.

The repository-local `.github/workflows/deploy-pages.yml` is manual-only while dedicated Pages for `oosaka0123-sudo/50plus` remains disabled. Do not trigger it during normal development merely to refresh the active preview.

### Final production target

- Final URL: `https://50plus.rss7.net`
- Final hosting: Lolipop
- Migration timing: only after the user considers the site complete and explicitly moves to final production

Lolipop configuration is **not** a blocker for current development. Do not trigger the Lolipop workflow or request Lolipop secrets during the GitHub Pages development stage.

## Active GitHub Pages preview bridge

### Source of truth

All product code, HTML, CSS, JavaScript, listing data and project rules remain in `oosaka0123-sudo/50plus`.

The bridge lives in the existing `oosaka0123-sudo/ai-agent` Pages workflow and performs a read-only clone of current public `50plus/main` during deployment. The generated preview copy is ephemeral and exists only in the Pages build workspace/artifact.

### Published runtime files

The bridge publishes under `/ai-agent/50plus/`:
- `index.html`
- `activities.html`
- `listings.html`
- `guides.html`
- `about.html`
- `contact.html`
- `404.html`
- `assets/`

It verifies that all seven HTML files exist and that `assets/styles.css` and `assets/main.js` exist before deployment.

### Search protection

The bridge injects this into every generated preview HTML page:

`<meta name="robots" content="noindex,nofollow">`

The injection is verified during the Actions run. Do not add this staging-only tag permanently to the 50PLUS source HTML; source canonical/OG metadata remains prepared for the final Lolipop domain.

### Refresh behavior

The bridge is scheduled from `ai-agent` and refreshes periodically by reading the latest 50PLUS `main`. A normal 50PLUS merge therefore does not need direct Pages enablement in this repository.

If an immediate preview refresh is needed, use the current ai-agent Pages workflow according to that repository's rules rather than changing the 50PLUS source-of-truth boundary.

### Verification rule

Do not claim a newly changed preview is refreshed merely because 50PLUS was merged. Check the relevant ai-agent Pages run and require:
1. current 50PLUS `main` clone succeeds
2. seven HTML pages/assets validation succeeds
3. `noindex,nofollow` verification succeeds
4. Pages artifact upload succeeds
5. `deploy-pages` succeeds

The bridge mechanism has been successfully executed from both its review branch and ai-agent `main`. Browser-level live rendering should still be distinguished from Actions deployment evidence when no browser observation is available.

## Dedicated 50PLUS Pages workflow — dormant/manual

`.github/workflows/deploy-pages.yml` is retained as a possible future dedicated Pages path but is **manual-only** while repository Pages remains disabled.

Do not re-enable automatic `main` push deployment here unless dedicated 50PLUS Pages is actually enabled and a successful deployment is verified. The active development preview does not depend on this workflow.

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

Repository → Settings → Secrets and variables → Actions → New repository secret

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
- never depend on either the GitHub Pages preview or the Lolipop production URL

Current coverage:
- HOME
- Activities
- Listings
- Guides
- About
- Contact
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

## Final Lolipop migration — future stage only

### Existing workflows

- `.github/workflows/deploy-preflight.yml`
- `.github/workflows/deploy-lolipop.yml`

These are preserved for the **final production migration after completion**. They are not part of the current GitHub Pages preview flow.

Current safety characteristics:
- manual-only
- no automatic Lolipop deployment from `main`
- no `mirror --delete`
- repository/dev files excluded from upload
- root/empty remote directory rejected

### Required future repository secrets

At final migration only, the existing Lolipop workflow expects:
- `LOLIPOP_FTP_SERVER`
- `LOLIPOP_FTP_USERNAME`
- `LOLIPOP_FTP_PASSWORD`
- `LOLIPOP_FTP_SERVER_DIR`

Never store their values in repository files or chat.

### Final migration prerequisites

Before final Lolipop deployment:
1. User explicitly confirms 50PLUS is ready for final production migration.
2. Confirm `main` is the intended final release.
3. Re-run/confirm PR checks and Browser QA evidence.
4. Human verifies the `50plus.rss7.net` subdomain and its dedicated Lolipop directory.
5. Human configures the four Lolipop repository secrets.
6. Run the Lolipop preflight and require success.
7. Run the manual Lolipop deploy.
8. Verify `https://50plus.rss7.net/`, all primary pages, `robots.txt`, `sitemap.xml` and 404 behavior.
9. Confirm final SEO behavior and retire the temporary ai-agent Pages bridge unless explicitly retained.

Do not mark final production complete until live verification succeeds.

## Verified listings maintenance

### Source of truth

`data/verified-listings.json` is the canonical source for factual listing data.

Do not hand-edit the generated verified-listing cards in `listings.html`. The generated block is bounded by:
- `VERIFIED_LISTINGS_GENERATED_START`
- `VERIFIED_LISTINGS_GENERATED_END`

### Update sequence

1. Re-check the official source before changing a listing.
2. Update only verified facts in `data/verified-listings.json`.
3. Update `verified_at` only when actually re-verified.
4. For events, maintain `start_date` and `end_date` in `YYYY-MM-DD`.
5. Run `python3 scripts/render_listings.py`.
6. Review the generated `listings.html` diff.
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
Issue → Active Owner → Branch → Implementation → Test → PR → Review → Merge.

For analysis-only tasks, follow the Issue's requested output without repository mutations.

For long AI sessions, update `HANDOFF.md` instead of depending on conversation history.
