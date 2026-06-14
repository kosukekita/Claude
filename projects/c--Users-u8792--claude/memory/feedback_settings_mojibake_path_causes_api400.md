---
name: feedback_settings_mojibake_path_causes_api400
description: 設定ファイルや記憶ファイルに化け漢字(U+8792 = u8792のエスケープ化け)の生文字が混入すると、SessionStartで毎回注入され API 400 invalid high surrogate になり /clear で直らない。孤立サロゲートだけ探すと見落とす
metadata:
  node_type: memory
  type: feedback
---

ユーザー名 `u8792` のエスケープ化けである化け漢字（コードポイント U+8792、ここでは生の文字を書かず常にこの数値表記で記す）の**生文字**が、SessionStart で毎ターン送信ボディに入る固定要素（設定ファイル・記憶ファイル・CLAUDE.md 等）に混入すると、そのプロジェクトで Claude Code を起動して「こんにちは」程度の簡単な入力を送るだけで毎ターン `API Error: 400 The request body is not valid JSON: invalid high surrogate in string: line 1 column N`（N は会話が伸びるたび変動）が出続ける。これらの固定要素は起動のたび読み直されて送信ボディに焼き付くため **`/clear` では直らない**（会話履歴を消すだけで再注入は止まらない）。U+8792 は正規の漢字でありサロゲートではないため、内部で送信用 JSON にエンコードされる過程で不正サロゲートを生む。

**Why:** 2026-06-14、Osteoporosis プロジェクト（`P:/Code/Research/Osteoporosis`）で発生。当初は孤立サロゲート(U+D800〜U+DFFF)だけを総当たりスキャンしたため、記憶・フック出力・全transcript(1076件)・プロジェクト内ファイル・git status が全てクリーンに見え原因を掴めなかった。第一の汚染源は `settings.local.json` の `additionalDirectories` に化けパスが入っていたこと。だがそれを除去しても 400 が継続。最終的な真因は **グローバル記憶ディレクトリ内の複数ファイル（この問題を説明・記録した記憶ファイル自身を含む）に U+8792 の生文字が書かれており、それが SessionStart フックで `additionalContext` として毎回注入されていた**こと。検出は U+8792 を含めて行う必要があった（`[char]0x8792` / `ord(c)==0x8792` で検出）。

**How to apply:**
1. API 400 invalid high surrogate が出たら、**孤立サロゲートだけでなく化け漢字 U+8792 自体**も捜索対象にする。
2. `/clear` で直らない 400 は、会話履歴ではなく**毎回読み直される固定要素**（設定ファイル・CLAUDE.md・記憶・git status・MCP instructions 等）を疑う。特に記憶ファイルと `settings.local.json` の additionalDirectories などパス系設定を最優先で見る。
3. 「特定プロジェクトでだけ起動直後に出る」なら、そのプロジェクトの `.claude/` 配下と、注入されるグローバル記憶を確認する。
4. 修正は化け文字の除去。記憶や設定の中で U+8792 に言及する必要があるときは**生文字を書かず必ず数値表記（U+8792）で書く**。パスを書くときはフォワードスラッシュ `C:/Users/u8792/...` を使い、ユーザー名 u8792 をバックスラッシュ直後に置く形（また化ける）を作らない。
5. 検出・サニタイズは `~/.claude/work/scan_u8792.py`（U+8792 と孤立サロゲートを数値検出）と `sanitize_u8792_v2.py` を使う。
6. 根本予防は [[feedback_u8792_path_unicode_escape]]（パスは常にフォワードスラッシュ）。関連: [[feedback_surrogate_in_grep_pollutes_api_body]]（会話コンテキスト汚染版。復旧は /clear のみ。本件は永続ファイル汚染で /clear では直らずファイル修正が必要、という別メカニズム）。
