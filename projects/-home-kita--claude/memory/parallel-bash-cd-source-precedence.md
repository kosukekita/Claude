---
name: parallel-bash-cd-source-precedence
description: "bashで `cd && source && (leg0) & (leg1) & wait` は優先順位でleg1がcd/sourceされず環境を失い全滅する。2GPU並列生成の実バグと修正"
metadata: 
  node_type: memory
  type: reference
  originSessionId: 7f792248-9bef-40fb-8283-33d15119eae9
---

**症状（2026-07-11 実障害）**: nsfw-auto phase1 の Qwen 18枚 2GPU並列生成で、**GPU1側（偶数ファイル）9枚が全滅・GPU0側9枚は全成功**（have: 9/18）。GPU1単体テストは成功、2枚同時再現も（cd/source を先に別実行していたため）成功 → 「並列そのもの」ではなく**ワンライナーの構造**が原因だった。

**根本原因（bashの演算子優先順位）**: `&&` は `&` より強く結合する。
```
cd DIR && source env.sh && ( leg0 ) & ( leg1 ) & wait
```
は次の3コマンドに分解される:
1. `cd DIR && source env.sh && ( leg0 )` を**バックグラウンド実行**（`&`）
2. `( leg1 )` を**バックグラウンド実行**（← cd も source もされない！）
3. `wait`
`cd`/`source` は #1 のサブシェル内だけで効き、親シェルには残らない。よって **leg1 は cwd も `$UV` 等の環境変数も無い**まま走り、`"$UV" run scripts/...` が `$UV` 空＋相対パス不成立で毎回失敗 → GPU1側が全滅。leg0 は cd/source 込みなので成功。

**修正**: 波括弧 `{ }` で並列部を1グループにまとめ、`cd`/`source` を親シェルで先に確定させる。
```
cd DIR && source env.sh && { ( leg0 ) & ( leg1 ) & wait; }
```
これで `cd`/`source` は現在のシェルで実行され、`{ ... }` グループ内の両サブシェルが同じ cwd と export 済み環境を継承する。実機で GPU0/GPU1 両方生成を確認。

**一般則**: 「前処理（cd/source/export）→ 複数ジョブを `&` で並列 → `wait`」を1つの `bash -c` に書くときは、**並列部を必ず `{ ...; }` か関数で包む**。包まないと最初のジョブにしか前処理が効かない。デバッグの罠: cd/source を別実行してから並列を試すと再現しないので、必ず本番と同じ単一 `bash -c` で再現する。exit は `wait` が 0 を返すので、`spawnSync` の exit だけ見ると成功に見える → 成果物の個数で判定する。

関連: [[nsfw-auto-pipeline-explicit-video.md]] [[gen-image-gpu-zombie-oom.md]] [[seed-randomize-always-image-gen]]
