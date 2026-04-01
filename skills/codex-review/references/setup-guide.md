# Setup Guide: Codex CLI の準備

## インストール

```bash
npm install -g @openai/codex
```

## ログイン（ChatGPT サブスクリプション）

```bash
codex login
```

ブラウザが開くので、ChatGPT のアカウントでサインインする。
ログイン状態の確認：

```bash
codex login status
# → "Logged in using ChatGPT"
```

---

## モデル設定

`~/.codex/config.toml` でモデルを管理：

```toml
model = "gpt-5.4"                # 現在の最新モデル
model_reasoning_effort = "high"  # コードレビューには high 推奨
```

新しいモデルがリリースされたら `model` の値を更新するだけでよい。

---

## 再ログインが必要な場合

```bash
codex logout
codex login
```

---

## 動作確認

```bash
# バージョン確認
codex --version

# ログイン状態確認
codex login status

# 簡単なテスト（git リポジトリ内で実行）
codex review --uncommitted "テスト"
```
