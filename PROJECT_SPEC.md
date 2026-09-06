# 50PLUS — Project Specification

## 1. Project

- Name: **50PLUS**
- Repository: `oosaka0123-sudo/50plus`
- Temporary development preview: `https://oosaka0123-sudo.github.io/ai-agent/50plus/`
- Production URL: `https://50plus.rss7.net`
- Primary production hosting: dedicated GitHub Pages for this repository
- Primary language: Japanese
- Initial area focus: Osaka / Kansai, with a structure that can expand nationwide

## 2. Purpose

50PLUS is an adult friendship and community discovery website for people who want to make new social connections after 50.

The service helps adults find ideas for hobbies, events, local activities and welcoming places where people can naturally meet and talk with other adults.

The product is **not a dating service, pickup optimization service, sexual service or matchmaking tool**. Women and men may both be part of the communities and activities introduced, but people must not be ranked or targeted by sex, age or perceived attractiveness for pickup purposes.

## 3. Core message

> 50代から、もう一度「新しい仲間」ができる。

Supporting copy:

> 趣味、街歩き、学び、スポーツ、ボランティア。ひとり参加から始められる、大人の友活情報サイト。

## 4. Audience

Primary:
- Adults around 50+ who want new friends or social connections
- People whose existing friendships have become harder to maintain because of work, family or lifestyle changes
- People who want a reason to go out alone and join an activity

Secondary:
- Adults under or over 50 who are comfortable joining mixed-age adult communities
- Organizers of safe, legitimate adult community activities

## 5. Current Information Architecture

### Home — `index.html`
- Brand / hero
- How 50PLUS works
- Activity categories
- First-step guide
- Safety / editorial promise
- Direct route to verified Osaka listings

### Activities — `activities.html`
- Ways to meet people through activities
- Categories: walking, learning, sports, culture, volunteering, food / social, outdoor
- Evaluation framework for choosing activities
- Route to verified Osaka listings

### Listings — `listings.html`
- Official-source-backed Osaka activity and event information
- Source links and verification date
- Published participation requirements, price and schedule only when verified
- Clear separation between sourced facts and unsupported assumptions
- Generated listing cards must remain synchronized with canonical JSON data

### Guides — `guides.html`
- How to join alone
- Conversation starters
- How to leave politely
- Safety / boundaries
- How to distinguish friendship, dating and solicitation contexts

### About — `about.html`
- Mission
- Editorial principles
- Who the site is for
- What the site will not do

### Contact — `contact.html`
- Future contact / listing request policy
- No fake contact destination before a real channel is configured

## 6. Verified Listing Data Model

`data/verified-listings.json` is the canonical factual source for verified listings.

Each listing may include only verified / sourced facts such as:
- Stable ID
- Kind / category
- Name
- Area / access
- Official source URL or URLs
- Published participation requirements
- Published price
- Official schedule or link
- Whether solo participation is explicitly welcomed
- Source / last verification date

For event records, machine-readable `start_date` and `end_date` are maintained in addition to human-readable schedule text so stale events can be detected automatically.

`listings.html` contains committed static markup for SEO and no-JavaScript readability, but its verified-listing block is deterministically generated from the canonical JSON by `scripts/render_listings.py`. Hand-edited factual drift between JSON and rendered HTML is not allowed.

Editorial observations such as atmosphere or beginner friendliness must be clearly labeled as editorial judgment and should not be presented as objective fact without evidence.

Do **not** fabricate:
- gender ratio
- participant ages
- number of women / men
- pickup success likelihood
- ratings or reviews
- schedules
- prices
- attendance figures

## 7. Product Safety Boundary

Allowed:
- adult-only friendship and community information
- hobby / event discovery
- practical advice for joining activities alone
- respectful social communication guidance
- inclusive age-related editorial content

Not allowed in product design:
- sexual services or explicit content
- features for targeting people for pickup
- ranking people by desirability
- deceptive identity / profile tactics
- harassment, stalking or circumvention of venue rules
- collecting private user data without an explicit product need and privacy design

## 8. Design Direction

Keywords:
- modern adult lifestyle
- warm but not senior-care themed
- energetic, urban, optimistic
- readable on smartphones
- generous whitespace
- strong typography
- subtle motion only

Avoid:
- stereotypical elderly imagery
- dating-app visual language
- excessive pink / romance cues
- medical / retirement-home tone

## 9. Technical Architecture

Current implementation:
- static HTML / CSS / vanilla JavaScript
- responsive mobile-first layout
- semantic HTML
- accessible navigation and focus states
- no external runtime dependency required for core UI
- source HTML canonical / OG metadata targets `https://50plus.rss7.net`
- canonical verified-listing data in `data/verified-listings.json`
- deterministic static HTML generation through `scripts/render_listings.py`
- PR checks validate local links, common secret patterns, listing schema and JSON-to-HTML synchronization
- scheduled CI checks verified event end dates and flags stale events for review rather than deleting or rewriting content automatically
- path-filtered rendered Browser QA uses pinned Playwright/Chromium against a local GitHub Actions runner server for UI-affecting changes
- Browser QA stores reviewable desktop/mobile screenshot artifacts
- production publishing uses repository-local `.github/workflows/deploy-pages.yml`
- the production artifact contains seven runtime HTML pages, `assets/`, `robots.txt`, `sitemap.xml` and `.nojekyll`
- the production workflow verifies generated listings, rejects preview-only `noindex,nofollow`, and checks the expected production origin
- the existing `ai-agent` Pages bridge remains temporary preview-only during activation and continues to inject `noindex,nofollow`
- this repository remains the sole 50PLUS source of truth
- existing Lolipop workflows remain manual fallback paths, not the primary production architecture

## 10. Development / Publishing

- GitHub is SSOT.
- Follow `ai-master` and repository `AGENTS.md`.
- Prefer Issue -> Branch -> Implementation -> Test -> PR -> Review -> Merge.
- Claude Code on the web reads `CLAUDE.md` before implementation.

### Production — dedicated GitHub Pages

- Approved work is merged to this repository's `main`.
- When dedicated Pages is enabled, `.github/workflows/deploy-pages.yml` publishes `main` automatically and also supports manual dispatch.
- Production is intended to resolve at `https://50plus.rss7.net` through GitHub Pages custom-domain configuration and DNS.
- Production pages are indexable and must not contain staging-only `noindex,nofollow`.
- `robots.txt` and `sitemap.xml` must be deployed with the site.
- Do not mark a release complete merely because the repository workflow is present; require actual Pages deployment evidence and live-domain verification.

### Temporary preview during activation / ongoing review

- Until dedicated Pages and the custom domain are fully activated, the `oosaka0123-sudo/ai-agent` Pages bridge may continue publishing the latest public `50plus/main` to `https://oosaka0123-sudo.github.io/ai-agent/50plus/`.
- The bridge is preview-only, uses `noindex,nofollow`, and does not become another source of truth.
- Continue using PR checks and Browser QA for development quality evidence.

### Lolipop fallback

- Preserve existing manual-only Lolipop preflight/deploy workflows for recovery or deliberate future fallback.
- Do not require Lolipop secrets for normal development or GitHub Pages production.
- Do not use destructive `mirror --delete` unless separately reviewed and explicitly approved.

Detailed operational procedures belong in `RUNBOOK.md`.

## 11. Current Completion Definition

The repository-side production foundation is complete when:
- the six primary public pages exist and share navigation / design
- mobile navigation works
- UI-affecting changes can pass repository-native rendered desktop/mobile Browser QA with reviewable screenshot evidence
- verified listings are sourced from canonical JSON and generated HTML stays in sync
- expired verified events are detectable by automated checks
- no fabricated live listing facts are presented as real
- static files and factual data changes are reviewable via PR
- dedicated GitHub Pages production workflow builds an indexable artifact including SEO files
- production canonical / OG metadata remains on `https://50plus.rss7.net`

Production activation is complete only after dedicated GitHub Pages is enabled, custom-domain/DNS configuration is complete, the Pages workflow succeeds, and `https://50plus.rss7.net` is live-verified.
