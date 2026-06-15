---
name: feedback-codex-rescue-hang-causes
description: codex:rescue委譲がハング/途中切れ/no outputになる真因はランナー呼び出し方(stdinブロッキング/120秒タイムアウト/background+stdin)。Codexの生成コマンドではない
metadata: 
  node_type: memory
  type: feedback
  originSessionId: 4fb3f955-1e55-4f42-836a-465b6f37acda
---

`codex:rescue`（codex-consult 経由）で Codex 委譲が「コマンドが途中で切れる/ハング/no output」になる真因は**ランナー（codex-companion.mjs）の呼び出し方**で、Codex が生成するシェルコマンドではない。3大原因:

1. **stdin ブロッキング読み** — `readStdinIfPiped()` が `fs.readFileSync(0,"utf8")`（fs.mjs:39）で同期読み。プロンプトを引数で渡さず stdin 依存にすると、入力が来ず**無限ハング**。→ プロンプトは必ず `/codex:rescue` の引数で全文渡す。
2. **親 Bash の 120 秒タイムアウト × Codex の長時間推論** — `--effort high` は数分かかる。foreground 実行だと 120 秒で途中切れ／no output。→ 重い委譲は最初から background（`/codex:status`・`/codex:result` で回収）。目安「3分以内で返ると確信できなければ background」。
3. **`--background` + stdin の同時使用** — detached（stdio:"ignore"）で stdin が無いのに読むと確実ハング。

**Why:** 2026-06-15、skills レビューを Codex に2回委譲して両方つまずいた（1回目=途中切れ、2回目=no output だが本文はセッションに残存）。ユーザーが貼った全角クォート入りコマンドが疑われたが、Codex セッションログの実コマンドは全て ASCII クォート（sq=0）で、全角版はログに無し＝**表示/転記段階での ASCII→全角変換**と判明。command-log には日本語が cp932 で激しく化けた行もあった。Windows では Codex は `shell:true`（Node→cmd.exe→codex の3段ツリー、app-server.mjs:244）で起動され、ツール実行は PowerShell/cmd 系（`Select-Object`/`Measure-Object`/`cmd /c` が動作）。`rg | Select-Object` 混成は PowerShell で動くので無害。

**How to apply:**
- 重い/`--effort high`/レビュー・実装委譲は **background**。短い一次見解だけ foreground。
- プロンプトは**常に引数で全文**渡す（空委譲＋stdin 待ち禁止）。
- 全角クォート `“ ”` はクォート未閉ハングの元 → コマンドは ASCII `"`/`'` に正規化。→ [[feedback_u8792_path_unicode_escape]]
- no output でも本文回収可: rollout-*.jsonl から最長 assistant メッセージを UTF-8 ファイル経由で。→ [[feedback_codex_review_output_via_session_jsonl]]
- 恒久対策は codex-consult/SKILL.md の Step 3 と Troubleshooting に記載済み（2026-06-15）。Codex の config.toml に shell 指定は無い（既定挙動依存）。
