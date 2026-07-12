---
name: ltx23-crossview-ic-lora-local
description: LTX-2.3 22B CrossView IC-LoRA(1動画→別カメラアングル)のローカルheadless導入。ComfyUI経路・実機動作確認済み・環境固有パッチ
metadata: 
  node_type: memory
  type: reference
  originSessionId: 7f792248-9bef-40fb-8283-33d15119eae9
---

`Cseti/LTX2.3-22B_IC-LoRA-CrossView-Prompt`（1本の参照動画→同じシーンを別カメラアングルで再撮影する v2v IC-LoRA、v1 pilot step13700）をローカルで**headless実行できるよう導入し、実機で完走確認した**（2026-07-13）。video-media-studio スキルに統合済み。

## 動かし方（確定）
- 入口: `scripts/gen_ltx_crossview.py`（薄いラッパー。ComfyUIサーバをspawn→参照動画をinputへ→API workflow POST→poll→mp4回収。torchは自プロセスに入れない＝HunyuanCustom/LTX-2.3委譲型と同じ）。
- CLI: `--ref/--azimuth/--elevation/--distance/--out/--ic-lora-scale/--speed-lora-scale/--gpu/--no-sage/--port/--timeout`。方位/高さ/距離は crossview 固定語彙（7×3×3=63通り、`reference/crossview_captions_all_63.txt`）で内部バリデーション。プロンプトは `crossview. new camera angle: {方位}, {高さ}, {距離}.`。
- **★起動は必ず `systemd-run --user`**（＝毎朝phase1と同じ、プロセス木から独立）。このマシンは fork/前景/nohup/run_in_background で起動した数分かかるGPUプロセスを **exit 144 で殺す**が、systemd起動なら生き残って完走する。これが最重要の環境知見。
- ComfyUI本体=`/data/kita/ComfyUI`（専用uv venv・python3.11・torch2.5.1+cu121・anaconda非依存）。基盤~42GBは取得済み（transformer fp8 22G / speed LoRA 2.6G / IC-LoRA 97M / VAE3種 / gemma 13G / upscaler）。custom node: ComfyUI-LTXVideo, KJNodes, VideoHelperSuite, rgthree, RES4LYF, comfyui-int-and-float, **ComfyUI_Fill-Nodes(FL_FloatToInt用)**。

## 実測（合否の基準）
- 参照(512×512/72f)→**出力 1024×1024 / 97フレーム / 4.0秒**（512×512 passthroughではなく本物＝2xアップスケール込み）。**~186秒（約3分）**、**ピークVRAM ~45GB（単一A6000 48GBに収まる）**。
- 合否＝出力が入力と違う解像度(1024)・数分かかる・nb_frames≈指定値。**3秒で終わり512×512が出たら失敗（=素通り）**。

## このワークフローに入れた「実行用パッチ」（この環境で回すため必須）
`reference/crossview-workflow/ltx2.3-ic-lora-crossview.json` に直接編集済み:
1. sageパッチ2ノード(5067 LTX2MemoryEfficientSageAttentionPatch / 5068 PathchSageAttentionKJ) と ModelPatchTorchSettings(5069) を **mode=4 バイパス**（pytorch2.5.1ではfp16累積(要2.7.1)・SageAttention不可。いずれも任意の速度/メモリ最適化で出力品質は不変）。
2. ImageResizeKJv2(5091) の `nvidia_rtx_vsr → lanczos`（RTX VSR未導入）。
3. **フレーム数 INTConstant(5099) を 241 → 97 に削減**（241fフルは単一48GBでSamplerCustomAdvanced OOM=peak48647MiB。97fで~45GBに収まる）。フル尺が要るなら frames を戻して解像度/フレーム調整 or マルチGPU。
ラッパーの spawn_comfyui は ComfyUI に `--lowvram` を渡す（`cmd += ["--", "--lowvram"]`。`--`以降がComfyUI引数）。

## ui_to_api.py（UI JSON→API prompt変換）の要点＝ハマりどころ
`scripts/ui_to_api.py`。順序が重要: **bypass_reroutes → resolve_get_set → inline_subgraphs → bypass_muted → convert**。
- **inline_subgraphs**: `definitions.subgraphs` を展開（SUBGRAPH_INPUT_ID=-10 / OUTPUT=-20）。このワークフローは2サブグラフ。
- **resolve_get_set**: KJNodes GetNode/SetNode の名前付きチャネルを実配線に解決（SetNode×16/GetNode×17）。
- **bypass_muted（★3秒no-opの真因だった）**: mode=4(muted/bypassed)ノードは「同型のinput→outputを橋渡し」して除去、mode=2は削除。これが無いとflattenがmuteノードを有効扱いで残しinput欠落→validation失敗で素通り出力(512×512)になる。
- MarkdownNote等 object_info に無いUI専用ノードはskip。

## つまずきlog（再発防止）
- kornia ImportError(`cannot import name 'pad'`)→ `kornia==0.7.3` にピン（ComfyUI-LTXVideoが `kornia.geometry.transform.pyramid.pad` を使う。0.8.3で削除。uv pipで固定）。ComfyUI venvは "No module named pip" なので `uv pip install --python <.venv/bin/python>`。
- LatentUpscaleModelLoader "model_name not in []"→ フォルダキーは `latent_upscale_models`（`upscale_models`でない）。upscalerをそこへsymlink。

## 使い分け（★入力モダリティが三者三様。CrossViewだけ「動画入力のv2v」）
- **CrossView = v2v**。入力は**動画1本まるごと**（参照動画がIC-LoRAのin-contextガイド。開始画像不要）で、それを別カメラアングルに再レンダ＝novel-view。公式READMEも "Type: Video-to-Video"。**r2vではない**（当初r2vと誤記した→2026-07-13訂正）。
- 「参照から別の動画を作る」系の対比（入力が違う）: **静止画1枚+テキスト→任意シーン = HunyuanCustom(r2v)** / **別人のモーション動画(骨格)を転写 = Wan-VACE(v2v・動き転写)** / **動画1本→同じテイクを別視点 = このLTX CrossView(v2v・novel-view)**。
- CrossViewはv1 pilotなので**角度追従は不安定**なことがある（step13700・実験的）。IC-LoRA strength=1.5 / speed LoRA=0.6 が既定。
関連: [[hunyuancustom-r2v-nogo]] [[wan-vace-r2v-local-setup]] [[r2v-reference-to-video-models]] [[video-media-studio-skill]]
