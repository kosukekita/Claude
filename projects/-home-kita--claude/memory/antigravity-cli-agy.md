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

## ★終わった agy の TUI を放置しない（実測 2026-09-03）

**完了後の agy TUI は tmux に残しておくと CPU とおそらく API クォータを食い続ける。** 実測: 6セッションが
20〜28日間 detached のまま生存し、**各6〜10日分の CPU 時間**を累積、当時も各25〜42%（合計約180%）を消費。
1つは Google API への ESTABLISHED 接続を保持していた。同日 `agy` がクォータ上限（"Individual quota
reached... Resets in 45h"）で使えなかったのは、これらの残骸が消費していた可能性がある（状況証拠）。

- 画面は「完了報告」「DONE」「フィードバック調査」で待機中でも、プロセスは回り続ける。
- **委譲が終わったら必ず TUI を終了させる**（`Ctrl+C` を2回で正常終了する。実測で6/6成功）。
  その後 `tmux kill-session`。強制 kill の前に必ず正常終了を試すこと（未 flush データ保護）。
- 掃除前の点検: `pstree -p <pane_pid>` の数字は**スレッド**で子プロセスではない（`pgrep -P` が0なら孤児化しない）。
  listen ポートは 127.0.0.1 限定で外部依存なし。GPU を使う ComfyUI は systemd 管理で tmux とは無関係。
- 消す前に `tmux capture-pane -p -S -3000` で全セッションのスクロールバックを退避しておくと後から追える。
