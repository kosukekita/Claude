---
name: cv-profile
description: "喜多洸介（Kosuke Kita）の個人プロフィール（経歴＝学歴・職歴、および学術業績＝論文・書籍・学会発表・受賞歴・助成金）を一元管理・参照・出力するスキル。CV・履歴書・科研費書類の作成、業績リスト/経歴の照会・出力に対応。Use when user asks about this person's CV, curriculum vitae, résumé, career history, education, work experience, publications, academic achievements, grants, awards, or research output. Trigger phrases: CV, 履歴書, 略歴, プロフィール, curriculum vitae, résumé, 経歴, 学歴, 職歴, 所属, 勤務先, 出身大学, career, education, work experience, 業績, 業績一覧, 論文一覧, 発表履歴, 学会発表, 受賞歴, 助成金, 研究費, publications, achievements, research output, grants, awards."
---

# CV Profile

> 喜多洸介の経歴（学歴・職歴）と学術業績（論文・書籍・学会発表・受賞歴・助成金）を一元管理・参照・出力するスキル。CV・履歴書・科研費書類は経歴と業績を1ドキュメントに統合するため、両データを単一スキルで扱う。

## データソース

| ファイル | 内容 |
|---------|------|
| `references/career.md` | 経歴データ（学歴・職歴）の完全リスト |
| `references/achievements.md` | 業績データ（論文・書籍・学会発表・受賞歴・助成金）の完全リスト |

## Instructions

### Step 1: リクエスト分類

ユーザーのリクエストを以下のカテゴリに分類する。CVや履歴書・科研費など**経歴と業績の両方**を要するリクエストでは両データソースを参照する。

| カテゴリ | 内容 | 参照データ | 例 |
|---------|------|-----------|-----|
| **CV/履歴書 全体** | 経歴＋業績を1ドキュメントに統合 | career + achievements | 「CVを作成して」「履歴書形式で」「科研費の様式で全部」 |
| **経歴出力** | 学歴・職歴の出力 | career | 「経歴を教えて」「略歴を出力して」 |
| **学歴のみ / 職歴のみ** | 経歴の一部を抽出 | career | 「学歴は？」「出身大学は？」「現在の所属は？」 |
| **全業績出力** | 業績一覧の完全リスト | achievements | 「業績一覧を出力して」 |
| **カテゴリ別業績** | 特定カテゴリのみ抽出 | achievements | 「論文一覧を出して」「受賞歴は？」 |
| **フィルタ業績** | 条件付き抽出 | achievements | 「筆頭論文だけ」「2023年以降の業績」「英語論文のみ」 |
| **フォーマット変換** | 特定形式で出力 | 該当データ | 「バンクーバー方式で」「CV用に英語で」 |
| **要約・統計** | 概要・件数集計 | achievements (+career) | 「論文数は？」「h-indexに使える情報は？」 |
| **データ追加・更新** | 新規エントリの登録 | 該当データ | 「この論文を追加して」「新しい所属を追加して」 |

### Step 2: データ参照

リクエストに応じて該当データソースを読み込む。

- 経歴系 → `references/career.md`
- 業績系 → `references/achievements.md`
- CV・履歴書・科研費の統合書類 → **両方**を読み込む

### Step 3: 出力生成

経歴フォーマッタと業績フォーマッタは**排他ではなく加算**として共存する。CV等の統合書類では両方を順に適用する。

#### 3-A. 経歴（Career）

**デフォルト（Markdown 時系列）:**

```
## 学歴
- 2006年4月～2009年3月　洛南高等学校
- 2009年4月～2015年3月　大阪大学医学部医学科
- ...

## 職歴
- 2015年4月～2017年3月　大阪大学医学部附属病院　初期研修医
- ...
```

- **現在の所属**: 職歴から終了日が「～」（現在進行中）のエントリを抽出し、最新の所属を出力。
- **CV用（英語）**: Education と Work Experience に分け、新しい順（逆時系列）で出力。
- **科研費様式**: 研究者番号がある場合は付記。学歴・職歴を統合して時系列順に記載。

#### 3-B. 業績（Achievements）

**筆頭著者（First Author）の判定:**
- 著者名 "Kosuke Kita" または "喜多 洸介" が先頭にある論文を筆頭論文とする。
- 太字（**Kosuke Kita** / **喜多 洸介**）でマークされているものも筆頭。

**カテゴリ構成:**
1. **論文（Publications）** — 査読付き学術論文
2. **書籍（Books）** — 書籍・分担執筆
3. **学会発表（Presentations）** — 国際学会・国内学会（招待講演・一般口演）
4. **受賞歴（Awards）** — 学術賞・奨励賞
5. **助成金（Grants）** — 研究助成・競争的資金

**デフォルト（Markdown）:**

```
## 論文
1. Kita K, et al. "Title". Journal. Year; Volume: Pages.
2. ...

## 受賞歴
1. 賞名（年）
...
```

- **科研費（JSPS）様式**: 筆頭論文を先に、共著を後に記載。著者名はフルネーム。査読の有無を明記。
- **バンクーバー方式**: 著者6名まで全員記載、7名以上は最初の6名 + "et al."。出現順に番号付け。

#### 3-C. CV/履歴書 統合書類

経歴 → 業績の順で結合し、1ドキュメントとして出力する。典型構成:

```
# 履歴書 / Curriculum Vitae — 喜多 洸介

## 学歴
...
## 職歴
...
## 論文
...
## 学会発表
...
## 受賞歴
...
## 助成金
...
```

要求された様式（日本語履歴書 / 英語CV / 科研費）に応じて 3-A・3-B のフォーマッタを適用する。

### Step 4: データ追加・更新

**業績を追加する場合:**
1. `references/achievements.md` を読み込む。
2. 該当カテゴリの適切な位置に追加。
3. 番号を振り直して保存。

**経歴を追加する場合:**
1. `references/career.md` を読み込む。
2. 該当カテゴリ（学歴 or 職歴）の適切な位置に追加。
3. 時系列順を維持して保存。

## Examples

### Example 1: CV作成（統合）

User says: 「CVを作成して」

Actions:
1. `references/career.md` と `references/achievements.md` の両方を読み込む。
2. 経歴（学歴・職歴）→ 業績（論文・学会発表・受賞・助成金）の順で結合。
3. 1ドキュメントの CV として出力。

### Example 2: 現在の所属

User says: 「現在の所属は？」

Actions:
1. `references/career.md` の職歴から終了日が「～」のエントリを抽出。
2. 最新の所属を出力。

### Example 3: 筆頭論文の一覧

User says: 「筆頭論文の一覧を出して」

Actions:
1. `references/achievements.md` の論文セクションを参照。
2. "Kosuke Kita" / "喜多 洸介" が先頭著者の論文を抽出。
3. リスト形式で出力。

### Example 4: 科研費の業績欄用

User says: 「科研費の業績欄に使えるフォーマットで論文を出力して」

Actions:
1. 筆頭論文と共著論文を分離。
2. 各論文に査読の有無を付記。
3. 科研費様式に整形して出力。

### Example 5: 業績サマリー

User says: 「業績の概要を教えて」

Actions:
1. 全カテゴリのデータを集計。
2. 論文数（筆頭/共著）、学会発表数、受賞数、助成金数を出力。

### Example 6: データの追加

User says: 「新しい論文を追加して：[論文情報]」

Actions:
1. `references/achievements.md` を読み込む。
2. 論文セクションの末尾に追加。
3. 番号を更新して保存。

## References

- `references/career.md` — 経歴データの完全リスト
- `references/achievements.md` — 業績データの完全リスト
