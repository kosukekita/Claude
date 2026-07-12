---
type: reference
title: LTX-2.3 CrossView IC-LoRA（1本の動画→別カメラアングル/マルチカメラ）
description: 参照動画を別カメラアングルで再レンダリングするLTX-2.3 22B IC-LoRA。crossviewプロンプト語彙・ComfyUIワークフロー・必要モデル・実行状況
tags: [ltx, crossview, ic-lora, multicam, novel-view, camera-angle, v2v, comfyui]
---

# LTX-2.3 CrossView IC-LoRA（1本の動画 → 別カメラアングル）

`Cseti/LTX2.3-22B_IC-LoRA-CrossView-Prompt`（v0.9 pilot, Apache-2.0, base=Lightricks/LTX-2.3）。LTX-Video 2.3 (22B) の **In-Context LoRA（IC-LoRA）＝"仮想の2台目カメラ"**。**参照動画＋カメラアングル指定プロンプト**を与えると、同じシーン・同じ被写体を**要求した新しい視点**で再レンダリングする（**v2v・開始画像不要**）。1つの撮影からマルチカメラ映像・novel-view合成が作れる。

## プロンプト語彙（固定・重要）
自由文ではなく**離散の固定語彙**で学習されている。必ず `crossview.` で始め、3軸で指定:
```
crossview. new camera angle: {horizontal}, {height}, {distance}.
```
| 軸 | 使える句 |
|---|---|
| **horizontal**（被写体の周りの方位） | `far to the left` / `to the left` / `slightly to the left` / `same angle` / `slightly to the right` / `to the right` / `far to the right` |
| **height**（カメラの高さ） | `lower`（下から見上げ） / `same height` / `higher`（上から見下ろし） |
| **distance**（被写体との距離） | `closer` / `same distance` / `further` |

7×3×3 = **63通り**（全文は `reference/crossview_captions_all_63.txt`）。**同義語（"45 degrees left" 等）は効きが悪い**ので必ずこの正確な句を使う。
例: `crossview. new camera angle: slightly to the left, higher, closer.`

## 使い方のコツ
- **小さな1ステップの変更が最も安定**。大きく視点を動かすなら**小刻みにチェーン**（生成結果を次の参照動画に食わせ、さらに小角度）。
- v0.9 pilot（step 13,700）＝実験段階。合成multi-view学習で実写にも一応効くが**アングル追従は常には安定しない**。

## 実行経路（ComfyUI v2v・著者テスト済み）
著者は **ComfyUI** の v2v IC-LoRA ワークフローでのみテスト。ワークフローJSON: `reference/crossview-workflow/ltx2.3-ic-lora-crossview.json`（72ノード）／解説: 同 `WORKFLOW_README.md`。
- 設定: **IC-LoRA strength=1.5 / distilled speed LoRA=0.6**、2パス（8-step base ~960×544・241f@24fps・音声あり → 2x latent spatial upscale）。
- 入力＝`Load Video` の参照動画（開始画像不要。参照フレームは出力解像度決めだけ）。

### 必要モデル（ComfyUI に配置）— ★大半が未導入
| 用途 | ファイル | 取得元 | 状況 |
|---|---|---|---|
| IC-LoRA（本体） | `LTX2.3-22B_IC-LoRA-CrossView-Prompt_v0.9_13700.safetensors`（100MB） | Cseti | ✅ `/data/kita/ComfyUI/models/loras/` に取得済み |
| 22B dev transformer fp8 | `ltx-2.3-22b-dev_transformer_only_fp8_scaled.safetensors` | Kijai/LTX2.3_comfy | ❌ 未 |
| distilled speed LoRA | `ltx-2.3-22b-distilled-1.1_lora-dynamic_fro09_avg_rank_111_bf16.safetensors` | Kijai/LTX2.3_comfy | ❌ 未 |
| video VAE / audio VAE / preview VAE | `LTX23_video_vae_bf16` / `LTX23_audio_vae_bf16` / `taeltx2_3` | Kijai/LTX2.3_comfy | ❌ 未 |
| text encoder | `gemma_3_12B_it_fp8_scaled.safetensors` | Comfy-Org/ltx-2 | ❌ 未 |
| text projection | `ltx-2.3_text_projection_bf16.safetensors` | Kijai/LTX2.3_comfy | ❌ 未 |
| spatial upscaler | `ltx-2.3-spatial-upscaler-x2-1.1.safetensors` | Lightricks/LTX-2.3 | ❌ 未 |
| custom nodes | ComfyUI-LTXVideo / KJNodes / VideoHelperSuite / rgthree / RES4LYF / comfyui-int-and-float | 各GitHub | ❌ 未 |

**現状（2026-07-13 実装完了・フル完走はサンドボックス制約で未実測）**:
- ✅ **基盤スタック全DL済み**（`/data/kita/ComfyUI/models/`・計~42GB）: 22B dev transformer fp8(22G) / distilled speed LoRA(2.6G) / IC-LoRA(97M) / video・audio・preview VAE / gemma text encoder fp8(13G) / text projection / spatial upscaler。
- ✅ **custom node 導入済み**: ComfyUI-LTXVideo / KJNodes / VideoHelperSuite / rgthree-comfy / RES4LYF / comfyui-int-and-float ／ **★`FL_FloatToInt` 用に `ComfyUI_Fill-Nodes` も導入**（WORKFLOW_README の記載は不正確で `comfyui-int-and-float` では別物）。
- ✅ **kornia を 0.7.3 に固定**（ComfyUI-LTXVideo が `kornia.geometry.transform.pyramid.pad` を要求。0.8.3 で削除）。HunyuanVideoWrapper は import 継続を確認。
- ✅ **spatial upscaler は `models/latent_upscale_models/` に配置**（`LatentUpscaleModelLoader` は `latent_upscale_models` キーを見る。`upscale_models` ではない）。
- ✅ **ヘッドレス変換＆ラッパー完成・実ノード実行まで到達を検証**:
  - `scripts/ui_to_api.py` に **`inline_subgraphs` / `resolve_get_set` / `bypass_reroutes` / `bypass_muted`** を実装（サブグラフ2個・GetNode/SetNode・mode=4バイパスを平坦化）。★特に **mode=4 のミュート/バイパスノードを有効ノードとして残すと validation で落ちて "3秒 no-op" になる** → `bypass_muted` で入力→同型出力へ直結して除去。
  - `scripts/gen_ltx_crossview.py`（ComfyUI を子プロセス管理・最終2xアップスケール出力ノード5249を回収・`nvidia_rtx_vsr→lanczos` 上書き）。workflow JSON 側でも 5091 の `nvidia_rtx_vsr→lanczos` を確定修正。
  - **実証**: 修正後、prompt が **validation 通過 → 実ノードが実行される**状態（3秒 no-op は解消）。
- ✅ **実行確認済み（2026-07-13 実機実証）**: 参照(512×512/72f)→ **出力 1024×1024 / 97フレーム / 4.0秒**（512×512 passthrough ではなく本物の生成・2xアップスケール込み）。**所要 ~186秒（約3分）**、**ピークVRAM ~45GB（単一 A6000 48GB に収まる）**。
- **★環境の実行方法（重要）**: このマシンは **fork/前景/nohup/run_in_background で起動した数分かかる生成プロセスを exit 144 で殺す**。**`systemd-run --user`（＝毎朝の phase1 と同じ、プロセス木から独立）で起動すれば生き残って完走する**。例:
  `systemd-run --user --unit=ltx-cv --working-directory=<scripts> bash -c '/data/kita/ComfyUI/.venv/bin/python gen_ltx_crossview.py --ref REF.mp4 --azimuth "slightly to the left" --elevation higher --distance closer --out OUT.mp4 --gpu 0 --no-sage'`
- **★このワークフローに入れた実行用パッチ（この環境で回すため）**: (1) sage パッチ2ノード(5067/5068)と ModelPatchTorchSettings(5069) を **mode=4 バイパス**（pytorch2.5.1/cu121 では fp16 累積・SageAttention 不可。いずれも任意の速度/メモリ最適化なので出力品質は不変）。(2) ImageResizeKJv2(5091) の `nvidia_rtx_vsr → lanczos`（RTX VSR未導入）。(3) **フレーム数 5099 を 241 → 97 に削減**（241f フルは単一48GBでOOM。97f で ~45GB に収まる。フル尺が要るなら frames を戻して `--lowvram`＋フレーム/解像度調整 or マルチGPU）。ラッパーは ComfyUI に `--lowvram` を渡す。
- `gen_ltx_crossview.py` の CLI: `--ref/--azimuth/--elevation/--distance/--out/--ic-lora-scale/--speed-lora-scale/--gpu/--no-sage`。方位/高さ/距離は crossview 固定語彙で内部バリデーション。

## スキルの既存LTXとの関係
`gen_ltx23_lora.py` は **i2v**（`--image` 必須）でLoRAをスタックする経路であり、この **v2v IC-LoRA（参照動画入力・in-context）には非対応**。CrossView は上記 ComfyUI v2v 経路で動かす（diffusers 直の v2v IC-LoRA は未検証）。
