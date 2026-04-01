# Setup Guide: Gemini CLI の準備

## インストール

```bash
npm install -g @google/gemini-cli
```

## 初回ログイン

```bash
gemini
```

対話モードが起動したらブラウザで Google アカウントにログインする。

---

## Preview Features の有効化（Gemini 3 系モデル使用に必須）

1. `gemini` を対話モードで起動
2. `/settings` を実行
3. **Preview Features (e.g., models)** を `true` に切り替え
4. `r` を押して設定を反映し CLI を再起動
5. `/model` で **Auto (Gemini 3)** が選択可能なことを確認

---

## 利用可能なモデル一覧

| モデル名 | 特徴 | 要件 |
|---|---|---|
| `gemini-3-pro-preview` | 最新・最高性能（デフォルト） | Preview Features 要 |
| `gemini-3-flash-preview` | 高速・低コスト | Preview Features 要 |
| `gemini-2.5-pro` | 安定版（フォールバック） | 不要 |

---

## モデル確認方法

```bash
# 対話モードで確認
gemini
/model
```
