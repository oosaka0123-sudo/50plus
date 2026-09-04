# AI control-plane onboarding

This repository is registered with the shared AI control plane.

- Project: **50PLUS** (`50plus`)
- Control plane: `oosaka0123-sudo/ai-agent`
- Managed manifest: `.ai-agent/project.json`
- Google Media MCP: `.mcp.json` (`mcpServers.google-media` entry only --
  any other MCP servers already configured in this repository are left
  untouched)
- Default publishing policy: **preview first**
- Direct push to `main`: **disabled**

## What becomes reusable automatically

The control plane provides shared AI media generation -- Google Vertex AI
(Imagen / Veo) today, Higgsfield planned -- as a Remote HTTP MCP server, so
Claude Code in this repository can call `generate_image` / `generate_video`
directly. No generation code, Google Cloud project configuration, or actual
credential value is copied into this repository: `.mcp.json` only configures
how to reach the shared server -- its URL and an environment-variable-backed
bearer token, resolved at run time rather than stored here.

Generation logs, provider routing, and future cross-project automation are
also shared this way, without copying implementation into every site.

## One-time setup this repository may still need

`.mcp.json`'s `Authorization` header reads `${GOOGLE_MEDIA_MCP_TOKEN}` from
the environment Claude Code runs in -- it is never committed here. Set it
once wherever this repository's Claude Code sessions run. See the control
plane's `docs/GOOGLE_MEDIA_MCP.md` for where to get the value.

## Safety boundary

This onboarding file does not contain API keys, service-account keys, passwords,
or tokens. Credentials remain in the control plane / GitHub Secrets.

The control plane opens Pull Requests for managed changes. It does not directly
overwrite the production branch.
