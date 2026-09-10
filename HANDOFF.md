# 50PLUS — HANDOFF

Updated: 2026-09-10 JST

## Purpose

This file is the project-local transient handoff for safely resuming 50PLUS work across ChatGPT / Claude Code / Jules / other approved agents.

GitHub is the SSOT. **Current `main`, Issues, Pull Requests, Actions and current repository files always override this handoff if anything has changed since it was written.**

Do not turn this file into a manual history log. Completed PR / commit / Actions history should be recovered from GitHub itself.

## Resume order

Before doing new work:

1. Read current `oosaka0123-sudo/ai-master` `README.md`, `AGENTS.md`, `PROJECTS.md`.
2. Confirm the current default branch of `oosaka0123-sudo/50plus`.
3. Read `AGENTS.md`, `README.md`, `PROJECT_SPEC.md`, `COUNCIL.md`, `RUNBOOK.md` and this `HANDOFF.md`.
4. Claude Code also reads `CLAUDE.md`.
5. Reconcile current Open Issues, Open PRs, latest Actions and current code before choosing work.
6. If this handoff conflicts with current GitHub evidence, follow current GitHub evidence and update or retire this handoff as needed. This file is a cache only, never SSOT or history: it may record unresolved cross-session context, but current GitHub Issues/PRs/Actions always win when they disagree.
7. Apply `COUNCIL.md`'s resume precedence: a flagged `needs-human` Issue/PR first, then any unfinished PR of your own (fix CI > confirm/request review > confirm merge readiness > verify deploy > verify live production) before starting any new Issue.

## Stable project foundation

The repository-side production foundation is in place:

- six primary public pages, four topic hub pages (`learning.html`, `volunteering.html`, `sports.html`, `culture-library.html`), plus the project 404 page
- responsive static HTML / CSS / vanilla JavaScript
- adult friendship / community discovery positioning; not a dating, pickup or sexual-service product
- verified listing facts use `data/verified-listings.json` as canonical data
- `scripts/render_listings.py` deterministically keeps generated listing markup synchronized with canonical JSON
- CI validates local links, common secret patterns, listing schema, JSON-to-HTML sync and stale verified event dates
- repository-native Browser QA uses pinned Playwright / Chromium against checked-out files served locally on the GitHub Actions runner
- Browser QA covers HOME, Activities, Listings, Guides, the four topic hubs, About, Contact and 404 at desktop and 390px mobile viewports
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

Active implementation task: **Issue #76 — Add verified upcoming Osaka events and current discovery flow**.

Current working branch: `feat/issue-76-upcoming-events` based on main commit `7dcd32900b97135c0b16e80ca074956cb6326a02`.

Current unmerged work on this branch:

- `data/verified-listings.json` now has 13 total records: the previous 8 plus 5 official-source Osaka events verified on 2026-09-10.
- The two existing multi-date events now have `occurrence_dates`; the five new events also have machine-readable occurrence dates.
- A machine comparison confirmed the previous 8 records' factual fields were unchanged except for the intentional `occurrence_dates` additions to the two existing events.
- `scripts/render_listings.py` emits event start/end/occurrence dates as data attributes and adds `すべて / 今週 / 今月` period controls on `listings.html`.
- `assets/listings-filter.js` computes current week/month at runtime, uses `occurrence_dates` when present, and hides expired event cards on Listings plus all four topic hubs while leaving resource cards visible.
- The generated HTML files have been regenerated and `python scripts/render_listings.py --check` passes for `listings.html` and all four topic hubs.
- Browser QA now covers `すべて / 今週 / 今月`, kind-filter interaction, no-match/reset behavior, and runtime expiry on Listings plus all four topic hubs using a fixed far-future clock; the local run passed for 11 pages across desktop and 390px mobile.
- Issue #76 is not merged to main yet; local implementation and QA are ready for commit/push and PR.

Five new event records currently staged in the canonical JSON are:

- 2026-09-26 認知症サポーター養成講座
- 2026-10-03 読書前のヨガ・タイム
- 2026-10-09 読書会『憑神』
- 2026-10-11 オータム・チャレンジ・スポーツ ニュースポーツ体験会
- 2026-10-31 小さな読書交流会-わたしの1冊、あなたの1冊-

Council / automation state:

- Council Autopilot core is merged and live.
- Event-driven `Autopilot Watch` is merged and verified in production; Pages completion successfully triggered the watcher and produced `no_action_clean` when the queue was empty.
- Issue #76 was then created and moved to `status:active`, `priority:high`, `risk:low` so development could continue.
- GitHub `@claude` automation currently authenticates successfully (`ANTHROPIC_API_KEY` present) but the Claude Code Action fails immediately after model initialization with `result is_error:true`. Do not treat this as a missing-secret problem.
- Until that GitHub Action failure is repaired, use the connected Surface Claude Code as the implementation owner for Issue #76, with Gemini as independent reviewer and ChatGPT as PM/integrator.
- Surface Claude has repeatedly consumed max-turns during broad tasks; keep follow-up work narrowly split by file/phase instead of reissuing the whole Issue.

### Exact next steps

1. Commit/push the completed Issue #76 branch and open its PR.
2. Wait for required PR checks and Browser QA; fix any branch-owned failure within the retry policy.
3. Merge only after required checks are green and review has no blocker.
4. Verify the GitHub Pages deployment and live production behavior before closing Issue #76.
5. Track the GitHub Claude Action `is_error:true` failure as a separate repair task; do not mix it into Issue #76 unless it becomes necessary to finish #76 safely.

### Re-entry message

`Resume 50PLUS Issue #76 from branch feat/issue-76-upcoming-events. Implementation, deterministic HTML regeneration, local/static checks, Browser QA, expiry coverage, and final Gemini review are complete. Continue with commit/push -> PR -> CI -> merge -> Pages -> live verify. GitHub @claude auth passes but the Action currently dies with result is_error:true; keep that as a separate repair task.`
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
