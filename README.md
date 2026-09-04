# 50PLUS

50代からの友活・仲間づくり情報サイト「50PLUS」。

趣味・イベント・地域交流を通じて、成人同士が自然につながれる場所や活動を紹介するWebプロジェクトです。

## Publishing targets

### Current development preview

- GitHub Pages: `https://oosaka0123-sudo.github.io/50plus/`
- Purpose: 完成までの公開確認・スマホ確認・クライアント/関係者確認
- Preview HTML is deployed with `noindex,nofollow` injected by GitHub Actions so the temporary GitHub Pages site is not treated as the final SEO destination.

### Final production target

- Planned final URL: `https://50plus.rss7.net`
- Final hosting: Lolipop
- Migration to Lolipop happens **after the site is considered complete and the user explicitly moves to final production**.

GitHub Pages is therefore a temporary public development/preview environment, not a replacement for the final Lolipop production target.

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
6. GitHub Actions publishes the current `main` to the GitHub Pages preview
7. Continue development and QA on GitHub Pages until completion
8. After completion, perform the deliberate final migration to Lolipop and verify `https://50plus.rss7.net`

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
