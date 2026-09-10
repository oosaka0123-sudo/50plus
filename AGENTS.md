# AGENTS.md — 50PLUS Project Rules

This repository is the project SSOT for 50PLUS. Global governance is defined by `oosaka0123-sudo/ai-master/AGENTS.md` and must be read first in a new AI session.

## Startup

1. Read current `oosaka0123-sudo/ai-master` default branch: `README.md`, `AGENTS.md`, then `PROJECTS.md`.
2. Confirm this repository's current default branch.
3. Read this `AGENTS.md`, `README.md`, `PROJECT_SPEC.md`, `COUNCIL.md`, `RUNBOOK.md` and `HANDOFF.md` when present.
4. Check open Issues, open PRs, latest Actions and current code before implementation.
5. Treat GitHub current state as authoritative over chat history or model memory.
6. Resolve priority using `COUNCIL.md`'s resume order: an unfinished PR of your own (failing CI, pending review, pending merge, pending deploy, pending live verification) always outranks starting a new Issue. Only pick up new work after confirming no such unfinished PR exists.

`COUNCIL.md` is the canonical definition of the 3-agent council state machine, priorities, retry limits and human-only escalation conditions. `.github/autopilot-policy.json` is its machine-readable mirror, checked by `scripts/autopilot_status.py`. Do not redefine these rules elsewhere; update `COUNCIL.md` and the policy file together if they need to change.

## Product Boundary

50PLUS is an adult friendship / community information site. Its purpose is to help adults discover hobbies, events, local activities and places where people can form respectful social connections.

Do not implement:
- sexual services or explicit sexual content
- coercive, deceptive or exploitative interaction features
- targeting or ranking people for pickup / harassment
- features intended to bypass venue or platform safety rules

Age-related editorial content is allowed when it is respectful, adult-only and relevant to community participation.

## Development Rules

- Prefer Issue -> Branch -> Implementation -> Test -> PR -> Review -> Merge.
- One active implementation owner per task unless an intentional competition mode is declared.
- Claude Code, ChatGPT, Jules, Copilot and other agents may collaborate, but must not silently duplicate the same implementation scope.
- Keep changes small and reviewable.
- Do not commit secrets, credentials, tokens, passwords or private user data.
- Do not invent deployment state, URLs, credentials, test results or external service connections.
- Code generation alone is not completion. Report evidence for relevant test / PR / CI / deploy / live verification steps.

## Chat persistence / knowledge routing

When the user says `このチャット内容をリポジトリに保存して` or gives an equivalent instruction, do not copy the raw conversation log into the repository. Normalize only durable or restart-critical information and route it to the existing Project source of truth.

- Before writing, re-read the current default branch and the relevant canonical files, plus related Issue / PR / Actions when needed.
- Current confirmed project specification or operating state -> update the existing `PROJECT_SPEC.md`, `README.md`, or other clearly responsible canonical document in place.
- Important long-lived design rationale -> create or update `DECISIONS.md` only when such a decision actually exists.
- Reusable operational procedure -> create or update `RUNBOOK.md` only when a reusable procedure actually exists.
- Unfinished work needed by the next AI/session -> use the Project handoff location defined by `ai-master`; if no dedicated location exists, use `HANDOFF.md`. Create it only when needed.
- Work history already recoverable from code, Issue, Pull Request, Actions, or Commit history -> do not duplicate it into Markdown.
- Prefer replacing stale current-state text over append-only chat summaries.
- Never save secrets, credentials, tokens, passwords, private user data, or other confidential values as chat persistence.
- After saving, report which canonical files changed and what was intentionally not duplicated.

## Publishing / Deployment

### Production path

Production URL: `https://oosaka0123-sudo.github.io/50plus/`

Primary production hosting is dedicated GitHub Pages for `oosaka0123-sudo/50plus`.

- this repository remains the sole code/content SSOT
- approved changes reach production from `main` through `.github/workflows/deploy-pages.yml`
- the production Pages artifact must include the 11 public HTML pages (six primary pages, four topic hub pages and `404.html`), `assets/`, `robots.txt` and `sitemap.xml`
- production HTML must not contain preview-only `noindex,nofollow`
- canonical, Open Graph, robots and sitemap URLs use the live GitHub Pages production URL
- `https://50plus.rss7.net` is an optional future custom domain and is not a blocker for current production
- never claim a release complete from merge alone; require successful Pages deployment and live verification of the current production URL

### Preview bridge

The existing `oosaka0123-sudo/ai-agent` Pages site may remain as a temporary preview bridge at `https://oosaka0123-sudo.github.io/ai-agent/50plus/`.

The bridge reads the current public `50plus/main`, generates runtime preview files only, injects `noindex,nofollow`, and does not become another source of truth. Do not confuse preview deployment evidence with production deployment evidence.

### Lolipop fallback

The existing Lolipop preflight/deploy workflows are retained as a manual fallback only. They are not the normal production path.

- do not request or modify Lolipop secrets for ordinary development or GitHub Pages production
- do not trigger Lolipop deployment merely because a custom domain is not configured
- never enable destructive mirror/delete behavior without an explicit reviewed migration or recovery plan

## Handoff

Follow the ai-master context handoff protocol. Use `HANDOFF.md` for useful unresolved cross-session context and keep GitHub Issues/PRs/Actions as the source for dynamic history. `HANDOFF.md` is a cache, not SSOT: if it disagrees with current GitHub state, GitHub wins and the handoff must be corrected, not trusted.
