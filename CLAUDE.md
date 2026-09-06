# CLAUDE.md — 50PLUS Bootstrap

Before making changes:

1. Read the current default branch of `oosaka0123-sudo/ai-master`.
2. Follow `ai-master/README.md` and `ai-master/AGENTS.md`.
3. Read this repository's `AGENTS.md`, `README.md`, `PROJECT_SPEC.md`, `RUNBOOK.md` and `HANDOFF.md` when present.
4. Check open Issues, open PRs, latest Actions and current code.
5. Use GitHub as SSOT. Do not rely on chat memory when GitHub differs.

Current product: 50PLUS, an adult friendship / community information website.

Production URL: `https://50plus.rss7.net`

Primary production publishing: dedicated GitHub Pages for `oosaka0123-sudo/50plus`, using `.github/workflows/deploy-pages.yml` from approved `main`.

Temporary preview while dedicated Pages/custom-domain activation is incomplete: `https://oosaka0123-sudo.github.io/ai-agent/50plus/`. The `ai-agent` bridge is preview-only, injects `noindex,nofollow`, and is not another source of truth.

Development is remote-first via GitHub and Claude Code on the web. Use Issue/Branch/PR flow unless a project rule explicitly permits otherwise.

Do not treat Lolipop as the normal production path. Existing Lolipop workflows are manual fallback only. Do not request or modify Lolipop secrets merely to continue development or GitHub Pages production.

Do not claim production complete until dedicated Pages is enabled, the production workflow succeeds, the custom domain/DNS is configured, and `https://50plus.rss7.net` is live-verified.

## Google Media MCP — fast connection path

The Google Media MCP onboarding is already installed. Do **not** rerun onboarding, recreate `.mcp.json`, create a new Google Cloud project, create a new Cloud Run service, or rebuild Vertex AI infrastructure merely to use media generation.

For a new Claude Code session that needs Google Media:

1. Work from the current `50plus/main` checkout and confirm `.mcp.json` exists.
2. Run:
   `bash scripts/google_media_mcp_preflight.sh`
3. The preflight may check only configuration structure, whether `GOOGLE_MEDIA_MCP_TOKEN` is present (never its value), network reachability, `/healthz`, and `/readyz`.
4. If preflight passes, confirm Claude Code itself recognizes the `google-media` MCP server and list the available MCP tools. Shell reachability alone is not proof that Claude's MCP runtime loaded the server.
5. Confirm `generate_image` and `generate_video` are available.
6. Run exactly one minimal image smoke test first, using the native MCP tool contract:
   - tool: `generate_image`
   - `project_slug`: `50plus`
   - `prompt`: `A simple blue circle centered on a clean white background, no text.`
   - `count`: `1`
7. Require a successful tool result and generated output location before continuing.
8. Only after image success, run exactly one minimal video smoke test:
   - tool: `generate_video`
   - `project_slug`: `50plus`
   - `prompt`: `A simple blue circle gently drifting across a clean white background, no text.`
   - leave optional model/duration/aspect-ratio fields at server/provider defaults unless the current tool schema requires otherwise.
9. Do not separately poll a video job; the MCP server's `generate_video` call handles polling server-side and should return the final outcome.

If connection or generation fails, do not repeat the same failed approach more than twice. Report only:

- `OBSERVED`
- `BLOCKER`
- `REQUIRED ACTION`

Classify the stop point as one of: current checkout / MCP recognition / client token / network egress / Cloud Run health / Cloud Run readiness / MCP tool discovery / Vertex AI generation. Do not expose secret values in commands, logs, Issues, PRs, screenshots or chat.

`CONTROL_PLANE_GITHUB_TOKEN` is unrelated to Google Media runtime connectivity. It is for future cross-repository onboarding automation and must not be treated as a prerequisite for `google-media` MCP use.

Do not commit secrets. Do not claim tests, deploys, connections or live verification unless actually observed.

For long sessions, follow the ai-master Claude Code context rule: initial 40% context threshold -> `/autocompact` first when available; if context grows again or handoff risk is high, update the project handoff according to the Master protocol.
