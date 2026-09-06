# 50PLUS

50代からの友活・仲間づくり情報サイト「50PLUS」。

趣味・イベント・地域交流を通じて、成人同士が自然につながれる場所や活動を紹介するWebプロジェクトです。

## Publishing targets

### Production

- Production URL: `https://oosaka0123-sudo.github.io/50plus/`
- Primary hosting: dedicated GitHub Pages for `oosaka0123-sudo/50plus`
- Source of truth: this repository `main`
- `.github/workflows/deploy-pages.yml` publishes the static production artifact after approved changes reach `main`.
- Production HTML is indexable; preview-only `noindex,nofollow` is not used in the dedicated production artifact.
- `robots.txt`, `sitemap.xml`, canonical URLs and Open Graph URLs use the current GitHub Pages production URL.
- `https://50plus.rss7.net` may be attached later as an optional GitHub Pages custom domain; it is not required for current production.

### Temporary preview bridge

The older preview bridge may remain available temporarily at:

- `https://oosaka0123-sudo.github.io/ai-agent/50plus/`

The `ai-agent` bridge is preview-only and injects `noindex,nofollow`. It must not be treated as the production URL or as another source of truth.

### Lolipop fallback

The existing manual Lolipop deployment/preflight path is retained as an emergency fallback only. Lolipop is not the normal production target and its secrets are not required for standard GitHub Pages publishing.

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
7. `Deploy 50PLUS GitHub Pages` publishes approved `main` automatically
8. Verify the production deployment at `https://oosaka0123-sudo.github.io/50plus/`

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
