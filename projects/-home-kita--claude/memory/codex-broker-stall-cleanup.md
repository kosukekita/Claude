---
name: codex-broker-stall-cleanup
description: Codexジョブが「Starting/Resuming thread」で無音のまま固まるのは長期稼働ブローカの応答不能。認証ではない。掃除手順つき
metadata: 
  node_type: memory
  type: project
  originSessionId: 8766f041-3971-53bb-a375-4b41305dacaa
  modified: 2026-09-01T06:19:11.699Z
---

**Codex ジョブが `Starting Codex Task.` / `Resuming thread ...` の直後で無音のまま進まない場合、原因は認証ではなく `app-server-broker.mjs` の長期残留。** 2026-09-01 実測。

## 見分け方（認証切れとの区別）

- `codex login status` → `Logged in using ChatGPT` なら認証は正常。認証切れなら `token_invalidated` 等が返り、無音にはならない
- ジョブログが3〜4行（Starting → Queued → Resuming thread）で止まり、以後タイムスタンプが増えない
- **決定的証拠**: 同時刻帯に別ワークスペースのジョブも同じ症状で固まる（2026-09-01 は Lower Limb と UKA で同時発生）

## 掃除手順

```bash
# 1) ブローカ一覧と稼働時間・cwd
ps -eo pid,etime,cmd --no-headers | grep app-server-broker | grep -v grep
# 2) 実行中ジョブがあるワークスペースを確認（あるものは温存を検討）
#    state/*/jobs/*.json の status=="running" を見る。ただし phase=="starting" で
#    updatedAt が無いものは「既に死んでいる」ので温存不要
# 3) 停止 → 孤立ソケット削除
kill <PID>...; rm -rf /tmp/cxc-<残す以外>/
```

**罠**: 温存対象を basename 比較で除外するとき、`grep -oE 'cxc-[A-Za-z0-9]+'` の結果に改行が入り比較が失敗して消してしまう（2026-09-01 に実際に発生）。`keep=$(... | tr -d '\n')` で正規化する。

**予防**: ブローカが数日〜数十日稼働しているのを見たら、詰まる前に再起動する。20日稼働のものが実際に詰まった。関連: [[codex-token-invalidation-stale-daemons]]（こちらは認証側の類似問題）
