---
name: achievement
description: >
  喜多洸介（Kosuke Kita）の学術業績（論文・書籍・学会発表・受賞歴・助成金）を
  管理・参照・出力するスキル。CV作成、業績リスト生成、研究実績の要約に対応。
  Use when user asks about publications, academic achievements, CV, grants, awards,
  or research output. Trigger phrases: "業績", "CV", "論文一覧", "発表履歴",
  "受賞歴", "助成金", "publications", "achievements", "research output",
  "curriculum vitae", "業績リスト", "学会発表", "研究費".
---

# Achievement

> 喜多洸介の学術業績を管理・参照・出力するスキル。

## Instructions

### Step 1: リクエスト分類

ユーザーのリクエストを以下のカテゴリに分類:

| カテゴリ | 内容 | 例 |
|---------|------|-----|
| **全業績出力** | CV・業績一覧の完全リスト | 「CV を作成して」「業績一覧を出力して」 |
| **カテゴリ別出力** | 特定カテゴリのみ抽出 | 「論文一覧を出して」「受賞歴は？」 |
| **フィルタ出力** | 条件付き抽出 | 「筆頭論文だけ」「2023年以降の業績」「英語論文のみ」 |
| **フォーマット変換** | 特定の形式で出力 | 「科研費のフォーマットで」「バンクーバー方式で」 |
| **要約・統計** | 業績の概要 | 「論文数は？」「h-indexに使える情報は？」 |
| **業績追加・更新** | 新しい業績の登録 | 「この論文を追加して」「助成金情報を更新して」 |

### Step 2: データ参照

業績データは `references/achievements.md` に格納されている。
リクエストに応じて該当セクションを読み込む。

### Step 3: 出力生成

#### 筆頭著者（First Author）の判定

- 著者名 "Kosuke Kita" または "喜多 洸介" が先頭にある論文を筆頭論文とする
- 太字（**Kosuke Kita** / **喜多 洸介**）でマークされているものも筆頭

#### カテゴリ構成

業績は以下のカテゴリで構成:

1. **論文（Publications）** — 査読付き学術論文
2. **書籍（Books）** — 書籍・分担執筆
3. **学会発表（Presentations）** — 国際学会・国内学会（招待講演・一般口演）
4. **受賞歴（Awards）** — 学術賞・奨励賞
5. **助成金（Grants）** — 研究助成・競争的資金

#### 出力フォーマット

**デフォルト（Markdown）:**

```
## 論文
1. Kita K, et al. "Title". Journal. Year; Volume: Pages.
2. ...

## 受賞歴
1. 賞名（年）
...
```

**科研費（JSPS）様式:**
- 筆頭論文を先に、共著を後に記載
- 著者名はフルネーム
- 査読の有無を明記

**バンクーバー方式:**
- 著者6名まで全員記載、7名以上は最初の6名 + "et al."
- 出現順に番号付け

### Step 4: 業績更新

新しい業績を追加する場合:
1. `references/achievements.md` を読み込む
2. 該当カテゴリの適切な位置に追加
3. 番号を振り直す
4. ファイルを保存

## Examples

### Example 1: 筆頭論文の一覧

User says: 「筆頭論文の一覧を出して」

Actions:
1. `references/achievements.md` の論文セクションを参照
2. "Kosuke Kita" / "喜多 洸介" が先頭著者の論文を抽出
3. リスト形式で出力

### Example 2: 科研費の業績欄用

User says: 「科研費の業績欄に使えるフォーマットで論文を出力して」

Actions:
1. 筆頭論文と共著論文を分離
2. 各論文に査読の有無を付記
3. 科研費様式に整形して出力

### Example 3: 業績の追加

User says: 「新しい論文を追加して：[論文情報]」

Actions:
1. `references/achievements.md` を読み込む
2. 論文セクションの末尾に追加
3. 番号を更新して保存

### Example 4: 業績サマリー

User says: 「業績の概要を教えて」

Actions:
1. 全カテゴリのデータを集計
2. 論文数（筆頭/共著）、学会発表数、受賞数、助成金数を出力

## References

- `references/achievements.md` — 業績データの完全リスト
