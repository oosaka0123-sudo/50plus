# 50PLUS — Project Specification

## 1. Project

- Name: **50PLUS**
- Repository: `oosaka0123-sudo/50plus`
- Planned public URL: `https://50plus.rss7.net`
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

## 5. MVP Information Architecture

### Home — `index.html`
- Brand / hero
- How 50PLUS works
- Activity categories
- First-step guide
- Safety / editorial promise
- Links to other pages

### Activities — `activities.html`
- Ways to meet people through activities
- Categories: walking, learning, sports, culture, volunteering, food / social, outdoor
- Evaluation framework for future verified listings
- No fabricated live event data in MVP

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

## 6. Future Verified Listing Fields

When real activities or venues are added, each listing may include only verified / sourced facts such as:
- Name
- Category
- Area / access
- Official URL
- Published participation requirements
- Published price
- Official schedule or link
- Whether solo participation is explicitly welcomed
- Source / last verification date

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

## 9. Technical MVP

Initial implementation:
- static HTML / CSS / vanilla JavaScript
- responsive mobile-first layout
- semantic HTML
- accessible navigation and focus states
- no external runtime dependency required for core UI
- SEO title / description / canonical placeholders for planned domain

## 10. Development / Deployment

- GitHub is SSOT.
- Follow `ai-master` and repository `AGENTS.md`.
- Prefer Issue -> Branch -> Implementation -> Test -> PR -> Review -> Merge.
- Claude Code on the web reads `CLAUDE.md` before implementation.
- Deployment pattern is based on `claudecode-kyoshitsu`: GitHub Actions -> lftp -> Lolipop FTPS.
- Initial workflow must remain `workflow_dispatch` only until Lolipop directory and GitHub Secrets are verified.
- Initial deployment must not use `mirror --delete`.
- Never commit secrets.

## 11. Initial Completion Definition

The MVP foundation is complete when:
- the five core pages exist and share navigation / design
- mobile navigation works
- no fabricated live listings are presented as real
- static files are reviewable via PR
- manual-only FTPS workflow exists without destructive delete sync
- automatic deployment remains disabled until server settings are verified
