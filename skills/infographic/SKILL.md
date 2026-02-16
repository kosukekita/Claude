---
name: infographic
description: AntV Infographic を活用したインフォグラフィック生成。テキストや情報から視覚的なインフォグラフィックを作成。約200種のテンプレート、手書き風・グラデーション等のテーマ、SVG出力対応。
---

# Infographic Creator

AntV Infographic を使用して、テキストや情報から高品質なインフォグラフィックを生成します。

**公式サイト**: https://infographic.antv.vision/

## AntV Infographic 構文

インフォグラフィック専用 DSL で、AI 生成・ストリーミング出力に最適化されています。

### 基本構造

```infographic
infographic <template-name>
data
  title タイトル
  desc 説明
  <data-field>
    - label ラベル
      desc 説明
      icon アイコン名
theme
  palette #3b82f6 #8b5cf6 #f97316
```

### 構文ルール

- 第一行は `infographic <template-name>`
- `data` / `theme` ブロックは 2 スペースインデント
- キーと値はスペース区切り（`key value`）
- 配列は `-` プレフィックス
- アイコンは `icon star fill` のようにキーワード指定

### データフィールド選択

テンプレートに応じて適切なフィールドを使用:

| テンプレート | データフィールド | 備考 |
|-------------|-----------------|------|
| `list-*` | `lists` | リスト形式 |
| `sequence-*` | `sequences` | 順序・フロー（`order asc/desc` 可） |
| `compare-*` | `compares` | 比較（`children` でグループ化） |
| `hierarchy-structure` | `items` | 独立した階層（3層まで） |
| `hierarchy-*` | `root` | ツリー構造（`children` でネスト） |
| `relation-*` | `nodes` + `relations` | 関係図 |
| `chart-*` | `values` | チャート |

## 利用可能なテンプレート

### リスト系 (`list-*`)
- `list-row-horizontal-icon-arrow` - 横並びアイコン矢印
- `list-column-done-list` - 縦チェックリスト
- `list-column-simple-vertical-arrow` - 縦矢印
- `list-column-vertical-icon-arrow` - 縦アイコン矢印
- `list-grid-badge-card` - グリッドバッジカード
- `list-grid-candy-card-lite` - キャンディカード
- `list-grid-ribbon-card` - リボンカード
- `list-sector-plain-text` - セクター
- `list-waterfall-badge-card` - ウォーターフォール
- `list-waterfall-compact-card` - コンパクトウォーターフォール
- `list-zigzag-down-compact-card` - ジグザグ下向き
- `list-zigzag-down-simple` - シンプルジグザグ下
- `list-zigzag-up-compact-card` - ジグザグ上向き
- `list-zigzag-up-simple` - シンプルジグザグ上

### シーケンス系 (`sequence-*`)
- `sequence-timeline-simple` - シンプルタイムライン
- `sequence-timeline-rounded-rect-node` - 角丸タイムライン
- `sequence-snake-steps-simple` - 蛇行ステップ
- `sequence-snake-steps-compact-card` - 蛇行コンパクトカード
- `sequence-snake-steps-underline-text` - 蛇行下線テキスト
- `sequence-roadmap-vertical-simple` - 縦ロードマップ
- `sequence-roadmap-vertical-plain-text` - 縦ロードマップテキスト
- `sequence-stairs-front-compact-card` - 階段コンパクト
- `sequence-stairs-front-pill-badge` - 階段バッジ
- `sequence-ascending-stairs-3d-underline-text` - 3D階段
- `sequence-ascending-steps` - 上昇ステップ
- `sequence-circular-simple` - 円形
- `sequence-color-snake-steps-horizontal-icon-line` - カラー蛇行
- `sequence-cylinders-3d-simple` - 3Dシリンダー
- `sequence-filter-mesh-simple` - フィルターメッシュ
- `sequence-funnel-simple` - ファネル
- `sequence-horizontal-zigzag-underline-text` - 横ジグザグ
- `sequence-mountain-underline-text` - 山型
- `sequence-pyramid-simple` - ピラミッド
- `sequence-zigzag-pucks-3d-simple` - 3Dジグザグ
- `sequence-zigzag-steps-underline-text` - ジグザグステップ

### 比較系 (`compare-*`)
- `compare-swot` - SWOT分析
- `compare-binary-horizontal-badge-card-arrow` - 二項比較バッジ
- `compare-binary-horizontal-simple-fold` - 二項折りたたみ
- `compare-binary-horizontal-underline-text-vs` - VS比較
- `compare-hierarchy-left-right-circle-node-pill-badge` - 左右階層比較
- `compare-quadrant-quarter-circular` - 円形象限
- `compare-quadrant-quarter-simple-card` - 象限カード

### 階層系 (`hierarchy-*`)
- `hierarchy-structure` - 組織図
- `hierarchy-tree-curved-line-rounded-rect-node` - 曲線ツリー
- `hierarchy-tree-tech-style-badge-card` - テックスタイルツリー
- `hierarchy-tree-tech-style-capsule-item` - カプセルツリー
- `hierarchy-mindmap-branch-gradient-capsule-item` - マインドマップ
- `hierarchy-mindmap-level-gradient-compact-card` - レベルマインドマップ

### 関係図系 (`relation-*`)
- `relation-dagre-flow-tb-simple-circle-node` - フローチャート
- `relation-dagre-flow-tb-badge-card` - バッジフロー
- `relation-dagre-flow-tb-animated-badge-card` - アニメーションフロー
- `relation-dagre-flow-tb-animated-simple-circle-node` - アニメーション円形フロー

### チャート系 (`chart-*`)
- `chart-bar-plain-text` - 棒グラフ
- `chart-column-simple` - 縦棒グラフ
- `chart-line-plain-text` - 折れ線グラフ
- `chart-pie-compact-card` - 円グラフカード
- `chart-pie-donut-pill-badge` - ドーナツバッジ
- `chart-pie-donut-plain-text` - ドーナツテキスト
- `chart-pie-plain-text` - 円グラフテキスト
- `chart-wordcloud` - ワードクラウド

## テンプレート選択ガイド

| ユースケース | 推奨テンプレート |
|-------------|-----------------|
| 順序・フロー・ステップ | `sequence-*` |
| タイムライン | `sequence-timeline-*` |
| ロードマップ | `sequence-roadmap-*` |
| 要点リスト | `list-row-*`, `list-grid-*` |
| 利点・欠点比較 | `compare-binary-*` |
| SWOT分析 | `compare-swot` |
| 象限分析 | `compare-quadrant-*` |
| 組織図・ツリー | `hierarchy-tree-*`, `hierarchy-structure` |
| マインドマップ | `hierarchy-mindmap-*` |
| フローチャート・関係図 | `relation-*` |
| 統計データ | `chart-*` |
| ワードクラウド | `chart-wordcloud` |

## テーマ設定

### 基本テーマ

```infographic
theme dark
  palette
    - #61DDAA
    - #F6BD16
    - #F08BB4
```

### スタイル設定

```infographic
theme
  stylize rough
  base
    text
      font-family 851tegakizatsu
```

**利用可能なスタイル**:
- `rough` - 手描き風
- `pattern` - パターン塗り
- `linear-gradient` - 線形グラデーション
- `radial-gradient` - 放射グラデーション

## 構文例

### リスト

```infographic
infographic list-grid-badge-card
data
  title 主要機能
  lists
    - label 高速
      desc 処理速度10倍
      icon flash fast
    - label 安全
      desc 暗号化対応
      icon secure shield
    - label 簡単
      desc ワンクリック操作
      icon click
```

### シーケンス

```infographic
infographic sequence-timeline-simple
data
  title プロジェクト計画
  sequences
    - label 企画
      desc 要件定義
    - label 設計
      desc アーキテクチャ設計
    - label 開発
      desc 実装・テスト
    - label リリース
      desc 本番公開
```

### 比較（SWOT）

```infographic
infographic compare-swot
data
  compares
    - label 強み
      children
        - label 技術力
        - label ブランド力
    - label 弱み
      children
        - label コスト高
        - label 人員不足
    - label 機会
      children
        - label 市場拡大
        - label 新技術
    - label 脅威
      children
        - label 競合増加
        - label 規制強化
```

### 階層

```infographic
infographic hierarchy-tree-tech-style-badge-card
data
  root
    label 会社
    children
      - label 開発部
        children
          - label フロントエンド
          - label バックエンド
      - label 営業部
        children
          - label 国内
          - label 海外
```

### 関係図

```infographic
infographic relation-dagre-flow-tb-simple-circle-node
data
  relations
    開始 --> 処理A
    処理A --> 判定
    判定 -Yes-> 処理B
    判定 -No-> 処理C
    処理B --> 終了
    処理C --> 終了
```

## HTML 生成

インフォグラフィック構文から HTML ファイルを生成:

```html
<!DOCTYPE html>
<html lang="ja">
<head>
  <meta charset="UTF-8">
  <title>{title} - Infographic</title>
  <style>
    body { margin: 0; padding: 20px; }
    #container { width: 100%; height: 100vh; }
  </style>
</head>
<body>
  <div id="container"></div>
  <script src="https://unpkg.com/@antv/infographic@latest/dist/infographic.min.js"></script>
  <script>
    const infographic = new AntVInfographic.Infographic({
      container: '#container',
      width: '100%',
      height: '100%',
      editable: true
    });

    const syntax = `{syntax}`;

    infographic.render(syntax);
    document.fonts?.ready.then(() => {
      infographic.render(syntax);
    });
  </script>
</body>
</html>
```

## 生成ワークフロー

1. **要件理解**: ユーザーの内容から構造（タイトル、説明、項目、階層）を抽出
2. **テンプレート選択**: 情報構造に適したテンプレートを選択
3. **構文生成**: AntV Infographic 構文でデータを構造化
4. **HTML出力**: 構文を埋め込んだ HTML ファイルを生成
5. **ファイル保存**: `<title>-infographic.html` として保存

## 注意事項

- ユーザーの入力言語を尊重（日本語入力なら日本語で出力）
- JSON や Markdown ではなく、Infographic 構文を使用
- 二項比較テンプレート（`compare-binary-*`）は必ず 2 つのルートノード
- 階層テンプレート（`hierarchy-*`）は単一の `root` から `children` でネスト
- SVG エクスポート機能を含める
