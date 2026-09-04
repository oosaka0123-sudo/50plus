# AGENTS.md — 50PLUS Project Rules

This repository is the project SSOT for 50PLUS. Global governance is defined by `oosaka0123-sudo/ai-master/AGENTS.md` and must be read first in a new AI session.

## Startup

1. Read current `oosaka0123-sudo/ai-master` default branch: `README.md`, `AGENTS.md`, then `PROJECTS.md`.
2. Confirm this repository's current default branch.
3. Read this `AGENTS.md` and `README.md`.
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

## Deployment

Target public URL: `https://50plus.rss7.net`

The intended deployment pattern is based on the proven `oosaka0123-sudo/claudecode-kyoshitsu` GitHub Actions -> FTPS -> Lolipop workflow, but deployment configuration must be verified for this project before enabling it.

Do not copy destructive synchronization options blindly. Verify the dedicated server directory and deployment exclusions before enabling any mirror/delete behavior.

## Handoff

Follow the ai-master context handoff protocol. If a project handoff becomes necessary and no local convention exists yet, use `HANDOFF.md` in this repository. Do not create it preemptively while there is no useful handoff content.
