# CLAUDE.md — 50PLUS Bootstrap

Before making changes:

1. Read the current default branch of `oosaka0123-sudo/ai-master`.
2. Follow `ai-master/README.md` and `ai-master/AGENTS.md`.
3. Read this repository's `AGENTS.md`, `README.md`, `PROJECT_SPEC.md`, `RUNBOOK.md` and `HANDOFF.md` when present.
4. Check open Issues, open PRs, latest Actions and current code.
5. Use GitHub as SSOT. Do not rely on chat memory when GitHub differs.

Current product: 50PLUS, an adult friendship / community information website.

Current development preview: `https://oosaka0123-sudo.github.io/ai-agent/50plus/`

Preview publishing: the already-enabled `oosaka0123-sudo/ai-agent` GitHub Pages workflow reads the latest public `oosaka0123-sudo/50plus` `main` and creates a temporary noindex preview artifact. This repository remains the SSOT; copied preview files are not committed to `ai-agent`.

Planned final production URL after completion: `https://50plus.rss7.net`

Development is remote-first via GitHub and Claude Code on the web. Use Issue/Branch/PR flow unless a project rule explicitly permits otherwise.

During active development, use the Pages bridge as the public preview environment. Do not treat dedicated 50PLUS Pages or Lolipop configuration as a development blocker and do not trigger final Lolipop migration unless the user explicitly moves the completed site to production.

Do not commit secrets. Do not claim tests, deploys, connections or live verification unless actually observed.

For long sessions, follow the ai-master Claude Code context rule: initial 40% context threshold -> `/autocompact` first when available; if context grows again or handoff risk is high, update the project handoff according to the Master protocol.
