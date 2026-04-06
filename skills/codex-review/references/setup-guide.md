# Setup Guide: Codex CLI + codex-plugin-cc の準備

---

## Part 1: Codex CLI のインストール

```bash
npm install -g @openai/codex
```

### ログイン（ChatGPT サブスクリプション）

```bash
codex login
```

ブラウザが開くので、ChatGPT のアカウントでサインインする。
ログイン状態の確認：

```bash
codex login status
# → "Logged in using ChatGPT"
```

### モデル設定

`~/.codex/config.toml` でモデルを管理：

```toml
personality = "pragmatic"
model = "gpt-5.4"                # 現在の最新モデル
model_reasoning_effort = "high"  # コードレビューには high 推奨
```

新しいモデルがリリースされたら `model` の値を更新するだけでよい。

### 再ログインが必要な場合

```bash
codex logout
codex login
```

### 動作確認

```bash
# バージョン確認
codex --version

# ログイン状態確認
codex login status

# 簡単なテスト（git リポジトリ内で実行）
codex review --uncommitted "テスト"
```

---

## Part 2: codex-plugin-cc のインストール

### 前提条件

- Claude Code がインストール済み
- Node.js 18.18 以上
- `CLAUDE_CODE_GIT_BASH_PATH` 環境変数の設定（Windows 必須）

### CLAUDE_CODE_GIT_BASH_PATH の設定（Windows）

Claude Code の `claude plugin` コマンドを使用するために必要。

**方法 1: Windows 環境変数として設定（推奨・永続）**

コントロールパネル → システム → 詳細設定 → 環境変数 から追加:
- 変数名: `CLAUDE_CODE_GIT_BASH_PATH`
- 変数値: `C:\Users\u8792\AppData\Local\Programs\Git\usr\bin\bash.exe`

**方法 2: ターミナルセッション内で設定（一時的）**

```bash
export CLAUDE_CODE_GIT_BASH_PATH="C:\\Users\\u8792\\AppData\\Local\\Programs\\Git\\usr\\bin\\bash.exe"
```

### インストールコマンド

Claude CLI バイナリのパス:
```
/c/Users/u8792/.antigravity/extensions/anthropic.claude-code-2.1.92-win32-x64/resources/native-binary/claude.exe
```

```bash
# 変数設定
CLAUDE_BIN="/c/Users/u8792/.antigravity/extensions/anthropic.claude-code-2.1.92-win32-x64/resources/native-binary/claude.exe"
export CLAUDE_CODE_GIT_BASH_PATH="C:\\Users\\u8792\\AppData\\Local\\Programs\\Git\\usr\\bin\\bash.exe"

# Step 1: マーケットプレース追加
$CLAUDE_BIN plugin marketplace add openai/codex-plugin-cc

# Step 2: プラグインインストール
$CLAUDE_BIN plugin install codex@openai-codex

# Step 3: 確認
$CLAUDE_BIN plugin list
```

### プラグインのセットアップ確認（Claude Code セッション内）

Claude Code を再起動（または `/reload-plugins`）した後：

```
/codex:setup
```

Codex CLI のインストール状態と認証状態を確認する。未ログインの場合は `!codex login` を実行する。

### プラグインの更新・アンインストール

```bash
# 更新
$CLAUDE_BIN plugin update codex@openai-codex

# アンインストール
$CLAUDE_BIN plugin uninstall codex@openai-codex
```

---

## トラブルシューティング

### `claude plugin` でエラーが出る
```
Claude Code on Windows requires git-bash...
```
→ `CLAUDE_CODE_GIT_BASH_PATH` が設定されていない。上記の設定手順を実施する。

### プラグインコマンドが認識されない
→ `/reload-plugins` を実行するか、Claude Code を再起動する。

### Codex CLI バージョンが古い
```bash
npm update -g @openai/codex
```
