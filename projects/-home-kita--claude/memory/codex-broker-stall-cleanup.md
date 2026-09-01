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

## 追記（2026-09-01）: ブローカ再起動後は read-only で立ち上がる

掃除して新しいブローカになった直後、Codex が**ファイルシステム全体 read-only** で起動し
「cp: Read-only file system」で何も書けなくなった。原因は `codex-companion.mjs` の
`sandbox: request.write ? "workspace-write" : "read-only"`（488行）＝**`--write` 未指定**。

**実装を委譲するときは必ず `--write` を付ける**（`--fresh`/`--resume`/`--background` と併記可）。
調査・相談だけなら不要。掃除の直後に実装タスクが「何も変更していません」と返ってきたら、
まずこのフラグを疑う。

## 追記2（2026-09-02）: `--resume` は `--write` を無視する

`--write` を付けたのに read-only で拒否される場合、原因は `--resume`。
ジョブJSONの `request.write` は True になっているのに書けない ＝ **サンドボックスは
スレッド作成時に固定され、resume は既存スレッドの設定を引き継ぐ**。

**対処**: 書込みが要る作業を resume 中のスレッドで頼まない。`--fresh --write` で新スレッドを作り、
必要な文脈（前スレッドの結論・実測値）はプロンプトに転記して渡す。
逆に、調査・相談だけなら resume のままでよい。
