# Chrome CDP モード詳細リファレンス

## Prerequisites

- Chrome / Chromium / Brave / Edge / Vivaldi でリモートデバッグを有効化
  - `chrome://inspect/#remote-debugging` を開き、スイッチをオン
  - または起動フラグ: `--remote-debugging-port=9222`
- Node.js 22+（内蔵 WebSocket を使用、Puppeteer 不要）
- `DevToolsActivePort` が非標準パスにある場合: `CDP_PORT_FILE` 環境変数でフルパスを指定

## コマンド詳細

スクリプトパス: `~/.claude/skills/browser-automation/scripts/cdp.mjs`

### list — 開いているページ一覧

```bash
node scripts/cdp.mjs list
```

出力例:
```
6BE827FA  https://example.com  Example Domain
A3F2910B  https://github.com   GitHub
```

`<target>` は一意のプレフィックスを指定（例: `6BE827FA`）。

### shot — スクリーンショット

```bash
node scripts/cdp.mjs shot <target> [file]
# デフォルト: screenshot-<target>.png をランタイムディレクトリに保存
```

- ビューポートのみキャプチャ（フォールド下のコンテンツは `eval` でスクロール後に撮影）
- DPR（デバイスピクセル比）を出力する

### snap — アクセシビリティツリースナップショット

```bash
node scripts/cdp.mjs snap <target>
node scripts/cdp.mjs snap <target> --compact   # コンパクト表示（推奨）
```

ページ構造の確認には `html` より `snap --compact` が高速で推奨。

### eval — JavaScript 評価

```bash
node scripts/cdp.mjs eval <target> <expr>
```

```bash
# 例
node scripts/cdp.mjs eval 6BE827FA "document.title"
node scripts/cdp.mjs eval 6BE827FA "document.querySelectorAll('a').length"
```

**注意**: 複数の `eval` 呼び出し間で DOM が変化する場合（クリック後カードインデックスがシフト等）、`querySelectorAll(...)[i]` のインデックスに依存しないこと。1回の `eval` でデータをまとめて取得するか、安定したセレクタを使用する。

### html — ページ/要素の HTML 取得

```bash
node scripts/cdp.mjs html <target> [selector]
# selector 省略時: ページ全体の HTML
```

### nav — ページナビゲーション

```bash
node scripts/cdp.mjs nav <target> <url>
# ロード完了まで待機
```

### click — 要素クリック（CSS セレクタ）

```bash
node scripts/cdp.mjs click <target> <selector>
```

### clickxy — 座標クリック

```bash
node scripts/cdp.mjs clickxy <target> <x> <y>
# CSS ピクセル座標で指定
```

### type — テキスト入力

```bash
node scripts/cdp.mjs type <target> <text>
```

- `Input.insertText` を使用。クロスオリジン iframe でも動作（`eval` は不可）
- `click` または `clickxy` でフォーカス後に `type` を呼ぶ

### loadall — 「もっと読む」を繰り返しクリック

```bash
node scripts/cdp.mjs loadall <target> <selector> [ms]
# デフォルト: クリック間隔 1500ms
# 指定セレクタが消えるまで繰り返しクリック
```

### evalraw — 生 CDP コマンド

```bash
node scripts/cdp.mjs evalraw <target> <method> [json]
# 例: スクロール
node scripts/cdp.mjs evalraw 6BE827FA "Runtime.evaluate" '{"expression":"window.scrollTo(0,1000)"}'
```

### net — リソースタイミング

```bash
node scripts/cdp.mjs net <target>
```

### open — 新しいタブを開く

```bash
node scripts/cdp.mjs open [url]
# 各タブで初回接続時に「デバッグを許可」モーダルが表示される
```

### stop — デーモン停止

```bash
node scripts/cdp.mjs stop [target]   # 特定タブのデーモンを停止
node scripts/cdp.mjs stop            # 全デーモンを停止
```

## 座標系

`shot` はネイティブ解像度で画像を保存: **画像ピクセル = CSS ピクセル × DPR**

CDP 入力イベント（`clickxy` 等）は **CSS ピクセル** で指定する。

```
CSS px = スクリーンショット画像px ÷ DPR
```

例: DPR=2（Retina）の場合、スクリーンショット座標を 2 で割った値を使う。

`shot` 実行時に現在ページの DPR が出力される。

## アーキテクチャ

- **デーモンベース**: タブごとに永続デーモンプロセスが CDP セッションを保持
- `open` コマンドはタブ初回アクセス時に「デバッグを許可」モーダルをトリガー
- デーモンは 20 分間のアイドル後に自動終了
- Puppeteer 不依存: 生 WebSocket で CDP に接続

## Tips

- ページ構造の確認: `snap --compact` を優先（`html` より高速）
- クロスオリジン iframe へのテキスト入力: `click`/`clickxy` でフォーカス → `type`（`eval` 経由の入力は不可）
- フォールド下のコンテンツをスクリーンショット: `eval` でスクロール後に `shot`
- 多数タブでも即時接続（Puppeteer と異なり起動コスト不要）
