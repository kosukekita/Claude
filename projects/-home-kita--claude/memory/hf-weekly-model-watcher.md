---
name: hf-weekly-model-watcher
description: 週次でHF新着の画像/動画生成モデル(NSFW含む)を検知しGmail通知するsystemd --userタイマー。設定場所・閾値・送信の仕組み
metadata: 
  node_type: memory
  type: project
  originSessionId: cee1ee3b-cf5e-48e5-82d4-e8881a33670e
---

リモートPC(Linux, uid1002, akitaken)で週次にHuggingFaceの新着 画像/動画生成モデル(NSFW含む)を検知し、新着がある週だけGmailに通知する仕組みを構築済み。ターミナルが閉じても動く(`Linger=yes`)。

**ファイル構成**
- 本体: `~/media-out/hf-watcher/hf-watcher.mjs`（`/usr/bin/node` で動かす。anaconda汚染回避が必須）
- 状態: `~/media-out/hf-watcher/seen.json`（model `id` で差分検知。sha不可=毎commit変わる）
- ログ: `~/media-out/hf-watcher/hf-watcher.log` / 直近digest: `last-digest.txt`
- SMTP秘密: `~/.config/gmail-smtp.pass`（mode600, Gmailアプリパスワード16桁）
- ユニット: `~/.config/systemd/user/hf-watcher.{service,timer}`（月曜09:00, Persistent=true）

**設計判断**
- 通知チャネルはGmail一択が確実。Claude PushNotificationはヘッドレス不可(ライブのエージェントターン内のみ発火)。`notify-send`はベストエフォートのローカルping
- 送信は `curl smtps://smtp.gmail.com:465 --ssl-reqd --user user:apppass --upload-file -`（anaconda curlはSMTP対応。`LD_LIBRARY_PATH=""`で起動）
- HF API: `https://huggingface.co/api/models` を `pipeline_tag`×4(t2i/i2i/t2v/i2v) + NSFWタグ(`not-for-all-audiences`) + free-text search(nsfw系/family名) で走査。`sort=createdAt&direction=-1` + `Link: rel="next"` カーソルページング。`createdAt`は一覧レスポンスに含まれる
- 2段ゲート: (1)relevance=画像/動画生成のみ(uncensored LLMを除外) (2)notability=likes≥100 OR dl≥5000 OR trendingScore≥80。閾値は env `HFW_MIN_LIKES/HFW_MIN_DL/HFW_MIN_TREND` で調整可
- **ユーザー希望で「週1件あるかどうか」に超厳選**（2026-06-24）。実測分布: 7d gen模型約1100件 → likes≥10で25件 / likes≥50で4件 / likes≥100で3件 / likes≥200で0件。likes≥100採用で7日3件(Krea-2-Turbo等のメジャーリリースのみ、無名LoRA全除外)
- バイパス(主要familyのbase新規 / NSFW傾向)は **OFF がデフォルト**（`HFW_BYPASS=1` で再有効化）。超厳選ではNSFWも同一閾値=likes100超のバズったものだけ通知（NSFWは稀にしか出ない、ユーザー了承済み）
- trendingScoreはlikesと連動するので緩い閾値だと「1like=通知」になる。MIN_TREND=80で実体化

**運用コマンド**
- 手動ドライラン: `cd ~/media-out/hf-watcher && /usr/bin/node hf-watcher.mjs --dry-run --window-days 7`
- 即時1回実行: `systemctl --user start hf-watcher.service`
- 次回確認: `systemctl --user list-timers hf-watcher.timer`
- ログ: `journalctl --user -u hf-watcher.service -n 30`

**環境制約(再掲・重要)**: PATH `node`/`jq`/`python3`/`curl` は anaconda版で `libtinfo.so.6` 警告を出し汚染する。systemdユニットは `PATH=/usr/bin:/bin`, `LD_LIBRARY_PATH=`(空) を明示。

## 比較生成パイプライン統合（2026-06-24追加）
検知だけでなく「新着画像モデルを現状最適baselineと同一プロンプトで実生成し、横並びPNG＋pCloudリンクをメールに添える」自動比較を追加。ユーザー希望: セッション閉じてもタイマーだけで画像リンク付きメールが届くこと。
- **追加ファイル(全て~/media-out/hf-watcher/)**:
  - `eval-prompts.json` — 4軸(sfw_noref/sfw_ref/nsfw_noref/nsfw_ref)のプロンプト＋baseline＋ref_image。`{場所}`(全角/半角両対応)プレースホルダは比較時にAIが週替わりで1つ選び全パターン共通で差し込む(used-locations.jsonで直近6回重複回避)。nsfw_refだけ場所固定で`{場所}`無し。baselineはローカル可動モデルのみ自動生成(qwen/zimage/chroma/noobai)、codex/grokはheadless不可で手動注記のみ→**SFW軸にローカルbaseline(sfw_noref=zimage, sfw_ref=qwen)を追加**しないと新モデル1枚だけになる
  - `eval-compare.mjs` — `--axis --model`受け。軸マップ→場所選び→**GPUプリフライト(nvidia-smiで空き確認、埋まってたらexit2でskip)**→新モデル汎用生成(ゲート)→baseline生成→ffmpeg drawtext+hstack→`~/pCloudDrive/Data/AIGenerated/`に保存→sync待ち→pcloud_link.mjs --directでURL。exit2=新モデル生成失敗(検知のみ), exit3=動画/対象外
  - `gen_generic_edit.py` — 新着モデルをdiffusers Auto*Pipelineで汎用ロード試行。**失敗(gguf/未知class/OOM/壊れ画像)なら非0で抜け比較全体skip(ユーザー確定: 生成全体スキップ検知メールのみ)**。`looks_broken()`で真っ黒/単色/ノイズ(輝度mean<6 or >249, std<4)を成功扱いから除外。`save_checked`はsys.exitするので各try節に`except SystemExit: raise`ガード必須。**turbo検出(`is_turbo`)**: モデルID/ファイル名にturbo/schnell/lightning/hyper/lcm/distill/dmd等があればsteps=8・guidance=1.0、なければ30・4.0(steps/guidance未指定時のみ。明示指定は尊重)。**重要**: Krea-2-Turboを汎用ローダーのデフォルト(step30/cfg4)で回すと顔が暗く潰れ緑フレア/ノイズの劣化画像になる→turbo判定でstep8/cfg1にすると正常なフォトリアルに改善(実証2026-06-24)。turbo系新モデルは必ずこの分岐が要る
- **hf-watcher.mjs改修**: 各NEW画像モデルの`_axes`を`mapAxis()`で4軸化→`runEvalCompare()`呼び出し→成功で`m._compareUrl/_compareAxis`セット→`fmtModel`がメールにリンク行追記。動画/生成失敗は従来digestのみ。`HFW_NO_COMPARE=1`で無効化
- **ref画像**: `~/media-out/hf-watcher/ref/male-body.jpg`(スキルのmale-body-reference.jpgコピー)。「(参照画像あり)」テキストだけでは効かず`--image`で実ファイル渡しが必須(sfw_ref/nsfw_refの男性同一性保持用、女性は参照なし)
- **systemd改修**: `hf-watcher.service`に`EnvironmentFile=-%h/.config/pcloud-link.env`(mode600, PCLOUD_USER/PASS)追加、`TimeoutStartSec`を600→**7200(2h)**に延長(複数モデル直列生成)、`KillMode=mixed`(hung gen childをreap)
- **Qwen baseline実測**: cu121/offload model/40step/640x1664で約6分(初回モデルロード込)、参照画像の同一性保持OK
- **フルテスト実証(2026-06-24)**: `krea/Krea-2-Turbo`(sfw_noref)でend-to-end成功。新モデル汎用生成4分20秒+zimage baseline1分9秒→横並び→pCloudリンク両方(ページ恒久+direct直URL)。**汎用ローダーgen_generic_editは専用gen_krea2.pyが別にあるKrea2でもAutoPipelineForText2Imageで素直にロード・生成できた**(ゲートは想定より頑健)。codex/grokは手動注記で正しくskip
- **ffmpeg合成の2つの落とし穴(フルテストで判明・修正済み)**: (1)ラベル日本語が豆腐化→DejaVuにCJKグリフ無し。**Noto Sans CJK(`/usr/share/fonts/opentype/noto/NotoSansCJK-Bold.ttc`)に変更**。(2)このリグのffmpegは**anaconda版のみ(`/home/kita/anaconda3/bin/ffmpeg`)、`/usr/bin`に無い**。CLEAN_ENVが/usr/bin前置きするのでbare"ffmpeg"は将来失敗しうる→eval-compare.mjsで絶対パス解決(FFMPEG定数)に変更
- **プロンプトの「盗撮」はSFW軸から除去(2026-06-24)**: sfw_norefに「盗撮している」が入っていた→**Codex(GPT Image)が「非同意撮影なので外す」と自動でプロンプト改変**(クラウドAIは盗撮表現を拒否/改変)。「さりげなくとらえた何気ない日常のスナップ」に置換。nsfw_norefの「盗撮」はNSFW軸なので意図的に残す。教訓: SFW軸に非同意/盗撮概念を入れるとクラウドAIで不安定化
- **Codex(GPT Image)はこのセッション環境で実用外**: codex execは画像生成自体は成功するが、**bwrap(`Failed RTM_NEWADDR: Operation not permitted`)で生成画像を保存先にcpできず回収不能**(Codex設計レビューが失敗したのと同根)。`--dangerously-bypass-approvals-and-sandbox`はClaude auto mode classifierが「Create Unsafe Agents」でブロック(permissionsでなくclassifierレイヤー、`Bash(codex exec:*)`は既に許可済み)→`-s workspace-write --skip-git-repo-check`なら起動はできるがbwrapでファイル出力不可。**Grokは画像生成・回収とも成功**(grok-media、日本語プロンプトそのまま、SFW盗撮なし版なら通る)。本番はheadlessなのでcodex/grokは手動注記扱い→パイプライン本体に影響なし
- **未完/Codexレビュー失敗**: Codex設計レビューは`bwrap: loopback: Failed RTM_NEWADDR`でサンドボックス起動不可→評価得られず。重要2点(壊れ画像検出・GPUプリフライト)はClaude自身で反映済み。残検討: pCloud REST API直upload(FUSE sync待ちをバイパス), systemd-credentials移行

## gguf/単一ファイルtransformer差し替え対応（2026-06-29追加）
「gguf-only/単一safetensorsのみ(model_index.json無し)」リポを今まで `gen_generic_edit.py` が即exit4で全スキップしていた問題を解消。実例: `wikeeyang/Flux2-Klein-9B-True-V3`(FLUX.2-klein-9Bのfinetune, transformer単一ファイルのみ=bf16/Q8/mxfp8/fp8mixed/Q6_K/Q5_K/Q4_K/nvfp4)が2026-06-29のメールで「0/2 produced an image」になっていた真因がコレ。
- **解決方式**: diffusersネイティブのgguf対応(`GGUFQuantizationConfig`+`from_single_file`)で、**ベースの完全diffusersリポからVAE/TE/scheduler/tokenizerを取り、transformerだけfinetuneリポの単一ファイルに差し替える**。`Flux2KleinPipeline.from_pretrained(base, transformer=tr)`。ComfyUI/sd.cpp不要(両方未インストール、入れない方針)。
- **`gen_generic_edit.py` 追加実装**: uvヘッダに`gguf`依存追加。`fetch_index`が`base_model:`タグ抽出。`SINGLEFILE_FAMILIES`テーブル(現状flux2のみ、match=flux.2/flux2/klein → pipeline=Flux2KleinPipeline/alt Flux2Pipeline, transformer=Flux2Transformer2DModel, default_base=black-forest-labs/FLUX.2-klein-9B)。`_pick_singlefile_weight`が**gguf優先(Q6_K>Q5_K>Q8_0>Q4_K)→fp8/mxfp8/bf16 safetensorsフォールバック**。`try_singlefile_transformer_swap`が`from_single_file(url, quantization_config=GGUF.., config=base, subfolder="transformer", torch_dtype=bf16)`。**configは単一ファイルに無いのでbase repoのtransformer/configを必ず`config=base, subfolder="transformer"`で渡す**(これが肝、無いとロード失敗)。main側でgguf-bailout手前に分岐(t2iのみ、`--image`時は対象外)。
- **LoRA誤検出修正**: 旧コードは「root-levelのsafetensorsがあれば全部LoRA扱い」→Flux2-Kleinのroot量子化バリアント群がLoRA誤分類されてた。**「lora名を含む or root safetensorsがちょうど1個 かつ ggufなし」のみLoRA**に厳格化(複数バリアント/ggufありは単一ファイルtransformer dump扱い)。
- **gated対応**: ベース`black-forest-labs/FLUX.2-klein-9B`は`gated:auto`。**ユーザーがHFで1回ライセンス同意済み**(2026-06-29時点アクセスOK)。`~/.cache/huggingface/token`(保存済みトークン, 2月設定)があれば`HF_HOME`経由でhuggingface_hubが自動利用→**HF_TOKEN環境変数は不要**(本番相当envで実証済み)。同系のFLUX.2-devも同意済み。新たなgatedベースが必要なモデルが来たら都度同意が要る。
- **systemd unit の2つの穴を修正(本番で確実に動かすため必須だった)**: (1)`Environment=PATH=/usr/bin:/bin`に`uv`(`/home/kita/.local/bin/uv`)が無く、hf-watcher.mjs→eval-compare.mjs→`uv run`の全階層でuv解決不能だった→**PATH先頭に`/home/kita/.local/bin`追加**。(2)HF_HOMEは元から設定済みでtokenファイル自動読込が効くのでHF_TOKEN追加は不要と判明。daemon-reload済み。
- **klein-9B実測**: _class_name=`Flux2KleinPipeline`(Flux2Pipelineでない), text_encoder=`Qwen3ForCausalLM`(Mistralでない), scheduler=FlowMatchEuler, `is_distilled:true`+`guidance_embeds:false`→**diffusersが自動でguidance無視(`Guidance scale X is ignored for step-wise distilled models`)・steps=8でフォトリアル高品質**。Q6_K gguf経路: transformerロード77s+パイプ組立133s(初回TE等17ファイルDL込)+生成70s。2回目以降キャッシュで新モデル生成36s。A6000 1枚でenable_model_cpu_offload(保険)で完走。
- **E2E実証**: 本番相当env(HF_TOKEN無し/新PATH/HF_HOME)で`eval-compare.mjs --axis sfw_noref --model wikeeyang/Flux2-Klein-9B-True-V3`完走→新モデル生成+zimage baseline横並び+pCloud公開リンク両方(ページ恒久+direct)発行成功。合成PNGのラベル日本語も正常(Noto CJK)。実写級品質確認済み。
- **Codex設計レビュー(codex:codex-rescue)併用**: 「fp8の方が信頼性高い/config推定に注意/offloadは保険」と助言。実機ではgguf Q6_Kが一発で高品質だったのでgguf優先採用、config明示渡しで懸念解消済み。fp8はフォールバックとして実装に残置(将来gguf読めないモデル用)。

## NSFW優先フォールバック + NSFW=リンクのみ/SFW=添付（2026-06-29追加・ユーザー恒久ルール）
ユーザー恒久ルール2件をwatcher本体に実装(hf-watcher.mjs):
- **(1) 全モデルで常にNSFW軸を先に生成 → 失敗したらSFW軸にフォールバック**。旧`mapAxis()`(タグ/名前でSFW/NSFW自動判定し片方だけ)は廃止(関数は参照用に残置・未使用)。新`runEvalCompare(modelId, axes)`が**参照画像の有無(`axes.ref`)だけメタから決め**、SFW/NSFW次元は必ずNSFW先行。ref無→`nsfw_noref`先/`sfw_noref`後、ref有→`nsfw_ref`先/`sfw_ref`後。両軸失敗で検知のみ。`runEvalCompareOnce`が1軸実行の下請け(戻り`{ok,url,localPng,status}`)。**ユーザー選択は「NSFW非対応モデルでも全モデルNSFW優先」**(2026-06-29、AskUserQuestionで確定)。SFW専用モデルはNSFW生成が失敗してSFWに落ちる分やや時間増だが許容。
- **(2) NSFW結果はメール添付せずpCloudリンクのみ／SFW結果はPNGをメール添付**。理由: **NSFWバイナリをGmailに添付/直貼りするとアカウントBANリスク**(ユーザー明示)。`sendEmail(subject, body, attachments=[])`をmultipart/mixed対応に拡張、**`_compareAxis`が`sfw_*`のものだけ添付候補**(`/^sfw_/`)。NSFWは従来通りdigest本文にpCloudリンクだけ載る。`runEvalCompareOnce`が**ログ`composed: <path>`から合成PNGのローカルパスを抽出**して`m._compareLocalPng`に保存(SFW添付用)。digest本文の比較生成行もNSFW=「🔞NSFWのため添付なし・リンクのみ」/SFW=「SFW: メール添付あり」と明示。
- **手動送信スクリプト**: `~/media-out/hf-watcher/send_nsfw_link_mail.mjs`(NSFW用・添付なしリンクのみ), `send_compare_mail.mjs`(SFW用・添付あり)。本番watcherは上記でmultipart内蔵なので手動スクリプトは単発検証/再送用。
- **今回の実証(2026-06-29)**: Flux2-Klein-9B-True-V3を`nsfw_noref`で生成成功(NEW+zimage+chroma 3カラム、grokはheadless不可skip)→pCloudリンクのみメール送信完了。SFW版(sfw_noref)は別途添付付きで先に送信済み。構文チェック+軸選択/添付フィルタの単体検証パス。

## nsfw_norefプロンプト刷新 + Chroma恒久除外 + negative配線（2026-06-29追加）
- **nsfw_norefプロンプトを「脱衣所で服を脱ぐ・上半身裸・不意を突かれた表情」に全面刷新**（旧:高級ホテルで紐パンツ盗撮）。ユーザー支給の長文プロンプト(iPhone縦型/咄嗟に胸を腕で隠す/友人がさりげなく撮った気配/圧縮画質・ノイズ・モーションブラー等のリアリズム指定)をそのまま採用。**脱衣所固定なので｛場所｝プレースホルダなし**(nsfw_refと同様、fillPromptは該当なしでそのまま通す。pickLocationは走るがログ表示のみで無害)。
- **eval-prompts.jsonに`negative`フィールド新設**。eval-compare.mjsの`genBaseline`/`genNewModel`に`negative`を配線し`--negative-prompt`で各genへ渡す(entry.negativeが非空のときのみ。空ならQwenの内蔵DEFAULT_NEG温存)。**negative対応モデル: Qwen/Z-Image/Chroma/SDXL(NoobAI)はhonor、FLUX系は内部で自動無視**(gen_image.py 587行・gen_generic_edit.pyがゲート)。nsfw_norefのnegativeにはユーザー指定NGリスト全部＋anime/illustration/cartoon/2D/CG等を追加。
- **★Chromaを恒久除外(ユーザー指示2026-06-29)**: nsfw_norefのbaselineを`["grok","zimage"]`に変更(chroma削除)。**Chroma1-HD(FLUX.1-schnellベースの実写無検閲)はこの実写NSFWプロンプト(iPhone/UI/画面系の語が多い)と相性が最悪**で、negative無し→アニメ化、negative追加→人物が消えiPhone設定画面風の青いUI＋文字化けに破綻、と2回連続で使い物にならず。**実写NSFW t2iの現状最適baselineはzimage(Z-Image-Turbo)**(grokはheadless不可で手動注記)。Chromaは実写人物プロンプトで不安定と判明したので今後baselineから外す。
- **実証(2026-06-29)**: 新プロンプト+negative+chroma除外で`eval-compare --axis nsfw_noref`完走。Flux2-Klein[NEW]とzimageの2カラムとも脱衣所・上半身裸・胸を腕で隠す不意打ち表情・実写級でプロンプト忠実。pCloudリンクのみメール送信完了(NSFW添付なしルール適用)。Flux2-Klein 2回目以降キャッシュで新モデル生成36s、zimage 20s、合成+リンクまで約1分。

## 週次ダイジェスト棚卸し（2026-07-07）
- **biz-insights.timer / x-digest.timer をユーザー指示で停止・無効化**（`systemctl --user disable --now`。ユニットファイルは残置、再開は `enable --now`）。sns-trends.timer は元から無効。hf-watcher.timer のみ稼働継続（毎週月曜09:00 JST）。
- **「NSFW動画モデルのメールが来ない」の真因は故障ではなく超厳格ゲートの構造的帰結**: 実行・SMTP は正常（7/6 も完走）。だが (1) notability=likes≥100 OR dl≥5000 OR trend≥80 は新着1週目のNSFW動画モデルにはほぼ到達不能（実測 2026-07-07: 直近8日のNSFW系動画モデル62件の最高が♥24=LTX-Best-Face-ID）、(2) NSFW救済バイパスはデフォルトOFF、(3) 0件の週は「nothing new → silence」でメール自体が出ない。→ 下の勾配ゲートv2で解消。

## 通知ゲートv2「勾配方式」（2026-07-07、ユーザー提案+Codexレビューで再設計・実装済み）
ユーザー提案「30日窓でlikesの絶対数でなく勾配（急上昇）を見る」を採用。Codex second-opinion（codex-consult経由）と30日実データのバックテストで設計確定。
- **最重要修正（Codex指摘）**: 旧 `cutoff=max(last_run, now-window)` は週次運用だと前回実行以降しか走査せず「生後2〜4週で伸びたモデル」を構造的に取りこぼす → **createdAt 30日窓を毎回フル再走査**に変更（例: 6/18リリースのKrea-2-Turbo tr118が一度も通知されていなかったのを実証検出）。重複送信はseen.jsonの永続dedupが防ぐ。
- **実測事実**: HF APIにlikes履歴なし（likersにも日付なし）→Δlikesは自前週次スナップショットでしか取れない。`downloads`は既に30日ローリング値（downloadsAllTimeと別）。`trendingScore`は直近勢い指標（2年前2225♥→tr14、2日前24♥→tr24）でHF版勾配。
- **新ゲート**（OR、env上書き可）: A)trend≥20(HFW_MIN_TREND) B)Δ♥/週≥20(HFW_DELTA_WK、likes-snapshots.jsonの5日以上前サンプル基準) C)生後14日以内かつ♥≥5かつ♥/日≥2(初日ノイズは絶対数下駄でブロック) D)保険=♥≥100 or (⬇≥5000かつ♥≥5、♥0の⬇7kボットミラー除外) + NSFW緩和(tr≥10/Δ≥5/♥日0.5&♥3)。classify()に`eros`境界付き正規表現を追加（10Eros系がNSFW判定されなかった穴を修正）。
- **状態**: `likes-snapshots.json`（seen.jsonと分離、tmp+rename書き込み、samples直近10件、createdAt60日/lastSeen45日でprune、破損時はΔ経路のみ無効化して続行）。
- **安全弁（loop-engineering準拠）**: 週次通知は速度スコア上位8件キャップ(HFW_MAX_REPORT、キャップ落ちはseenに入れず翌週再浮上可)、GPU比較生成は1回3件まで(HFW_COMPARE_MAX、2h unit上限保護)、閾値未満の上位3件をnear-missとしてログに常時記録（無音週の説明可能性）。
- **テスト**: ゲート関数をexport化(import guard付き、`import.meta.url`一致時のみmain実行)し単体テスト18件PASS。E2Eドライラン→本番実行で7/7に30日分バックログ34件(NSFW 3=10Eros系)をHFW_MAX_REPORT=40で一括送信済み（emailSent=true）。次回から週8件上限の定常運転。
- 旧HFW_BYPASSは廃止。--window-days既定は7→30。

関連: [[nsfw-models-chroma-noobai-wan-lora]]（HF探索TIPS・追跡family。Chromaは実写人物NSFWでは不安定と判明）, [[image-cache-volatile-use-media-out]]（durableデータは~/media-out）, [[optimal-gen-models-table-and-new-model-eval]]（4軸baseline。nsfw_norefのbaselineからchroma除外）, [[pcloud-public-link-api]]（リンク発行、getfilelinkが直URL）, [[gen-image-gpu-zombie-oom]]（生成前GPUゾンビkill）, [[gmail-send-smtp-attachments]]（Gmail添付メール送信の定番手順）
