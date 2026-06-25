# 引用‑主張の忠実性監査（存在≠支持）

> 各定量・事実主張について「引用文献が実在するか」ではなく「その文献が当該主張を実際に支持しているか」を独立に監査するプロトコル。reference existence は必要条件であって十分条件ではない。

## このプロトコルが解く問題

参考文献リストの検証（その文献が実在し、メタデータが正しいか）と、主張の忠実性検証（**その文献が、原稿が言っている内容を実際に述べているか**）は別物である。前者を通過しても後者で落ちる。よくある崩れ方は次の3つ:

- ソースは実在するが、主張した数値・記述がそのソースに**書かれていない**（`UNVERIFIABLE`）。
- ソースは正しいが、原稿が結論を**強めすぎている**（ソースは "suggests" なのに原稿は "shows" = `synthesis_overclaim`）。
- ソースは狭い検証データセットの話なのに、原稿が**広い deployment 推奨**に一般化している。

監査者の責務は「judge する（証拠に紐づいた verdict を出す）」ことであって「arbitrate する（合否を決める）」ことではない。合否は下流の formatter / 投稿前チェックが verdict 集計から機械的に判定する。

---

## 手順 E1〜E3: 主張のレジストリ化と照合

### E1 — Claim Extraction（主張の抽出とレジストリ化）

原稿全体を走査し、すべての定量・事実主張を拾う。対象スコープ:

- すべての数値主張（percentages, counts, effect sizes, p-values）
- すべての categorical assertion（"X is the largest…", "Y was the first to…"）
- すべての trend claim（"increasing", "declining", "stable"）
- すべての causal claim（"X causes Y", "X leads to Y"）

各主張について次を記録し **Claim Registry** テーブルにする: claim text / cited source(s) / paper section / page・line。所在（ページ・表番号・図番号・引用文）を一緒に記録するのが要点で、これが無いと E2 の anchor 照合ができない。

### E2 — Source Tracing（ソース追跡）

各主張について、引用ソース内の**それを支持する具体的な passage** を特定する。WebSearch + DOI lookup で原典を見つける。ソースが paywall の場合は `UNVERIFIABLE_ACCESS` として記録（合否はブロックしない）。

### E3 — Cross-Referencing（突き合わせ）

claim text と source text を比較。照合項目: exact numbers / date ranges / population descriptions / methodology descriptions。乖離はすべて flag する。

---

## 照合する6次元

主張ごとに、以下の6次元すべてを通す。Pass / Fail 条件は次のとおり。

| Check | 求める証拠 | Pass condition | Fail condition |
|---|---|---|---|
| **Reference existence** | DOI, PMID, arXiv ID, trial registry ID, または title‑author‑year で解決可能 | 外部インデックスか出版社ページで解決する | 解決できない、またはメタデータが矛盾する |
| **Claim anchor** | page, section, table, figure, または短い引用文 | ソースがその具体的な数値・記述を**実際に含む**（所在が特定できる） | ソースは存在するが、主張された証拠を含まない |
| **Population match** | study population と setting | 原稿の主張がソースの研究集団・設定に一致 | 狭い／異なる集団からの一般化に拡大している |
| **Outcome match** | sensitivity, specificity, effect size, endpoint, または定性的所見 | 同一の endpoint・指標定義を使っている | endpoint・timeframe・comparator・metric をすり替えている |
| **Strength of conclusion** | ソースの結論と限界 | 不確実性・限界を保存している | "may" / "in this dataset" / "needs validation" を広い deployment advice に強化している |
| **Clinical boundary** | human review と intended use | 出力を research・evidence synthesis・tool evaluation として枠付け | 患者個別の diagnosis・treatment・triage・deployment instruction になっている |

### 次元 (4) Outcome match の注意 — 指標すり替えの検出 tell

`sensitivity` ↔ `specificity` の取り違え、endpoint のすり替え（例: 主要評価項目を別の副次項目にこっそり置き換える）、比較対照や観察期間の差し替えは、この次元で機械的に検出する。「同一エンドポイント・同一期間・同一比較対照・同一指標定義か」を逐一突き合わせる。

### 次元 (5) Strength of conclusion の注意 — synthesis_overclaim

ソースが `suggests` なのに原稿が `shows` と書く、ソースが "in this dataset" と限定しているのに原稿が無条件の一般則にする、これが代表的な `synthesis_overclaim`。ソースの内容自体は正しいのに、原稿が結論強度を上げている点が defect。

---

## Verdict ladder（主張ごとの判定）

| Verdict | 定義 | Severity | 例 |
|---|---|---|---|
| **VERIFIED** | 主張がソースと完全一致、または丸めの範囲（rounding tolerance）で一致 | None | Paper: "15.2%"; Source: "15.2%" |
| **MINOR_DISTORTION** | 言い換えだが意味は保存されている | MINOR | Paper: "about 15%"; Source: "15.2%" |
| **MAJOR_DISTORTION** | 単純化しすぎ・誇張・誤表現 | SERIOUS | Paper: "declined **sharply**"; Source: "declined by **2.1%**" |
| **UNVERIFIABLE** | ソースに当該情報が無い | SERIOUS | Paper が Smith (2020) を引くが、Smith (2020) はそのトピックを論じていない |
| **UNVERIFIABLE_ACCESS** | ソースは存在するが、全文にアクセスできず検証不能 | MEDIUM | Paywall の論文 |

---

## Defect stage 語彙（失敗の発生段階を分類）

verdict が SUPPORTED 以外のとき、失敗がどの段階で起きたかを次の語彙で分類する。分類には、retrieved excerpt 内の**その分類を駆動した具体的なテキスト断片を必ず引用**する（「ソースが X と言っている」を引用なしで捏造しない）。

| Defect stage | 意味 |
|---|---|
| `source_description` | ソースが、主張が断言するのとは**異なる集団・方法論**を記述している |
| `citation_anchor` | ソースの内容は正しいが、引用された anchor（page/section/quote）が**間違った passage** を指している |
| `synthesis_overclaim` | ソースの内容は正しいが、原稿が結論を**強めすぎ**ている（例: "suggests" を "shows" にする） |
| `metadata` | reference は存在するが author/year/title が誤り（retrieval の受け渡し時に検出） |

PARTIAL（ソースが一部の sub-claim だけを支持し、他は支持しない）の場合は `judgment=UNSUPPORTED, defect_stage=source_description` に正規化したうえで sub-claim ごとの内訳（どれが SUPPORTED でどれが UNSUPPORTED か）を残す。部分支持を「完全解決」として黙って受け入れないため、未支持の sub-claim を未支持主張と同じゲートに通す。

---

## Pass / Fail 規則

| 判定 | 条件 |
|---|---|
| **PASS** | `MAJOR_DISTORTION = 0` **かつ** `UNVERIFIABLE = 0` |
| **FAIL** | `MAJOR_DISTORTION` または `UNVERIFIABLE` が1つでもある |
| **PASS_WITH_NOTES** | `MINOR_DISTORTION` と `UNVERIFIABLE_ACCESS` のみ（MAJOR/UNVERIFIABLE はゼロ） |

`UNVERIFIABLE_ACCESS`（paywall）は記録するが PASS をブロックしない。`MINOR_DISTORTION` も同様にブロックしない。ブロックするのは `MAJOR_DISTORTION` と `UNVERIFIABLE` の2つだけ。

---

## Sampling（検証する主張の割合）

| モード | サンプリング |
|---|---|
| **事前パス（pre-review）** | 主張の **30% をランダム抽出（最低10件）** |
| **最終チェック（final-check）** | **100% の主張** |

事前パスは全数でなくてよいが、最低10件は保証する。最終チェックでは全主張を監査する。

---

## 安全な書き換えパターン（NG → OK）

### ケース1: 引用が未検証 / 検証不能

数値や推奨をそのまま書かず、evidence status を明示して保留する。

**NG（検証前に数値と推奨を断言）:**
> AI-assisted retinal image screening achieved 99% sensitivity and 98% specificity for diabetic retinopathy detection and should be deployed broadly in primary care.

**OK（evidence status を明示し、検証されるまで数値・推奨を出さない）:**
> Evidence status: unverified. The draft claims diagnostic performance for AI-assisted diabetic retinopathy screening, but the cited source has not been resolved and no source-text anchor is available. Do not report the sensitivity, specificity, or deployment recommendation until the reference is externally resolved and the exact supporting passage is located.

### ケース2: 引用は実在するが、狭い設定のみを支持

広い一般化に拡大せず、ソースが支持する範囲に限定し、broad deployment readiness はそれ単独では確立しないと明記する。

**OK:**
> In the cited validation dataset, the AI-assisted retinal image system reported [metric] for [population/setting]. This does not by itself establish broad primary-care deployment readiness; additional external validation, workflow evaluation, and qualified clinical review are required.

---

## Output Format

### Claim Verification Report

| # | Claim | Source | Section | Verdict | Detail |
|---|-------|--------|---------|---------|--------|
| 1 | [claim text] | [source] | [section] | VERIFIED | Exact match |
| 2 | [claim text] | [source] | [section] | MAJOR_DISTORTION | Paper says X, source says Y |

### Summary

- Total claims checked: [N]
- VERIFIED: [N]
- MINOR_DISTORTION: [N]
- MAJOR_DISTORTION: [N] （PASS には 0 が必須）
- UNVERIFIABLE: [N] （PASS には 0 が必須）
- UNVERIFIABLE_ACCESS: [N] （記録のみ。PASS をブロックしない）

### 主張単位の監査テンプレート（臨床主張向け）

```markdown
## Clinical Citation Verification

### Claim Under Review
- Claim:
- Citation key:
- Paper section:

### Deterministic Lookup
- DOI / PMID / registry ID:
- External lookup result:
- Metadata match:

### Source Anchor
- Page / section / table / figure:
- Supporting passage:
- Anchor status:

### Claim-to-Source Match
- Population:
- Outcome:
- Metric:
- Limitation preserved:

### Verdict
- VERIFIED / MINOR_DISTORTION / MAJOR_DISTORTION / UNVERIFIABLE / UNVERIFIABLE_ACCESS:
- Rationale:

### Clinical Safety Note
- This is research, evidence synthesis, or documentation support only.
  It is not patient-specific diagnosis, treatment, triage, or clinical decision support.
```

### 監査結果の記録例（未検証ケース）

| Field | Result |
|---|---|
| Claim | AI-assisted retinal image screening achieved 99% sensitivity and 98% specificity and should be deployed broadly in primary care. |
| Citation status | `existence_unverified` |
| Anchor status | `anchor_missing` |
| Support status | `unsupported_until_verified` |
| Clinical safety status | `overclaim_risk` |
| Required next step | Resolve the citation externally, then locate the exact source passage or table supporting both metrics. |

---

## 適用のコツ

- **存在 ≠ 支持**: reference existence は必要条件にすぎない。anchor（所在）まで特定できて初めて支持を主張できる。
- **anchor を引用で残す**: 「ソースが言っている」を retrieved text の引用なしで書かない。defect_stage 分類にも、それを駆動した具体的テキスト断片を添える。
- **臨床境界を超えない**: 出力は research・evidence synthesis・tool evaluation の枠内に保ち、患者個別の診断・治療・トリアージ指示にしない。
