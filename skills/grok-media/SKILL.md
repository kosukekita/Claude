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
**以下は実機（Windows, grok 0.2.51, X Premium+ ログイン）で検証済みの手順。**

## 前提・土台（実機検証済み）

- **CLI 実体**: `~/.grok/bin/grok.exe`（Windows）。PATH 未解決を想定し、原則
  **フルパス** `"$HOME/.grok/bin/grok.exe"` で叩く。
- **認証**: X Premium+ / SuperGrok の **OAuth**。**画像・動画ともサブスク枠で生成可**
  （API キー従量課金は不要。$0.05/秒は別経路=Imagine API の価格で、本スキルは無関係）。
- **生成の仕組み**: Grok Build はエージェント。メディア生成ツールを**内蔵**し、
  **自然言語の指示で発火**する。専用サブコマンドは無い。
  - 画像ツールの実名は **`image_gen`**（Web情報の `generate_image` ではない）。
- **ヘッドレス実行**: `grok -p "<指示>"` で単発実行し stdout に結果を出す。
- **出力先（重要・実機確認）**: 生成物は cwd 直下ではなく **セッションディレクトリ**配下に出る:
  `~/.grok/sessions/<URLエンコードしたcwd>/<session-id>/images/N.jpg`
  → ファイルは **広域 ls か grok 自身に絶対パスを聞いて回収**する（下記 Step 3）。

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
"$HOME/.grok/bin/grok.exe" models 2>&1 | head -3
```

`You are not authenticated.` が出たら止めて、ユーザーに **手元のターミナル**での
ログインを依頼する（**`!` プレフィックス経由や非対話実行では OAuth が完走しない**）:

> 手元の PowerShell で実行してください:
> `& "$env:USERPROFILE\.grok\bin\grok.exe" login --device-auth`
> 表示された URL を X Premium+ ログイン済みブラウザで開き、コードを承認。

`You are logged in with grok.com.` が出ればログイン済み。

### Step 1: タイプ判定とプロンプト最適化（optimize は常に内包）

ユーザーの要望を生成向けの**具体的プロンプト**に整える。曖昧なら被写体・動き・
カメラ・尺・スタイル・アスペクト比を補う。整形は Claude（自分）が行う。
**Claude が使うモデルは Fable5、使えなければ最新（現在は Opus 4.8）。**

動画プロンプトに含めると良い要素: 被写体と動作 / カメラワーク(push-in・pan・static) /
尺(1〜15秒) / スタイル・質感 / アスペクト比・解像度 / image-to-video なら入力画像パス。

### Step 2: grok に委譲（ヘッドレス）

**クリーンな作業ディレクトリ**で実行する（既存プロジェクト直下だと grok が周辺を
探索して `Auth(AuthorizationRequired)` 等で落ちることがある。実機で確認済み）。

```bash
WORK="$(mktemp -d)"; cd "$WORK"   # クリーンな cwd

# text-to-image
"$HOME/.grok/bin/grok.exe" -p \
  'Use your image_gen tool to create an image: <整形済みプロンプト>.' 2>&1

# text-to-video
"$HOME/.grok/bin/grok.exe" -p \
  'Use your video generation tool to create a short Ns video: <整形済みプロンプト>.' 2>&1

# image-to-video（静止画を動かす）
"$HOME/.grok/bin/grok.exe" -p \
  'Animate ./input.jpg into an N second cinematic push-in.' 2>&1
```

注意:
- `-p`（=`--single`）は単発実行で応答を stdout に出して終了。
- **動画は非同期で時間がかかる**。run_in_background で実行し完了通知を待つ。
- 失敗時はその stderr/JSON をそのままユーザーに見せる。

### Step 3: 生成物の回収（出力先がセッション配下なので確実な方法を使う）

確実なのは **grok 自身に絶対パスを聞く**（同じセッションを `-r` で継続）:

```bash
"$HOME/.grok/bin/grok.exe" -r -p \
  'What is the absolute file path of the media you just generated? Reply with ONLY the path.' 2>&1
```

または広域検索:

```bash
ls -t "$HOME/.grok/sessions/"*"/"*"/images/"* 2>/dev/null | head -3
# 動画は images の隣（videos 等）の可能性。初回は session ディレクトリを ls -R で確認。
```

掴んだファイルを **SendUserFile** でユーザーに送る（長尺の完了通知後なら status=proactive）。

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
| 動画生成 | `grok -p 'Use your video generation tool to create a short Ns video: <prompt>'` |
| 静止画→動画 | `grok -p 'Animate ./img.jpg into an N second push-in'` |
| 回収 | `grok -r -p 'absolute path of the media you just generated?'` |
| 出力先 | `~/.grok/sessions/<enc-cwd>/<session-id>/images/N.jpg` |

## Common Mistakes

- **`!` 経由や非対話で login** → OAuth が完走しない。**手元ターミナルで** `login --device-auth`。
- **既存プロジェクト直下で生成** → grok が周辺探索して Auth エラーで落ちることがある。**mktemp の空dirで**。
- **cwd 直下に生成物を探す** → 出ない。実体は **session ディレクトリ配下**。`-r` で grok に絶対パスを聞く。
- **PATH 依存で `grok` 直叩き** → 環境次第で未解決。フルパスで。
- **API キーを探す** → 不要。X Premium+ OAuth のサブスク枠で動く。
- **動画を同期前提で待つ** → 非同期。run_in_background + 完了通知。
- **ツール名 `generate_image` と決め打ち** → 実名は **`image_gen`**。動画ツール名は初回実行ログで確認。

## 関連

- 同型の外部CLI委譲: codex-consult（GPT系に会話文脈ごと委譲）。
- 生成画像をスライドに使うなら slide-making、図解なら infographic へ。
