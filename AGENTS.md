# AGENTS.md — 50PLUS Project Rules

This repository is the project SSOT for 50PLUS. Global governance is defined by `oosaka0123-sudo/ai-master/AGENTS.md` and must be read first in a new AI session.

## Startup

1. Read current `oosaka0123-sudo/ai-master` default branch: `README.md`, `AGENTS.md`, then `PROJECTS.md`.
2. Confirm this repository's current default branch.
3. Read this `AGENTS.md`, `README.md`, `PROJECT_SPEC.md`, `RUNBOOK.md` and `HANDOFF.md` when present.
4. Check open Issues, open PRs, latest Actions and current code before implementation.
5. Treat GitHub current state as authoritative over chat history or model memory.

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

## Publishing / Deployment

### Current preview stage

Current preview URL: `https://oosaka0123-sudo.github.io/50plus/`

During active development, GitHub Pages is the public preview environment. The Pages workflow publishes a reduced static artifact from current `main` and injects `noindex,nofollow` into preview HTML so the temporary preview is not treated as the final SEO destination.

Agents may update the GitHub Pages preview through the normal Issue/Branch/PR/Merge flow when repository rules and CI allow it.

### Final production stage

Planned final production URL: `https://50plus.rss7.net`

Final production hosting is Lolipop, but migration is deferred until the site is considered complete and the user explicitly moves the project to final production.

Until that final-migration decision:
- do not treat Lolipop configuration as a blocker for normal development
- do not trigger the Lolipop deploy workflow
- do not request or modify Lolipop secret values
- preserve the existing manual-only Lolipop path for future final migration

At final migration, verify the dedicated server directory, deployment exclusions, required secrets, Browser QA evidence and live site before declaring production complete. Never enable destructive mirror/delete behavior without an explicit reviewed migration plan.

## Handoff

Follow the ai-master context handoff protocol. Use `HANDOFF.md` for useful unresolved cross-session context and keep GitHub Issues/PRs/Actions as the source for dynamic history.
