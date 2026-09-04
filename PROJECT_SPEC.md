# 50PLUS — Project Specification

## 1. Project

- Name: **50PLUS**
- Repository: `oosaka0123-sudo/50plus`
- Current development preview: `https://oosaka0123-sudo.github.io/ai-agent/50plus/`
- Planned final production URL: `https://50plus.rss7.net`
- Primary language: Japanese
- Initial area focus: Osaka / Kansai, with a structure that can expand nationwide

## 2. Purpose

50PLUS is an adult friendship and community discovery website for people who want to make new social connections after 50.

The service helps adults find ideas for hobbies, events, local activities and welcoming places where they can naturally meet and talk with other adults.

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
- source HTML keeps canonical metadata for the planned final production domain
- canonical verified-listing data in `data/verified-listings.json`
- deterministic static HTML generation through `scripts/render_listings.py`
- PR checks validate local links, common secret patterns, listing schema and JSON-to-HTML synchronization
- scheduled CI checks verified event end dates and flags stale events for review rather than deleting or rewriting content automatically
- path-filtered rendered Browser QA uses pinned Playwright/Chromium against a local GitHub Actions runner server for UI-affecting changes
- Browser QA stores reviewable desktop/mobile screenshot artifacts
- active GitHub Pages preview is generated by the already-enabled `oosaka0123-sudo/ai-agent` Pages workflow
- that bridge clones the current public `oosaka0123-sudo/50plus` `main` read-only during the Actions run and copies only seven runtime HTML pages plus `assets/` into the Pages artifact under `web/50plus/`
- the bridge injects and verifies `noindex,nofollow` in every preview HTML page and does not commit copied 50PLUS runtime files to `ai-agent`
- this repository remains the sole 50PLUS source of truth
- repository-local dedicated Pages deployment is manual-only while Pages is disabled here
- final Lolipop deployment remains a separate future production migration path

## 10. Development / Publishing

- GitHub is SSOT.
- Follow `ai-master` and repository `AGENTS.md`.
- Prefer Issue -> Branch -> Implementation -> Test -> PR -> Review -> Merge.
- Claude Code on the web reads `CLAUDE.md` before implementation.

### Stage A — development preview

- Merge approved work to this repository's `main`.
- The `oosaka0123-sudo/ai-agent` Pages bridge periodically reads the latest public 50PLUS `main` and publishes it to `https://oosaka0123-sudo.github.io/ai-agent/50plus/`.
- The bridge needs no 50PLUS FTP credentials or Lolipop secrets.
- The preview is public for visual/functional review but deployed with `noindex,nofollow`.
- Continue using PR checks and Browser QA throughout development.
- Do not duplicate 50PLUS source files into `ai-agent`; only the generated Pages artifact may contain the preview copy.

### Stage B — final production migration

- Only after the user considers the site complete, migrate final production to Lolipop at `https://50plus.rss7.net`.
- Keep the manual-only Lolipop workflow available for this later stage.
- Before final migration, verify the dedicated Lolipop directory and required repository secrets.
- Final migration must not use destructive `mirror --delete` unless separately reviewed and explicitly approved.
- After final migration, verify live pages, SEO files and 404 behavior on the Lolipop domain.
- Retire the temporary ai-agent Pages bridge after final production is confirmed unless the user explicitly wants to retain it.

Detailed operational procedures belong in `RUNBOOK.md`.

## 11. Current Completion Definition

The development-preview foundation is complete when:
- the six primary public pages exist and share navigation / design
- mobile navigation works
- UI-affecting changes can pass repository-native rendered desktop/mobile Browser QA with reviewable screenshot evidence
- verified listings are sourced from canonical JSON and generated HTML stays in sync
- expired verified events are detectable by automated checks
- no fabricated live listing facts are presented as real
- static files and factual data changes are reviewable via PR
- the active ai-agent Pages bridge can publish current 50PLUS `main` without FTP credentials
- the preview remains `noindex,nofollow` until final production migration

Final production completion is a separate milestone requiring explicit migration to Lolipop, successful deployment evidence and live verification of `https://50plus.rss7.net`.
