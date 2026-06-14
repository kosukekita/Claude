---
name: feedback_settings_mojibake_path_causes_api400
description: settings.local.json の additionalDirectories 等に化け漢字 螒(U+8792) を含むパスが混入すると、起動＋任意入力で毎ターン API 400 invalid high surrogate になり /clear で直らない。孤立サロゲートだけ探すと見落とす
metadata:
  node_type: memory
  type: feedback
---

プロジェクトの `.claude/settings.local.json`（や他の起動時読み込み設定）の `permissions.additionalDirectories` 等に、ユーザー名 `u8792` のエスケープ化けである `螒`(U+8792) を含むパス（例: `C:\Users螒\.claude\plans`）が書き込まれていると、そのプロジェクトで Claude Code を起動して「こんにちは」程度の簡単な入力を送るだけで毎ターン `API Error: 400 The request body is not valid JSON: invalid high surrogate in string: line 1 column N`（N は会話が伸びるたび変動）が出続ける。設定は起動のたび読み直されて送信ボディに焼き付くため **`/clear` では直らない**（会話履歴を消すだけで設定の再注入は止まらない）。修正は当該設定ファイルから化けパスのエントリを除去すること。

**Why:** 2026-06-14、Osteoporosis プロジェクト（P:\Code\Research\Osteoporosis）で発生。記憶・フック出力・全transcript(1076件)・プロジェクト内ファイル・git status を「孤立サロゲート(U+D800〜U+DFFF)」で総当たりスキャンしたが全てクリーンで原因が掴めなかった。真因は `settings.local.json` の `additionalDirectories: ["C:\\Users螒\\.claude\\plans"]`。`螒` は**正規の漢字でありサロゲートではない**ため孤立サロゲート検出器をすり抜けていた。`螒` を含む文字列が Claude Code 内部で送信用JSONにエンコードされる過程で不正サロゲートを生み、400 になっていた。`螒` の出どころは `螒`(ユーザー名) のエスケープ化け＝ [[feedback-u8792-path-unicode-escape]] と同根。

**How to apply:**
1. API 400 invalid high surrogate が出たら、**孤立サロゲートだけでなく化け漢字 `螒`(U+8792) 自体**も捜索対象にする。`[char]0x8792` で検出する。
2. `/clear` で直らない 400 は、会話履歴ではなく**毎回読み直される固定要素**（設定ファイル・CLAUDE.md・記憶・git status・MCP instructions 等、送信ボディに常時入るもの）を疑う。特に **`settings.local.json` の additionalDirectories などパス系設定**を最優先で見る。
3. 「特定プロジェクトでだけ起動直後に出る」なら、そのプロジェクトの `.claude/` 配下（settings.local.json / settings.json）を真っ先に確認する。
4. 修正は化けパスのエントリ削除。クリーンなUTF-8(BOMなし)で書き直す。元ファイルは `.bak` でバックアップ。
5. 根本予防は [[feedback-u8792-path-unicode-escape]]（パスは常にフォワードスラッシュ `C:/Users/u8792/...`、設定書き込み時もバックスラッシュ+u8792 を直書きしない）。
6. 関連: [[feedback_surrogate_in_grep_pollutes_api_body]]（こちらは会話コンテキスト汚染で /clear が唯一の復旧。今回は設定ファイル汚染で /clear では直らず設定修正が必要、という別メカニズム）。
