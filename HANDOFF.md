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

### Active task — Issue #58

Repository: `oosaka0123-sudo/50plus`

Goal:
- redesign 50PLUS with Claude Code as the single active implementation owner
- use Google Media MCP-generated production assets extensively, especially a cinematic home hero video and coherent lifestyle images
- keep the experience premium, energetic, readable, fast and mobile-first
- retain the product boundary: respectful adult friendship/community discovery, not dating or pickup optimization

Confirmed design requirements:
- finished media files are committed and served statically; page viewing must never wait for AI generation
- hero video needs a still-image fallback and `prefers-reduced-motion` behavior
- imagery should depict respectful adults around 50+ enjoying Osaka/Kansai activities such as walking, learning, culture, outdoor activity and casual community participation
- avoid stereotypical elderly, medical, retirement-home, romance or dating-app imagery
- preserve the seven public pages, verified-listing safeguards, canonical/SEO files and dedicated GitHub Pages architecture
- do not fabricate venue/event facts, schedules, prices, reviews, ratings or participant demographics

### OBSERVED

- Issue #58 exists and assigns the visual redesign scope to Claude Code as the single active owner.
- Current `main` at the start of this task was commit `9ebe10a`.
- The authorized Windows development device is online and has a fresh `C:\\Users\\oosak\\50plus` clone on `main`.
- The same device previously verified Claude Code, Google Media MCP and Steel Browser MCP end-to-end in the `ai-agent` project.
- In the 50PLUS checkout, Claude Code discovered the Project-scoped `google-media` MCP entry but reported `Pending approval`.
- The automated 50PLUS approval-setting command was interrupted before success could be observed. Do not assume that approval was written.
- No 50PLUS implementation branch, media generation, source-file change, commit or PR has been completed for Issue #58 yet.

### BLOCKER / resume point

The only current stop point is 50PLUS Project-scoped Google Media MCP approval/recognition in Claude Code. Production Google Media infrastructure must not be recreated.

Resume with:
1. Re-read current `ai-master`, current 50PLUS `main`, Issue #58, open PRs and latest Actions.
2. Verify the Windows device is online and the `50plus` checkout is clean/current.
3. Finish Project-scoped `google-media` approval without exposing or persisting token values in the repository.
4. Run `bash scripts/google_media_mcp_preflight.sh`, then confirm Claude Code reports `google-media` as connected and exposes `generate_image` / `generate_video`.
5. Follow `CLAUDE.md`: exactly one minimal image smoke test, then exactly one minimal video smoke test.
6. Let Claude Code create a dedicated Issue #58 branch and implement the redesign, generated assets, fallbacks and documentation.
7. Run static checks and desktop/390px Browser QA; review performance, reduced-motion and no-horizontal-overflow behavior.
8. Create a PR, review evidence, merge only when safe, wait for GitHub Pages deployment, and live-verify production.

### Re-entry message

`Read current ai-master and 50PLUS main, then read Issue #58 and HANDOFF.md. Resume at the 50PLUS google-media Project approval step and complete the Claude-first media redesign through PR, checks, Pages deploy and live verification.`

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
