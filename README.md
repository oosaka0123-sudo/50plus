# 50PLUS

50代からの友活・仲間づくり情報サイト「50PLUS」。

趣味・イベント・地域交流を通じて、成人同士が自然につながれる場所や活動を紹介するWebプロジェクトです。

## Publishing targets

### Production

- Production URL: `https://50plus.rss7.net`
- Primary hosting: dedicated GitHub Pages for `oosaka0123-sudo/50plus`
- Source of truth: this repository `main`
- `.github/workflows/deploy-pages.yml` publishes the static production artifact after approved changes reach `main`.
- Production HTML is indexable; the staging-only `noindex,nofollow` injection is not used in the dedicated production artifact.
- `robots.txt` and `sitemap.xml` are included in the Pages artifact and continue to use `https://50plus.rss7.net`.
- GitHub Pages repository enablement and the custom-domain/DNS setup are one-time human-owned activation steps.

### Temporary preview bridge

Until dedicated 50PLUS Pages and the custom domain are fully activated and verified, the existing preview remains available at:

- `https://oosaka0123-sudo.github.io/ai-agent/50plus/`

The `ai-agent` bridge is preview-only and injects `noindex,nofollow`. It must not be treated as the production URL or as another source of truth.

### Lolipop fallback

The existing manual Lolipop deployment/preflight path is retained as an emergency/future fallback only. Lolipop is no longer the normal production target and its secrets are not required for standard GitHub Pages publishing.

## Repository

- `oosaka0123-sudo/50plus`
- GitHub is the source of truth for project code and current state.
- Global AI governance: `oosaka0123-sudo/ai-master`

## Development Model

Remote-first development:

1. Claude Code on the web / other approved AI agents
2. GitHub Issue + working branch
3. Implementation and test
4. Pull Request / review
5. Merge to `main`
6. PR/static checks and Browser QA remain the evidence for code/UI quality
7. Once dedicated Pages is enabled, `Deploy 50PLUS GitHub Pages` publishes approved `main` automatically
8. Verify the production deployment and `https://50plus.rss7.net`

Before dedicated Pages activation is complete, continue using the existing `ai-agent` noindex preview bridge for visual review.

## Initial Product Scope

- 50代を中心に、成人が参加しやすい趣味・イベント・地域活動の紹介
- 一人参加しやすさ、雰囲気、参加条件などの実用情報
- 大人の友活・仲間づくりを支援する記事・ガイド
- 将来的に大阪から関西・全国へ拡張できる情報設計

## Safety / Editorial Boundary

50PLUS is an adult community / friendship information site.

It does not provide sexual services, explicit content, deceptive interaction features, coercive targeting, or tools intended for harassment / pickup optimization.

## AI Startup

AI agents should read:

1. current `oosaka0123-sudo/ai-master`
2. this repository's `AGENTS.md`
3. this `README.md`
4. `HANDOFF.md` when it exists
5. current Issues / PRs / Actions / code

Claude Code additionally uses `CLAUDE.md` as its project bootstrap.
