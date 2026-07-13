---
name: hunyuancustom-r2v-setup
description: HunyuanCustom r2v(参照1枚+テキスト→任意シーン動画)をローカル導入・実証(2026-07-08)。当初no-go判定は前提が誤りで撤回、導入成功。gen_hunyuan_custom.py
metadata: 
  node_type: memory
  type: project
  originSessionId: 200959a5-a45c-4159-a506-8fc428432c92
---

三井彩香ペルソナの「参照人物1枚+テキストで任意シーン(例:浴室でシャワー)の動画」をローカルで実現。**HunyuanCustom(tencent)をKijai ComfyUI wrapper経由で導入・実証成功(2026-07-08)**。NSFW全裸ローカル可・検閲なし。

## ★★2026-07-13 ユーザー判断: 複雑NSFWシーンでは「クビ」(品質が実用外)
長谷川ペルソナで「裸で胸をマッサージを受ける」r2v動画を **736×1280・2h18m/本 × 2seed** 生成した結果、**両方とも破綻**: 手が出ない or 指が崩れる、キャンドルが顔/腹に物体化、後半で胸が黒く溶ける、下半身がレインボーノイズで融解。**高解像でも直らない=解像度でなくモデルが複雑な相互作用(手で胸を揉む)+多要素シーンを描けない**。ユーザー「hunyuanは酷いのでクビ」。
- **適性の切り分け**: HunyuanCustomが通るのは**単純シーン(シャワー/1人で立つ・座る、手や物との複雑な接触が無い)**まで。**手-身体の相互作用・オイル・小物多数・激しい体位はほぼ破綻**。シャワー成功例(2026-07-08)は偶々単純だっただけ。
- **★NSFW人物→動画の推奨は「r2v(identity注入)」でなく「i2v(綺麗なキーフレーム→動かす)」**: z-image/Qwen-Editで破綻の無い静止画キーフレームを作り(=coherent)、それを i2v(ローカル Wan2.2-spicy / クラウド wan-2.7-spicy / LTX i2v)で動かす。静止画が綺麗なら動画も破綻しにくい。Hunyuanは「静止topless参照から全部(identity+シーン+動き)を生成」で無理をしていた。
- 教訓(再): **高解像本番を無検証で長時間賭けない**。まず512×896(~35分)で破綻に気づくべきだった([[hunyuan-highres-and-gpu-loop-lessons]])。

## ★当初のno-go判定は撤回(前提が誤りだった)
最初「VACEで足りる」前提でHunyuanCustom導入をno-go判定したが、これは誤り。**VACE r2vは別人モーション動画をOpenPose骨格化して転写する方式で、モーション元動画が無いとシャワー等の任意シーンを作れない**。ユーザーが欲しかったのは「参照人物+テキストだけで任意シーン」=subject customization=まさにHunyuanCustomの設計目的。また「ディスク残63GB」も誤認で、実際は**モデル/HFキャッシュは全部Dドライブ(/data/kita, symlink先, 空き8.5TB)** にあり退避不要だった(`~/.cache/huggingface`→`/data/kita/.cache/huggingface`)。→ 方針転換して導入、成功。教訓: no-goの前提(既存で足りるか)を疑う。

## 導入構成(Kijai ComfyUI wrapper, headless)
- **ComfyUI**: `/data/kita/ComfyUI`(専用uv venv、★`--python-preference only-managed`でanaconda python回避。拾うとlibtinfo汚染+競合で起動しない)。custom_nodes: HunyuanVideoWrapper/KJNodes/VideoHelperSuite。torch三点cu121(torch/torchvision/**torchaudio**==2.5.1、torchaudio欠くと最新ComfyUIがModuleNotFoundError)+setuptools。
- **モデル(~22.5GB, `hunyuan_fetch.py`)**: fp8 transformer 13GB(Kijai/HunyuanVideo_comfy)、llava fp8 8.7GB+clip_l+clip vision(Comfy-Org/HunyuanVideo_repackaged /split_files/)、VAE 493MB。★identity核=**CLIP-Vision(llava_llama3_vision)** が参照顔を全フレームに注入(pose骨格でない)。
- **起動**: `comfyui_serve.sh --gpu N --no-sage`(sageattn未ビルド時)。`--listen 127.0.0.1`(NSFWローカル)。
- **UI→API変換**: `ui_to_api.py`が`/object_info`でwidget順序を吸収。★3つの罠: (1)`"COMBO"`文字列型もwidget扱い(新ComfyUIはcombo=文字列型) (2)リンク済みinputはwidgets_valuesに値が残ってもlink優先 (3)リンクfrom_nodeは文字列id(整数だと/prompt KeyError)。外すと全widget1つずれ。
- **APIテンプレ**: `reference/hunyuan_custom_api_template.json`。★Kijaiサンプルの`ImageConcatMulti`は参照と生成を左右連結するtesting用可視化→本番はバイパスしHyVideoDecode直→VHS。

## 実装(video-media-studioスキル)
- **主入口 `gen_hunyuan_custom.py`**: 薄いラッパー(spawn/接続→upload_image→patch_template(class_typeで探索)→POST /prompt→poll /history→/view でmp4回収)。引数はgen_wan_vaceに揃え。torch非依存(ComfyUI venv所有)。DEFAULT_NEGにtattoo系込み。--print-workflow/べき等スキップ有。
- **`compare_face_sim.py`**: ArcFace(insightface buffalo_l)のFace-Sim。★正面顔同士でしか公平でない。
- **登録**: models.py/gen_video.py FALLBACK_MODELSに`hunyuan-custom-720p`(task=r2v/pipeline=comfyui/defer_to_hunyuan)、gen_video.py `--task r2v`は早期defer(probe前、emit_hunyuan_defer)、DEFAULT_MODEL_FOR_TASK[r2v]。reference/models.mdにr2v節、SKILL.mdにタスク(5)+r2vフロー+Common Mistakes。

## 設定・実測
- Tencent推奨: 512x896 or 720x1280、frames 129(4k+1≈5s)、steps30、cfg7.5、flow_shift13.0、use_cfg_zero_star OFF。
- ★VRAM/速度(A6000 1枚実測): fp8+block_swap20+text_enc fp8で512x896/129f通る。**~70s/step→129f/30step≈36分**。2枚目は別ポート+--gpuで並列。
- ★fp8_scaledはLoRA非対応(Kijai明言)。モーションLoRAはbf16経路(未実装)。

## A/B結果(2026-07-08)
- 顔忠実度Face-Sim(正面同士): HunyuanCustom 0.180 vs VACE 0.184=**ほぼ互角**。ただしHunyuanはstd小(0.027<0.043)でフレーム間安定、目視で顔がシャープ。
- ★決定的差: **Hunyuanは任意シーン(シャワー等)をテキストだけで作れる、VACEはモーション元動画必須で不可**。→ 任意シーンr2vはHunyuanCustom、別人の動きを転写したいならVACE、と使い分け。
- 成果物: hunyuan_shower_final.mp4(本番129f)、hunyuan_frontal.mp4(A/B用)、~/media-out/persona-ayaka/

関連: [[wan-vace-r2v-local-setup]], [[r2v-reference-to-video-models]], [[session-resume-hf-watcher-r2v]], [[optimal-gen-models-table-and-new-model-eval]], [[person-image-6elements-confirm-before-fill]]
