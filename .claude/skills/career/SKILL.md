---
name: career
description: >
  喜多洸介（Kosuke Kita）の経歴（学歴・職歴）を管理・参照・出力するスキル。
  CV作成、経歴照会、履歴書フォーマットでの出力に対応。
  Use when user asks about career history, education, work experience,
  or curriculum vitae background.
  Trigger phrases: "経歴", "学歴", "職歴", "履歴", "略歴", "プロフィール",
  "career", "education", "work experience", "background", "履歴書",
  "所属", "勤務先", "出身大学".
---

# Career

> 喜多洸介の経歴（学歴・職歴）を管理・参照・出力するスキル。

## Instructions

### Step 1: リクエスト分類

ユーザーのリクエストを以下のカテゴリに分類:

| カテゴリ | 内容 | 例 |
|---------|------|-----|
| **全経歴出力** | 学歴・職歴の完全リスト | 「経歴を教えて」「略歴を出力して」 |
| **学歴のみ** | 学歴部分を抽出 | 「学歴は？」「出身大学は？」 |
| **職歴のみ** | 職歴部分を抽出 | 「職歴は？」「現在の所属は？」 |
| **フォーマット変換** | 特定の形式で出力 | 「履歴書形式で」「CV用に英語で」 |
| **経歴更新** | 新しい経歴の追加 | 「新しい所属を追加して」 |

### Step 2: データ参照

経歴データは `references/career.md` に格納されている。
リクエストに応じて該当セクションを読み込む。

### Step 3: 出力生成

#### 出力フォーマット

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

**CV用（英語）:**
- Education と Work Experience に分けて記載
- 新しい順（逆時系列）で出力

**科研費様式:**
- 研究者番号がある場合は付記
- 学歴・職歴を統合して時系列順に記載

### Step 4: 経歴更新

新しい経歴を追加する場合:
1. `references/career.md` を読み込む
2. 該当カテゴリ（学歴 or 職歴）の適切な位置に追加
3. 時系列順を維持して保存

## Examples

### Example 1: 経歴の一覧

User says: 「経歴を教えて」

Actions:
1. `references/career.md` を参照
2. 学歴・職歴を時系列順で出力

### Example 2: CV用の英語経歴

User says: 「CVに使う英語の経歴を出して」

Actions:
1. `references/career.md` を参照
2. Education / Work Experience に分けて英語で逆時系列出力

### Example 3: 現在の所属

User says: 「現在の所属は？」

Actions:
1. `references/career.md` の職歴から終了日が「～」（現在進行中）のエントリを抽出
2. 最新の所属を出力

## References

- `references/career.md` — 経歴データの完全リスト
