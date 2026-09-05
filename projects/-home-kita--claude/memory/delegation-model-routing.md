---
name: delegation-model-routing
description: 委譲先のモデル使い分け。プラン・診断=最新モデル(GPT-6 Astra / Fable 5.1)、実装=GPT-6 Astra、不可ならSonnet 5（ユーザー指示 2026-09-05）
metadata: 
  node_type: memory
  type: feedback
  originSessionId: 8766f041-3971-53bb-a375-4b41305dacaa
  modified: 2026-09-05T05:25:04.570Z
---

**委譲先の使い分け（ユーザー指示 2026-09-05）**:

| 用途 | 委譲先 |
|---|---|
| **プラン・診断・原因究明**（大事な元になるもの） | **最新モデル**: GPT-6 Astra（Codex）または **Fable 5.1**（`Agent` の `model: "fable"`） |
| **与えられたプランの実装** | **GPT-6 Astra**（Codex）。不可なら **Sonnet 5** |

ユーザー原文: 「どちらかというと、プランや診断などの大事な元は gpt6astra や fable5.1 のような最新モデル。
与えられたプランを実装するときは、gpt6astra か無理なら sonnet5 にして」

**Why:** プラン・診断は後段すべての精度上限を決めるため、最新モデルの推論力を使う。実装は与えられた
仕様に従う作業なので、Astra が使えないときは Sonnet 5 で代替できる。

**How to apply:**
- Codex の既定モデルは `~/.codex/config.toml` の `model` で決まる。**2026-09-05 時点で `gpt-6-astra`**
  （それ以前の記憶にある `gpt-5.6-sol` は古い。委譲前に config を確認する）
- **モデル名は `gpt-6-astra`**。`astra` / `gpt-5.7-astra` / `astra-preview` は `not supported` で弾かれる
- Codex が利用上限に達したら（`You've hit your usage limit ... try again at <日時>`）その時刻まで使えない。
  **実装は Sonnet 5 へ、診断は Fable 5.1 へ**振り分ける
- Codex はジョブ登録に失敗することがある（タスクIDを返すのに `codex-companion.mjs status` に現れない）。
  その場合も切り替える
- 関連: [[codex-unavailable-sonnet5-fallback]]、[[codex-broker-stall-cleanup]]、[[plan-fable-implement-codex-goal]]

## 追記（2026-09-05）: Astra には CLI 0.154.0-alpha 以降が要る

`gpt-6-astra` を安定版 CLI（0.153.4 = npm の `latest`）で呼ぶと
`The 'gpt-6-astra' model requires a newer version of Codex` で 400 になる。
**npm の `latest` にはまだ来ていない**ので、alpha タグから入れる:

```bash
npm view @openai/codex dist-tags          # alpha-linux-x64 を確認
npm_config_prefix=/tmp/codex-alpha-test npm install -g @openai/codex@0.154.0-alpha.3
```

グローバルを alpha で上書きすると他セッションの Codex ジョブを巻き込むので、
**隔離 prefix に入れて先に検証する**。alpha では上記400は消え、モデル自体は通った。

`codex exec` の罠2つ:
- 引数でプロンプトを渡しても `Reading additional input from stdin...` で待つ → `< /dev/null` を付ける
- リポジトリ外だと `Not inside a trusted directory` → `--skip-git-repo-check` か、対象リポジトリで実行

なお 2026-09-05 時点では alpha でも**アカウント側が利用上限**（9月8日 10:22 まで）。
「バージョン不足」と「利用上限」は**別々に**出るので、片方を直しても他方が残ることがある。
