---
name: antigravity-cli-agy
description: Antigravity CLI の実体はコマンド名 agy（このLinux機・Codex不可時の委譲先候補）
metadata:
  type: reference
---

**Antigravity CLI = `agy`**（`~/.local/bin/agy`・v1.1.11 確認 2026-08-07・このLinux機 akitaken）。

- ユーザーが「antigravity cli に委譲して」と言ったらこれを指す。`which antigravity` では見つからない（コマンド名が `agy`）。
- 実測の起動形: `agy --model gemini-3.6-flash-high --mode accept-edits`（モデル指定・編集自動承認モードあり）。
- 位置づけ: Codex CLI が使えないときの実装委譲先の1つ。Gemini CLI（`/usr/bin/gemini`・headless は `--approval-mode yolo -p "..."`）も代替になる。指名があれば指名先へ直行（[[external-ai-consult-fallback]] と同じ規則）。
- 経緯: 2026-08-07 に「antigravity は未検出」と誤報告しかけた（検索パターンが anti/grav/gemini のみで agy に不一致）。ツール探索は `compgen -c` の部分一致だけでなく、実行中プロセス（`pgrep -fa`）も見ると発見できることがある。
