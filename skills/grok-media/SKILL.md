---
name: grok-media
description: >
  xAI 公式 Grok Build CLI（X Premium+ / SuperGrok の OAuth で認証）に委譲して、
  動画生成（テキスト→動画・画像→動画）・画像生成・生成済みメディアのレビュー・
  生成用プロンプトの最適化を行うスキル。codex-consult と同型の外部CLI委譲。
  Use when the user wants to generate a video or image with Grok, animate a still
  image, review/critique generated media, or turn a vague idea into a strong
  generation prompt.
  Trigger phrases: Grokで動画, Grok動画生成, 動画を作って（Grok）, Grokで画像,
  画像生成（Grok）, この画像を動かして, Grok Imagine, grok-imagine,
  生成した動画をレビュー, 動画プロンプトを最適化, generate video with Grok,
  generate image with Grok, animate this image, grok imagine.
  Do NOT trigger for: Claude/他ツール自身の画像生成、コードレビュー（code-reviewer 等）、
  arXiv/論文検索（alphaxiv/research-toolkit）。本スキルは Grok Build CLI による
  メディア生成・そのレビュー・プロンプト整形に限る。
allowed-tools: Bash, Read, Glob, SendUserFile, AskUserQuestion
---

# Grok Media

xAI 公式 **Grok Build CLI** に委譲して、Grok Imagine の動画・画像生成と、その
レビュー・プロンプト最適化を行う。codex-consult と同じ「外部 AI CLI 委譲」型。

## 前提・土台（重要）

- **CLI 実体**: `~/.grok/bin/grok.exe`（Windows）。PATH 未解決の環境を想定し、
  スキルは原則 **フルパス** `"$HOME/.grok/bin/grok.exe"` で叩く。
- **認証**: X Premium+ / SuperGrok の **OAuth**。未ログインだと生成は失敗する。
  確認: `grok models` が `You are not authenticated.` を返したら未ログイン。
  対処: ユーザーに `! ~/.grok/bin/grok.exe login`（ブラウザOAuth）を依頼する。
  ＝ **このログインだけは Claude が代行できない**（ブラウザ操作のため）。
- **生成の仕組み**: Grok Build はエージェント。`generate_video` / `generate_image`
  を**内蔵ツール**として持ち、**自然言語の指示で発火**する。専用サブコマンドは無い。
- **ヘッドレス実行**: `grok -p "<指示>"` で単発実行し stdout に結果を出す。
- **出力先**: 既定 `<cwd>/.grok/generated-media/`。明示パス指定も可。
- **課金**: X Premium+/SuperGrok のサブスク枠内で動く（API キー従量課金ではない）。

## いつ使うか

| やりたいこと | タイプ |
|---|---|
| テキストから動画を作る | video（text-to-video）|
| 静止画を動かす | video（image-to-video）|
| テキストから画像を作る | image |
| 生成済みの動画/画像を評価・改善案がほしい | review |
| 曖昧な要望を生成向けプロンプトに整える | optimize |

## Instructions

### Step 0: ログイン確認（毎回最初に）

```bash
"$HOME/.grok/bin/grok.exe" models 2>&1 | head -5
```

`You are not authenticated.` が出たら、ここで止めてユーザーに次を依頼する:

> ブラウザで X Premium+ ログインが必要です。プロンプト欄で実行してください:
> `! ~/.grok/bin/grok.exe login`

ログイン済み（モデル一覧が出る）なら次へ。

### Step 1: タイプ判定とプロンプト最適化（optimize は常に内包）

ユーザーの要望を、生成向けの**具体的なプロンプト**に整える。曖昧なら被写体・
動き・カメラ・尺・スタイル・アスペクト比を補う。整形は Claude（自分）が行う。
**Claude が使うモデルは Fable5、使えなければ最新（現在は Opus 4.8）。**

動画プロンプトに含めると良い要素:
- 被写体と動作（何が・どう動く）
- カメラワーク（push-in / pan / static など）
- 尺（1〜15秒）、スタイル/質感、アスペクト比、解像度
- image-to-video なら入力画像の相対パス

### Step 2: grok に委譲（ヘッドレス）

整形済みプロンプトを `grok -p` に渡す。出力先を明示すると回収が確実。

```bash
# text-to-video
"$HOME/.grok/bin/grok.exe" -p \
  'Generate a video and save it under ./.grok/generated-media/: <整形済みプロンプト>. Duration 6s, 16:9, 720p.' \
  --output-format json 2>&1 | tee /tmp/grok-out.json

# image-to-video（静止画を動かす）
"$HOME/.grok/bin/grok.exe" -p \
  'Animate ./assets/cover.jpg into a 6 second cinematic push-in. Save the mp4 under ./.grok/generated-media/.' \
  2>&1

# text-to-image
"$HOME/.grok/bin/grok.exe" -p \
  'Generate an image and save it under ./.grok/generated-media/: <整形済みプロンプト>.' \
  2>&1
```

注意:
- `-p`（= `--single`）は単発実行で stdout に応答を出して終了する。
- `--output-format json` で機械可読に。失敗時はそのエラーをユーザーに見せる。
- 動画は非同期で時間がかかる。長引く場合は run_in_background で実行し完了通知を待つ。

### Step 3: 生成物の回収と提示

生成ファイルを特定し、ユーザーに渡す。

```bash
ls -t ./.grok/generated-media/ 2>/dev/null | head -5
```

新しく出来たファイルを **SendUserFile** でユーザーに送る（status は通常 normal、
完了待ちの長尺なら proactive）。

### Step 4: レビュー（review タイプ / 任意）

生成済みメディアの評価・改善案がほしい場合、grok 自身に批評させるか、Claude が
プロンプト面から改善案を出す。grok にレビューさせる例:

```bash
"$HOME/.grok/bin/grok.exe" -p \
  'Review ./.grok/generated-media/clip.mp4 as a video director: list 3 concrete issues and a revised generation prompt.' \
  2>&1
```

レビュー結果を踏まえ、Step 1 に戻ってプロンプトを練り直し再生成するループが基本。

## Quick Reference

| 操作 | コマンド |
|---|---|
| ログイン確認 | `grok models`（未認証なら要 login）|
| ログイン | `! ~/.grok/bin/grok.exe login`（ユーザー操作）|
| 動画生成 | `grok -p 'Generate a video ...: <prompt>'` |
| 静止画→動画 | `grok -p 'Animate ./img.jpg into ...'` |
| 画像生成 | `grok -p 'Generate an image ...: <prompt>'` |
| レビュー | `grok -p 'Review ./media/x.mp4 ...'` |
| 出力先 | 既定 `./.grok/generated-media/` |

## Common Mistakes

- **未ログインのまま生成を叩く** → `You are not authenticated.`。必ず Step 0 を先に。
- **PATH 依存で `grok` 直叩き** → 環境次第で未解決。フルパスで叩く。
- **プロンプトが曖昧** → 動き・カメラ・尺・比率を補ってから渡す（Step 1）。
- **同期前提で待つ** → 動画は非同期。長引くなら run_in_background + 完了通知。
- **API キーを探す** → このスキルは API キー課金ではなく OAuth サブスク枠。キー設定不要。

## 関連

- 同型の外部CLI委譲: codex-consult（GPT系に会話文脈ごと委譲）。
- 画像/スライド用途で Grok を使う場合も本スキルで生成し、加工は slide-making 等へ。
