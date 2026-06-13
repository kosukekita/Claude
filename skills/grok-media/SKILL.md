---
name: grok-media
description: >
  xAI 公式 Grok Build CLI（X Premium+ / SuperGrok の OAuth で認証）に委譲して、
  動画生成（画像→動画・参照→動画）・画像生成・画像編集・生成済みメディアのレビュー・
  生成用プロンプトの最適化を行うスキル。codex-consult と同型の外部CLI委譲。
  Use when the user wants to generate a video or image with Grok, animate a still
  image, edit an image, review/critique generated media, or turn a vague idea into
  a strong generation prompt.
  Trigger phrases: Grokで動画, Grok動画生成, 動画を作って（Grok）, Grokで画像,
  画像生成（Grok）, この画像を動かして, 画像を編集（Grok）, Grok Imagine, grok-imagine,
  生成した動画をレビュー, 動画プロンプトを最適化, generate video with Grok,
  generate image with Grok, animate this image, grok imagine.
  Do NOT trigger for: Claude/他ツール自身の画像生成、コードレビュー（code-reviewer 等）、
  arXiv/論文検索（alphaxiv/research-toolkit）。本スキルは Grok Build CLI による
  メディア生成・編集・そのレビュー・プロンプト整形に限る。
allowed-tools: Bash, Read, Glob, SendUserFile, AskUserQuestion
---

# Grok Media

xAI 公式 **Grok Build CLI** に委譲して、Grok Imagine の画像・動画生成と、その
レビュー・プロンプト最適化を行う。codex-consult と同じ「外部 AI CLI 委譲」型。
**本手順は実機（Windows / grok 0.2.51 / X Premium+ ログイン）で画像・動画とも生成成功を確認済み。**

## 前提・土台（実機検証済み）

- **CLI 実体**: `~/.grok/bin/grok.exe`（Windows）。PATH 未解決を想定し、原則
  **フルパス** `"$HOME/.grok/bin/grok.exe"` で叩く。
- **認証**: X Premium+ / SuperGrok の **OAuth**。**画像・動画ともサブスク枠で生成可**
  （API キー従量課金は不要。"$0.05/秒" は別経路=Imagine API の価格で本スキルは無関係）。
  ※ サブスクには利用上限はあるが、生成ごとに財布から引かれる従量課金ではない。
- **生成の仕組み**: Grok Build はエージェント。メディアツールを**内蔵**し、**自然言語の
  指示で発火**する。専用サブコマンドは無い。grok が持つツールの実名（grok 本人が回答）:
  - `image_gen` … テキスト→画像
  - `image_edit` … 画像編集
  - `image_to_video` … 入力画像→動画
  - `reference_to_video` … 参照画像→動画
  - **text-to-video の専用ツールは無い**。「テキストから動画」は
    **image_gen で画像→ image_to_video で動かす 2 段**で実現する。
- **ヘッドレス実行**: `grok -p "<指示>"` で単発実行。**応答テキストは空でも、ファイルは
  生成されている**ことがある（回収は Step 3 で確実に行う）。
- **出力先（実機確認）**: 生成物は cwd 直下でなく**セッションディレクトリ**配下に出る:
  - 画像: `~/.grok/sessions/<URLエンコードしたcwd>/<session-id>/images/N.jpg`
  - 動画: `~/.grok/sessions/<URLエンコードしたcwd>/<session-id>/videos/N.mp4`

## いつ使うか

| やりたいこと | ツール / 手順 |
|---|---|
| テキストから画像 | `image_gen` |
| 画像を編集 | `image_edit` |
| 静止画を動かす | `image_to_video`（要・入力画像）|
| テキストから動画 | image_gen → image_to_video の2段 |
| 参照画像から動画 | `reference_to_video` |
| 生成物のレビュー | grok にレビューさせる（Step 4）|
| プロンプト最適化 | Claude が整形（Step 1、常に内包）|

## Instructions

### Step 0: ログイン確認（毎回最初に）

```bash
"$HOME/.grok/bin/grok.exe" models 2>&1 | head -3
```

`You are not authenticated.` が出たら止めて、ユーザーに **手元のターミナル**での
ログインを依頼する（**`!` プレフィックス経由や非対話実行では OAuth が完走しない**。実機確認）:

> 手元の PowerShell で実行してください:
> `& "$env:USERPROFILE\.grok\bin\grok.exe" login --device-auth`
> 表示された URL を X Premium+ ログイン済みブラウザで開き、コードを承認。

`You are logged in with grok.com.` が出ればログイン済み。

### Step 1: タイプ判定とプロンプト最適化（optimize は常に内包）

ユーザーの要望を生成向けの**具体的プロンプト**に整える。曖昧なら被写体・動き・
カメラ・尺・スタイル・アスペクト比を補う。整形は Claude（自分）が行う。
**Claude が使うモデルは Fable5、使えなければ最新（現在は Opus 4.8）。**

動画プロンプトに含めると良い要素: 被写体と動作 / カメラワーク(push-in・pan・static) /
尺(1〜15秒) / スタイル・質感 / アスペクト比・解像度 / 入力画像のパス。

### Step 2: grok に委譲（ヘッドレス・クリーンな作業dir）

**必ずクリーンな空ディレクトリ**で実行する（既存プロジェクト直下だと grok が周辺を
探索し `Auth(AuthorizationRequired)` 等で生成手前で落ちることがある。実機確認）。

```bash
WORK="$(mktemp -d)"; cd "$WORK"

# 画像生成
"$HOME/.grok/bin/grok.exe" -p \
  'Use your image_gen tool to create an image: <整形済みプロンプト>.' 2>&1

# 画像→動画（静止画を動かす）。入力画像を WORK に置いてから:
cp /path/to/input.jpg "$WORK/input.jpg"
"$HOME/.grok/bin/grok.exe" -p \
  'Use your image_to_video tool to animate ./input.jpg into a short 3-second video: <動き>. Save the video file.' 2>&1

# テキスト→動画 は2段（まず画像、その画像を上の image_to_video へ）
```

注意:
- `Auth(AuthorizationRequired)` の ERROR 行は **毎回出るが致命的ではない**ノイズ。
  ファイルが生成されていれば成功（画像・動画ともこのログが出ても生成成功した）。
- **動画は時間がかかる**（実機で i2v 約50秒）。run_in_background で実行し完了通知を待つ。

### Step 3: 生成物の回収（出力先がセッション配下なので確実な方法を使う）

応答が空でもファイルはある。**grok 自身に絶対パスを聞く**のが最も確実（`-r` で同セッション継続）:

```bash
"$HOME/.grok/bin/grok.exe" -r -p \
  'What is the absolute file path of the media you just generated? Reply with ONLY the path.' 2>&1
```

または直接探索（画像=images, 動画=videos）:

```bash
ls -t "$HOME/.grok/sessions/"*"/"*"/videos/"*.mp4 2>/dev/null | head -3
ls -t "$HOME/.grok/sessions/"*"/"*"/images/"*.jpg 2>/dev/null | head -3
```

掴んだファイルを **SendUserFile** で送る（長尺の完了通知後は status=proactive）。

### Step 4: レビュー（review タイプ / 任意）

```bash
"$HOME/.grok/bin/grok.exe" -p \
  'Review <生成物の絶対パス> as a director: list 3 concrete issues and a revised generation prompt.' 2>&1
```

結果を踏まえ Step 1 に戻ってプロンプトを練り直し再生成するループが基本。

## Quick Reference

| 操作 | コマンド |
|---|---|
| ログイン確認 | `grok models`（未認証なら要 login）|
| ログイン | 手元ターミナルで `grok login --device-auth`（ユーザー操作）|
| 画像生成 | `grok -p 'Use your image_gen tool to create an image: <prompt>'` |
| 画像編集 | `grok -p 'Use your image_edit tool to ... ./img.jpg'` |
| 画像→動画 | `grok -p 'Use your image_to_video tool to animate ./input.jpg into ...'` |
| 参照→動画 | `grok -p 'Use your reference_to_video tool with ./ref.jpg ...'` |
| 回収 | `grok -r -p 'absolute path of the media you just generated?'` |
| 出力先 | 画像 `.../sessions/<enc-cwd>/<sid>/images/N.jpg` / 動画 `.../videos/N.mp4` |

## Common Mistakes

- **`!` 経由や非対話で login** → OAuth が完走しない。**手元ターミナルで** `login --device-auth`。
- **既存プロジェクト直下で生成** → grok が周辺探索して Auth エラーで生成手前で落ちる。**mktemp の空dirで**。
- **応答が空＝失敗、と即断** → ファイルは生成済みのことがある。Step 3 で必ず回収確認。
- **cwd 直下に生成物を探す** → 出ない。実体は **session ディレクトリの images/ または videos/**。
- **"テキストから動画"を1ツールで頼む** → text-to-video 専用ツールは無い。**image_gen→image_to_video の2段**。
- **PATH 依存で `grok` 直叩き** → 環境次第で未解決。フルパスで。
- **API キーを探す** → 不要。X Premium+ OAuth のサブスク枠で動く。
- **動画を同期前提で待つ** → 非同期・約1分。run_in_background + 完了通知。

## 関連

- 同型の外部CLI委譲: codex-consult（GPT系に会話文脈ごと委譲）。
- 生成画像をスライドに使うなら slide-making、図解なら infographic へ。
