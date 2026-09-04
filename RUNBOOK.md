# 50PLUS RUNBOOK

## Purpose

This file is the operational handoff for one-time setup and repeatable remote operation. GitHub is the SSOT; do not rely on chat memory when this file and current repository state are available.

## Current public target

- Repository: `oosaka0123-sudo/50plus`
- Planned URL: `https://50plus.rss7.net`
- Default branch: confirm current GitHub state before work
- Deployment target: Lolipop via FTPS

## Claude Code Issue automation

### Observed live state

The repository contains `.github/workflows/claude-issue.yml`.

Live verification completed on 2026-09-04:
- an OWNER Issue comment containing `@claude` triggered the GitHub Actions workflow
- repository checkout succeeded
- the workflow stopped at the explicit authentication check
- Claude Code Action itself was skipped because no supported Anthropic authentication was configured in this repository

Therefore the trigger path is verified; the remaining blocker is authentication.

### Supported authentication inputs already wired

Configure **one** supported GitHub Actions repository secret:

Option A:
- Secret name: `ANTHROPIC_API_KEY`
- Value: an Anthropic API key created by the human account owner

Option B:
- Secret name: `CLAUDE_CODE_OAUTH_TOKEN`
- Value: a Claude Code OAuth token
- Anthropic's Claude Code Action setup documentation states that Claude Pro/Max users can generate this token with `claude setup-token` locally

Never write either secret value into Issues, PRs, commits, README, RUNBOOK, logs or chat screenshots.

### Human setup path in GitHub

Repository → Settings → Secrets and variables → Actions → New repository secret

Add exactly one of the supported secret names above.

After authentication is configured:
1. Open the target GitHub Issue.
2. Confirm no other Agent is actively implementing the same Issue.
3. The repository OWNER posts a new comment containing `@claude`.
4. Confirm `Claude Code Issue Implementation` starts in Actions.
5. Confirm the authentication check passes.
6. Claude must use a dedicated branch, run checks, and create/update a PR.
7. Do not auto-merge; review evidence first.

### Trigger safety

The workflow is intentionally bounded:
- only newly created Issue comments are considered
- comment must contain `@claude`
- comment author association must be `OWNER`
- bot comments are excluded
- no automatic deploy is included
- no automatic merge is included
- secret mutation is outside Claude's task scope

## Lolipop deployment

### Workflow

`.github/workflows/deploy-lolipop.yml`

Current safety state:
- manual `workflow_dispatch` only
- automatic deployment from `main` is disabled
- `mirror --delete` is not used
- repository/dev files are excluded from upload
- root/empty remote directory is rejected

### Required repository secrets

The current workflow expects these four GitHub Actions repository secrets:

- `LOLIPOP_FTP_SERVER`
- `LOLIPOP_FTP_USERNAME`
- `LOLIPOP_FTP_PASSWORD`
- `LOLIPOP_FTP_SERVER_DIR`

Do not store their values in this repository.

### Verified workflow constraint

The workflow currently validates:
- `LOLIPOP_FTP_SERVER` must be `ftp.lolipop.jp`
- all four values must be non-empty
- `LOLIPOP_FTP_SERVER_DIR` must not be empty, `.` or `/`

### Before first deployment

Human must verify in Lolipop control panel:
1. subdomain `50plus.rss7.net` exists
2. its dedicated public directory is known exactly
3. FTP username/password are the intended Lolipop account credentials
4. the target directory is isolated from other websites

Then add the four repository secrets.

### First deployment sequence

1. Confirm `main` contains the intended release.
2. Confirm PR checks are green.
3. Confirm no secret values are present in tracked files.
4. Open GitHub Actions → `Deploy to Lolipop (manual only)`.
5. Run the workflow manually.
6. Inspect the workflow result.
7. Verify `https://50plus.rss7.net/` in a browser.
8. Verify at least HOME, Activities, Guides, About, Contact, `robots.txt`, `sitemap.xml`, and a nonexistent URL for 404 behavior.
9. Record the deployment evidence in the relevant Issue/PR.

## Project boundary

50PLUS is an adult friendship/community discovery product, not a pickup, sexual-service, dating-optimization or matchmaking product.

Never fabricate live venue/event facts, schedules, prices, ratings, participant demographics, gender ratios, attendance, reviews or success rates.

## Operational rule

For implementation tasks prefer:
Issue → Active Owner → Branch → Implementation → Test → PR → Review → Merge.

For long AI sessions, write a repository handoff instead of depending on conversation history.
