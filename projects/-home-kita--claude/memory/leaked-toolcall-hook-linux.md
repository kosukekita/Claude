---
name: leaked-toolcall-hook-linux
description: ツールコール漏洩(count/court/call + <invoke>)検知フックがLinuxで無効だった原因とnode版での恒久対策
metadata: 
  node_type: memory
  type: feedback
  originSessionId: fa37c53f-75f8-403f-bc64-3847918c0990
---

ハーネスのシリアライズ不具合で、ツール呼び出し `<function_calls><invoke name=...>` の開始マーカーのプレフィックスが落ち、`count`（または `court`/`call`）という裸トークン + 生 `<invoke name=...>` テキストとして出力され、ツールが実行されずサイレント失敗する既知バグがある。**モデル出力境界の内側で起きるので、いかなるフックも漏洩自体は予防できない**（事後検知して次ターンで再送を促すのが限界）。

**「対策フックを入れたのに再発した」原因（2026-06-23 確定）**: 対策フック `~/.claude/hooks/detect-leaked-toolcall.ps1` が PowerShell 専用で、settings.json の Stop 登録もガード無しの `powershell -File ...` 直叩きだった。Linux 機には powershell/pwsh が無いため、Stop フックは毎回コマンド不在で失敗し、**検知が一度も走っていなかった**（Windows 機でのみ機能していた）。

**Why**: フックは `.ps1` 1種類しか無く、クロスOSになっていなかった。さらに settings.json 内で同種フックの登録パターンが3流儀混在（ガード無し直叩き / `|| true` 握り潰し / if-else）していて、`detect-leaked-toolcall` だけ最も脆い直叩きだった。

**How to apply**: 検知フックは **node版 `detect-leaked-toolcall.mjs` を第一候補**にする。理由 = このリグの `jq`・`python3` は anaconda 版（`libtinfo.so.6` で LD を汚染。Codex の bash 版は実行毎にこの警告を吐いた）で、**`/usr/bin/node` だけがクリーン**。node 版は警告ゼロ、`.mjs` 1本で Win/Linux 両対応、JSONL パースも単純。settings.json の Stop 登録は3段フォールバック: `command -v node → node .mjs` / `elif powershell → .ps1` / `else bash .sh`。検証済み（漏洩 transcript で exit 2・警告なし、正常 transcript で exit 0）。`.mjs` は `stop_hook_active===true` で再ナグを抑止。

**フックでも防げない以上のモデル側緩和**（CLAUDE.md「ツールコール漏洩バグへの対処」にも追記済み）: ツール呼び出しは単独ターンで出す / 結果が返らなければ漏洩を疑い再送 / **同一会話で2回以上漏れたらコンテキスト汚染なので `/clear` を推奨**（同一コンテキストの再試行は再発しやすく、フックの再送促しも効きにくい）。

関連: anaconda LD 汚染は [[video-media-studio-skill]] でも既出（env.sh が掃除）。フック解析系を選ぶときは「anaconda 版でなく `/usr/bin/node` を使う」が一般則。漏洩したときの対処順序（前置き消し再送→/compact→/rewind→引き継ぎ）と予防策（サブエージェント3〜4体・1セッション1テーマ等）の運用プレイブックは [[leaked-toolcall-mitigation-playbook]]。
