# Global Rules

- **Language**: Always respond in Japanese (常に日本語で回答してください).

## Skill Security

スキル追加時は `skill-scanner scan <path> --use-behavioral` を実行し、HIGH/CRITICAL は精査の上で却下（誤検知は許容）。

## 実装前の理解度確認（必須）

アプリ/AI モデルの**本実装コードに着手する直前**に、以下を必ず実行する:

1. 設計方針・アーキテクチャ・主要なトレードオフについて**理解度を試すクイズ問題を出題**する
2. ユーザーが正しく答えられるまで実装を開始しない
3. 理解が不十分な場合は図解・例示・類比で説明し、再度クイズで確認する

discovery/plan/brainstorming フェーズはブロックしない。クイズは Plan Mode 中なら AskUserQuestion、それ以外はテキストで出題する。

## Workflow Best Practices

### 開発フロー
- **Plan Mode 優先**: 複雑なタスクは Plan Mode でアーキテクチャを固めてから実装
- **1機能 = 1会話**: 大規模開発では機能単位で会話を分割（個人開発規模なら1スレッドでも可）
- **セッション間共有**: `SCRATCHPAD.md` や `plan.md` に進捗・計画を書き出し、次のセッションで参照

### トラブル対応
- **ループ時の対処**: 指示を重ねるのではなく、会話をクリアするかアプローチを根本から変える
- **Hooks 活用**: ファイル変更時に Prettier・型チェックを自動実行して技術的負債を防ぐ

<!-- wmux:start — AUTO-MANAGED BY wmux. Do not edit this section manually. -->

# wmux

You are running inside wmux, a terminal multiplexer with a browser panel on the right side that the user can see in real-time.

## Browser

For any web browsing task, use the `wmux browser` commands so the user can watch in the browser panel. Do NOT use Playwright, Firecrawl, or WebSearch — they open invisible windows the user cannot see. If the user explicitly asks for one of those tools, use it.

```bash
wmux browser open <url>          # navigate
wmux browser snapshot            # get accessibility tree with @eN refs
wmux browser click @eN           # click element
wmux browser type @eN <text>     # type into element
wmux browser fill @eN <value>    # set input value
wmux browser get-text            # get page text
wmux browser screenshot          # capture screenshot
wmux browser eval <js>           # run JavaScript
wmux browser back                # go back
wmux browser forward             # go forward
wmux browser reload              # reload page
```

Workflow: `browser open <url>` → `browser snapshot` → read tree → `browser click/type @eN` → `browser snapshot` again.

Refs (`@e1`, `@e2`...) expire after page changes — always re-snapshot.

<!-- wmux:end -->
