---
name: hunyuan-highres-and-gpu-loop-lessons
description: GPU長時間生成の運用規律(killするtimeout禁止/停止せず空きGPU並列/進捗可視化)＋HunyuanCustom高解像の実測(block-swapは速度もVRAMもほぼ動かさない)
metadata: 
  node_type: memory
  type: feedback
  originSessionId: 7f792248-9bef-40fb-8283-33d15119eae9
---

★ユーザー指摘＋実測（2026-07-13, HunyuanCustom 736×1280 Shot生成で発生）。GPU長時間ジョブの運用規律と、HunyuanCustom高解像の速度の真実。

## 運用規律（ユーザー恒久・[[quality-over-speed-media-gen]]と対）
- **killするtimeoutを付けない**。品質優先の長時間生成に、生成を殺すtimeoutは方針と真逆。**実質無制限（`--timeout 86400`）＋ComfyUIを別サービス化（wrapperは`--server`で接続・`--keep-server`）**して、働いているジョブを絶対に殺さない。**Why:** 旧run(118分・ほぼ完成間近)をwrapperのtimeout(120分)寸前で自ら停止し全損させた事故。timeoutが無ければ数分後に完成していた可能性大。
- **停止せず、空いてるGPUで並列**。動いているジョブを止めて別設定を始めない。2枚目GPUが空いていれば、そこで別seed/別設定/次ショットを**並列**に回す。**How:** ComfyUIをGPU毎に別ポートで起動（`comfyui_serve.sh --port 8189 --gpu 1`）、各wrapperを`--server http://127.0.0.1:<port> --gpu <n>`で繋ぐ。**1クリップは1GPU**（HunyuanCustomはテンソル並列不可＝1本を2枚に分割/96GB合算は不可。block-swapの退避先もCPUでGPU2ではない）。但し**複数ジョブは両GPU並列可**。
- **進捗を可視化する**。`gen_hunyuan_custom.py`は spawn した ComfyUI の stdout/stderr を DEVNULL に捨てるので tqdm(step進捗)が見えない→**ComfyUIを別サービスで起動しログにリダイレクト**すれば `N/30 [.. , 秒/it]` が読める。`tr '\r' '\n' < server.log | grep /30 | tail`。これを怠り2時間ブラインドで走らせた。

## HunyuanCustom 高解像の速度・VRAM実測（A6000 1枚・--no-sage・129f・30step）
- **736×1280 ≈ 260秒/step ≈ 2h20m/shot**。512×896 ≈ 70s/step ≈ 35分。640×1120 ≈ 160s/step ≈ 80分。**高解像は本質的に遅い**（巨大attention、no-sage）。
- **★block-swap(`--offload`=double_blocks_to_swap / `--offload-single`=single_blocks_to_swap)は速度もVRAMもほぼ動かさない**（実測: single=0/12/30 いずれも VRAM ~22–34GB・~4分/step）。**遅さの真因は「解像度×フレーム×attention」であって退避ではない**。「退避しすぎで遅い」は誤診だった。退避は[[quality-over-speed-media-gen]]の通り品質にも無影響。
- **高解像を速くしたいなら**: ①解像度/フレームを下げる（512×896=4x速い）②SageAttention導入（要ビルド・未検証だが高解像に効く見込み）③steps削減。**退避を弄るのは無意味**。
- 実装補足: HyVideoBlockSwap は double max20 / single max40。`gen_hunyuan_custom.py`に`--offload-single`/`--offload-io`を追加済（VRAM調整用だが速度対策にはならない）。VRAMは退避量にほぼ非依存（~22GB @ full-load）なので736×1280はno-swapでも48GBに収まる(34GB)。
- **検証優先の型**: 高解像本番(2h20m)の前に、512×896(~35分)で同一性・構図・手だけ描写・質感を先に検証してから高解像に賭けるのが安全（2h20mを無検証で賭けない）。ただしユーザーが「高解像のまま待つ/品質優先」と言えばそれに従う。

関連: [[quality-over-speed-media-gen]] [[hunyuancustom-r2v-nogo]] [[ltx23-crossview-ic-lora-local]]
