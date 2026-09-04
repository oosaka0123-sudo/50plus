# 50PLUS

50代からの友活・仲間づくり情報サイト「50PLUS」。

趣味・イベント・地域交流を通じて、成人同士が自然につながれる場所や活動を紹介するWebプロジェクトです。

## Public URL

- Planned: `https://50plus.rss7.net`

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
6. GitHub Actions deployment to Lolipop after this project's deployment configuration is verified

The deployment architecture will be based on the proven `oosaka0123-sudo/claudecode-kyoshitsu` pattern, adapted specifically for the 50PLUS server directory and safety requirements.

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
