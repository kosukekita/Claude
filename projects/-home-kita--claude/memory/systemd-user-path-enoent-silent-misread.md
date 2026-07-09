---
name: systemd-user-path-enoent-silent-misread
description: systemd --user の PATH に /usr/sbin も anaconda も無く、spawnSync が ENOENT を黙って stdout=null で返すため「ツール不在」を「対象が不正」と誤読する事故が起きる
metadata: 
  node_type: memory
  type: project
  originSessionId: b5c59fca-1c3e-43c9-a89d-49a0d09e7056
---

**systemd --user のジョブから裸のコマンド名を spawnSync すると、対話シェルでは動くのに本番で ENOENT になる**（2026-07-09 [[sheet-factory-daily-sfw-loop]] 実障害）。

- **PATH の落とし穴**: unit の `Environment=PATH` は自分で書いた値がそのまま使われる。akitaken では `sysctl` は `/usr/sbin/sysctl`、`ffprobe`/`ffmpeg`/`curl` は **anaconda 配下にしか無い**（`/usr/bin/ffprobe` は存在しない）。`/usr/sbin` を PATH に足しても ffprobe は直らない → **外部バイナリは絶対パス候補を `existsSync` で解決する**（`const FFPROBE = [...].find(existsSync)`）。anaconda を PATH ごと入れるのは他を壊すので不可。
- **Node の罠**: `spawnSync("x")` はコマンド不在でも throw せず `{ error: ENOENT, status: null, stdout: null }` を返すだけ。`r.stdout?.trim()` は `undefined`、`(r.stdout||"").split(",")` は `[""]`。**`r.error` / `r.status` を見ないと不在が値に化ける**。
- **★本質的な誤り（再発防止の核）**: 「ツールが実行できなかった」を「対象が不正だった」と読み替えたこと。実際は sysctl 不在 → `sysctl=undefined` → 「AppArmor 制限が有効」と誤報して Codex を不当にスキップ、ffprobe 不在 → `dims=0xundefined` → 合格画像(1280x720/260KB)を FAILED 判定し exit 1。**検証ゲートが壊れたときは FAILED ではなく WARN（検証不能）にする**（[[loop-engineering]] の verification debt）。
- **確認の型**: `env -i PATH=<unit の PATH> HOME=... sh -c 'command -v X'` で実測する。修正後も**あえて古い PATH で実行**して、コード側の修正だけで通ることを確かめる。
- **PATH 非依存の代替**: sysctl(8) を呼ばず `/proc/sys/kernel/...` を `readFileSync`。画像寸法は ffprobe が無ければ PNG(IHDR)/JPEG(SOFn) を自前パース（実ファイルで ffprobe と一致を確認済み）。

**Why**: 対話シェル（anaconda 入り PATH）で動作確認したスクリプトが、systemd --user では静かに別物になる。ENOENT が例外にならないので、症状は「ツールが無い」ではなく「対象が異常」の顔をして現れ、原因究明が遠回りになる。
**How to apply**: systemd --user / cron から動くスクリプトを書く・直すときは、外部バイナリを絶対パス解決し、`spawnSync` の `error`/`status` を必ず見る。検証ツールが動かなかった場合を「不合格」に倒さない。同種の罠は hf-watcher・biz-cards 等の他ジョブにも残っている可能性があり未監査（2026-07-09 時点、Claude の月次上限で監査ワークフローが実行できず）。
