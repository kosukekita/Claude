---
name: feedback-codex-review-output-via-session-jsonl
description: codex:rescueがno output/中間状態で返ってもCodex本文は~/.codex/sessions/YYYY/MM/DD/rollout-*.jsonlに残る。最長assistantメッセージを抽出する
metadata: 
  node_type: memory
  type: feedback
  originSessionId: 4fb3f955-1e55-4f42-836a-465b6f37acda
---

`codex:rescue`（codex-consult 経由の Codex 委譲）のラッパーが `<task-notification>` で「no output」や中間状態の文言（"Codex is actively reading..."）を返すことがあるが、**Codex の実レビュー本文は ~/.codex/sessions/YYYY/MM/DD/rollout-*.jsonl に必ず残る**。最新ファイル≠目的のセッションのことがあるので、複数ファイルを横断して `role=assistant` の最長メッセージを拾うのが確実。

**Why:** 2026-06-15、Codex に skills のレビューを2回委譲。1回目は Codex が `Get-Content` をサンドボックスのコマンドポリシーで弾かれてファイルを読めず途中終了（→対象ファイル内容をプロンプトに全文埋め込んで再委譲したら成功）。2回目はラッパーが「no output」と返したが、実際は別セッションファイル(18-08-47)に 6542 字の完全なレビューが書かれていた。コンソールに直接 print すると cp932 で化けるので、抽出は必ず UTF-8 でファイルに書き出してから Read する。

**How to apply:**
1. `ls -t ~/.codex/sessions/<年>/<月>/<日>/rollout-*.jsonl | head -4` で直近数本を見る。
2. 各 jsonl を Python で走査し `type==message & role==assistant` のテキストを集め、**最長**を本文とみなす（短い断片は思考/ツール段階）。
3. 抽出結果は `print` せず UTF-8 でファイルに書き出し、Read ツールで開く（コンソール print は cp932 化け）。
4. Codex にファイルを読ませる委譲が `Get-Content`/`rg` ポリシーで止まるなら、**レビュー対象を要約でなく全文プロンプトに埋め込む**（cwd 探索・コマンド実行に依存させない）。関連: [[project_grok_media_skill]]（外部CLI委譲は実ターミナル/セッション保存系）, [[feedback_u8792_path_unicode_escape]]（通知のバックスラッシュパスはスラッシュ変換してから Read）。
