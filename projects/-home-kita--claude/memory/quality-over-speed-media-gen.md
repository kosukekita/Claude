---
name: quality-over-speed-media-gen
description: ユーザー恒久方針-メディア生成は処理時間より精度/品質を優先。offload/block-swapは品質に無影響なので遠慮なく使ってよい
metadata: 
  node_type: memory
  type: feedback
  originSessionId: 7f792248-9bef-40fb-8283-33d15119eae9
---

★ユーザー恒久方針（2026-07-13 明示）: 画像/動画のローカル生成は、**処理時間より精度・品質を優先**する。速度のために品質を落とす選択（steps削減・解像度削減・フレーム間引き等）を、ユーザーに断らず勝手にやらない。

**Why:** ユーザーが明言「処理時間より精度が大事」。長時間ジョブは systemd-run＋ウォッチャーで無人完走できるので、時間はコストになりにくい。

**How to apply:**
- **offload/block-swap は品質に一切影響しない**（`--offload`=double_blocks_to_swap, `--offload-single`=single_blocks_to_swap, `--offload-io`=txt/img_in offload, diffusers の sequential/cpu offload も同様）。重みを CPU RAM ⇄ GPU VRAM で出し入れするだけで、計算・出力はビット同一、遅くなるだけ。**VRAMのために遠慮なく多めに使ってよい**（品質と無関係）。「逃がしすぎ」は速度の話であって精度の話ではない。
- **品質に実際に効くのは別軸**: 量子化(fp8/4bit)=品質低下方向のトレードオフ／**steps↑・解像度↑・cfg適正=品質向上**。速度のためにこれら（特にsteps/解像度/frames）を削るのは**事前確認してから**。
- 迷ったら「時間はかかるが高品質」を既定に。より高品質が要るなら offload ではなく steps(例30→40〜50)・解像度を上げる。
- HunyuanCustom等のローカル生成: high-res で VRAM 不足なら single-block swap を増やして解像度/stepsは維持する（swapは無害なので）。

関連: [[hunyuancustom-r2v-nogo]] [[optimal-gen-models-table-and-new-model-eval]] [[ltx23-crossview-ic-lora-local]] [[gen-image-gpu-zombie-oom]]
