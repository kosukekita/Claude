---
name: nsfw-real-to-anime-v2v-qwen
description: NSFWリアル動画→アニメ動画は gen_v2v_qwen.py(Qwen-Image-Edit+アニメLoRA)が確定の本命。SDXL+IP-Adapterは別人化で不可
metadata: 
  node_type: memory
  type: feedback
  originSessionId: 07bfcea1-7bcc-4022-bd20-58360e43dbcc
---

★ユーザー恒久ルール(2026-06-30 実機実証＆確定): **NSFWのリアル人物動画→アニメ動画は、video-media-studio の `gen_v2v_qwen.py`(Qwen-Image-Edit-2511 + アニメLoRA)でやる**。フレームごとにアニメ化し同一人物を保ったまま1本に結合する用途の第一選択。

**なぜ Qwen 経路なのか(核心)**: Qwen-Image-Edit は「入力画像そのものを*編集*する」モデルなので、各フレームが元の実写フレームを土台にし、顔・髪・体型が入力から直接受け継がれ**同一人物が保たれる**。対して SDXL+IP-Adapter(`gen_v2v_style.py`)は「新規生成＋顔を薄くヒント」なので毎フレーム別の顔を描き**別人化**する(2026-06-30: Pony+IP-Adapterで前髪が消え面長の量産アニメ顔になり失敗→Qwenで解決)。

**確定構成**: `--repo Qwen/Qwen-Image-Edit-2511` + `--lora prithivMLmods/Qwen-Image-Edit-2511-Anime`(トリガー"Transform into anime."、4-8step lightning、cfg≈1、「ポーズ/視点保持」設計＝フレーム単位最適)。アニメLoRAは**必須**(無いと入力の表情/ポーズを勝手に作り変える)。NSFW表現が要れば `ScottzillaSystems/qwen-image-edit-plus-nsfw-lora` を2枚目にスタック。逆(アニメ→実写)はLoRAを `Hyperccino/Qwen-Edit-2511-Anime-to-Photoreal-v1.1` 等＋NSFW LoRAに差し替え(準実写まで・NSFWはローカル一択、編集APIは全NSFW拒否)。

**実証パラメータ**: `--steps 8 --guidance 1.0 --seed <fixed> --max-side 1280 --offload model`。★`--offload none`は20B+LoRAが1280pxで48GB OOM→offload必須(1枚~30-40秒)。fps=24が画質/滑らかさ/時間のバランス良(60fps全部は非現実的)。長尺は両GPUで前半後半分割並列(`--work-dir`共有,`--start/--end`)→全フレーム手動concat。**後処理ブレンド(minterpolate=blend)はしない**=輪郭が二重ボケで画質低下(raw>smoothed、ユーザー確定)。生成フレーム無加工結合(raw)が最高画質。残るちらつきはフレーム別編集の宿命でfps上げて緩和。元動画の画面録画UI等はアニメ化されて写り込むので必要ならトリム。

完全ローカルで外部送信しない(NSFW)。納品先は指定パス(例 P:\Data\NSFW\unreal\generated)。SKILL.md §「★NSFWリアル動画→アニメ動画」と reference/models.md §5a が正本。関連: [[reference-image-gen-codex-vs-qwen]](参照NSFW=Qwen), [[optimal-gen-models-table-and-new-model-eval]]。
