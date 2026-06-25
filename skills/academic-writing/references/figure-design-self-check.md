# Figure 設計の自己チェック

> 「フォント 20pt + 凡例で略語定義」を超える図品質チェック。チャート種選択・禁則と修正・アクセシビリティ・VLM レンダリング検証・図表トレース（部分的エビデンス過大主張の視覚版）を一括で確認する。投稿前に各セクションのチェックリストを上から潰す。

本 reference は SKILL.md 本体の Figure 基本ルール（font >= 20pt、凡例で略語定義など）を前提に、その「上」のレイヤーを扱う。基本ルールは繰り返さない。

---

## (a) チャート種選択 — Chart Type Decision Tree

「何のデータで・何を問うか」から推奨チャートと **避けるべき(Avoid)** チャートを決める。原典の決定表をそのまま保持する。

| データ (Your Data) | 問い (Your Question) | 推奨 (Recommended) | 避ける (Avoid) |
|---|---|---|---|
| カテゴリ + 値 | 大小を比較 | **Bar chart**（縦/横） | **Pie chart** |
| カテゴリ + 値 + 群 | 群間で比較 | **Grouped bar** / **stacked bar** | **3D bar chart** |
| 連続変数, 1 群 | 分布を見る | **Histogram** + density curve | — |
| 連続変数, 2–5 群 | 分布を比較 | **Boxplot** / **violin plot** | **平均だけの Bar chart** |
| 連続変数 2 つ | 関係を見る | **Scatter plot** + regression line | — |
| 時系列 (1–5 系列) | トレンド | **Line chart** | 時系列の Bar chart |
| 時系列 (> 5 系列) | トレンド | **Small multiples**（faceted line） | **Spaghetti plot** |
| 相関行列 | 多変数関係 | **Heatmap** | Scatter plot matrix（密すぎ） |
| 効果量 + CI（メタ解析） | メタ解析を要約 | **Forest plot** | Bar chart |
| 効果量 + SE（メタ解析） | 出版バイアス確認 | **Funnel plot** | — |
| 概念 + 関係 | 理論枠組みを地図化 | **Network graph** / concept map | — |
| 合計 100% の割合 | 構成を見る | **Stacked bar chart** | **Pie chart** |
| 地理データ | 空間パターン | **Choropleth map** | — |

### 可視化しない判断（When NOT to Visualize）

次は図にせず本文 or 表へ回す。

- [ ] データ点が **3 未満** → 本文または表
- [ ] **単一の割合 or 平均** → 本文で一文で述べる
- [ ] チャートの説明に **2 文を超える** 解説が要る → 表にする
- [ ] すでに表にあるデータの **冗長な可視化** → 図にしない

---

## (b) 禁則と修正 — Critical / Subtle Errors

### 絶対やってはいけない（Critical Errors）

| 禁則 (Pitfall) | なぜ問題か | 修正 (Fix) |
|---|---|---|
| **Pie charts** | 人間は角度/面積の比較が苦手 | **Bar chart** へ |
| **3D charts** | 透視投影で値が歪む | **2D** にする |
| **Dual y-axes（二重 y 軸）** | 偽の相関を示唆し、スケール選択が恣意的 | **2 パネルに分ける** |
| **Rainbow colormap（虹色）** | 知覚的に非一様・色覚非対応 | **viridis / cividis** |
| **Truncated y-axis（原点省略・無表示）** | 小さな差を誇張する | **0 から開始** または break を明示 |
| **Missing error bars** | 不確実性を隠し、有意性を読者が評価できない | **SE / SD / 95% CI** バーを足す |
| **Chartjunk（装飾要素）** | data-ink 比を下げ、データから注意をそらす | 不要な要素を除去 |

### 見落としやすい（Subtle Errors）

| 禁則 | 問題 | 修正 |
|---|---|---|
| ヒストグラムの **不均等な bin 幅** | 頻度の知覚を歪める | 均等 bin にする |
| **重なるラベル** | 印刷サイズで読めない | 回転・略記・カテゴリ削減 |
| **8 色超の色数** | 印刷サイズで区別不能 | カテゴリをまとめる or facet |
| **データから遠い凡例** | 視線が往復する | プロット内に置く or 直接ラベル |
| **アスペクト比の歪み** | トレンドを誇張/縮小 | 既定 4:3、時系列は 16:9 |

---

## (c) アクセシビリティ — Accessibility Rules

- [ ] **色だけに依存しない** — shape / pattern / label を併用する
- [ ] **最小コントラスト比 3:1**（非テキスト要素の WCAG AA）
- [ ] 確定前に **色覚シミュレータ** で検証する
- [ ] **グレースケール印刷** でも pattern か label で群が区別できる
- [ ] **カテゴリパレットは約 8 色まで**

### 推奨パレット（具体 Hex）

- **連続/逐次データ**: viridis（知覚的に一様）。例: `#440154`(最暗) → `#277F8E` → `#FDE725`(最明)。
- **色覚（Deuteranopia/Protanopia）最優先**: cividis。例: `#00204D` → `#7B7463` → `#FFE945`。
- **カテゴリ（Tol's qualitative, 最大 8 色）**: Blue `#0077BB` / Cyan `#33BBEE` / Teal `#009988` / Orange `#EE7733` / Red `#CC3311` / Magenta `#EE3377` / Grey `#BBBBBB`（参照/NA） / Black `#000000`（外枠/文字）。
- **発散（相関/差分マップ）**: 負 `#2166AC` ↔ 0 `#F7F7F7` ↔ 正 `#B2182B`。

---

## (d) レンダリング検証（VLM）— 描画画像をデータと突合

図はコードレビューでは検出できない欠陥（ラベル切れ・テキスト重なり・誤った描画・誤解を招くスケール）を含みうる。**図生成後はコードではなく描画された画像** を元データと突合する。Multimodal LLM（vision 対応の Claude / GPT-4V 等）に画像 + 元データ + 下のチェックリストを渡し、各項目を pass/fail で返させる。

### 使いどころ

- **推奨**: 複雑なデータ（多パネル・多カテゴリ・統計プロット）
- **任意**: 単純な図（単一の bar / 基本 line）
- **必須**: パイプラインが `final-check` モード（Stage 4.5+）のとき
- **スキップ**: multimodal 能力が無いとき（graceful degradation）

### Verification Checklist

**Data Accuracy**
1. プロットした値が元データと **視覚的に一致** するか（"45%" のバーは軸範囲の約 45% を占めるべき）
2. **全データ系列が在る** か（欠けたカテゴリ/群が無い）
3. **error bar / CI のスケールが正しく** 見えるか

**APA 7.0 Compliance**
4. **両軸に descriptive なラベル + 単位** が付いているか
5. （多系列で）**凡例が在り読める** か
6. 図タイトルが正しい形式（bold label + italic title）か
7. **出版サイズでフォントが読める**（8pt 未満のテキストが無い）か

**Visual Quality**
8. テキストの **切れ・重なり・見切れ** が無いか
9. **色が区別可能**（視覚的に同一の 2 系列が無い）か
10. **chartjunk（3D 効果・不要な gridline）が無い** か

### Verification Loop（反復は最大 2 回 = 計 3 レンダー）

```
Step 1: 図コードを生成
Step 2: コードを実行して図画像をレンダー
Step 3: 画像 + 元データ + チェックリストを VLM へ
Step 4: VLM が各項目を pass/fail で返す
Step 5: いずれか FAIL なら:
  - VLM が具体的な問題を記述
  - コードを修正 → Step 2 に戻る（最大 2 反復）
Step 6: 全 PASS or 反復上限なら:
  - 検証結果を Figure Package に添付
  - 残った問題は caption の Note に明記
```

2 回修正しても問題が残るなら、ループを続けず **ユーザーレビューに回す**。

### Figure Package への追記（VLM 検証を走らせたとき）

```markdown
### VLM Verification
- Status: PASS / PASS_WITH_NOTES / NEEDS_REVIEW / SKIPPED
- Iterations: [N]（1 = 一発合格、SKIPPED なら N/A）
- Issues found: [見つかった問題]
- Issues fixed: [適用した修正]
- Remaining issues: [自動修正できず残った問題]
```

---

## (e) 部分的エビデンス過大主張の視覚版 — Figure/Table Trace

(d) の VLM チェックは *「描画が元データに忠実か」* だけを見る。それとは別の失敗がある: **図は完璧にレンダーされていても caption がデータ以上を主張する**、あるいは **原稿がその図表を、図表が支持しない主張のために引用する**。これは引用における partial-evidence trap（sub-claim 分解してから引用判断する）の **視覚版** であり、実装は別物として扱う。"見た目はプロフェッショナルでも無効な量的関係を含む図" がこの罠。

これを検査可能にするため、各 visual artifact（図 **または** 原稿の表）1 つにつき 1 エントリの **`figure_table_trace[]`** を Figure Package に持たせる。これは producer（visualization 担当）と consumer（integrity 検証担当）が読む **散文の契約** であり、機械検証スキーマではない（lint も JSON Schema も gold fixture も足さない）。

### Trace ブロック形式

```yaml
figure_table_trace:
  - artifact_id: "fig-3"               # 図番号 or 表 id、package 内で安定
    source_data:
      dataset_id: "abl-n128"           # 論理データセット名
      file: "results/abl_n128.csv"     # 生データへのパス/ポインタ
    transformation: {script: "scripts/plot_fig3.py", hash: "a1b2c3d"}
      # または精密な手動導出ポインタ、例:
      # transformation: "manual derivation: see §4.2 paragraph 2 (mean over 3 seeds, SE bars)"
    caption_claim: "Accuracy improves monotonically with N up to N=256."
    supported_manuscript_claims:                            # この図が引用される主張
      - claim: "Accuracy scales with model size up to N=256."   # 主張テキスト(+ 任意の locator)
        locator: "Results §4.2, ¶3"                              # 原稿のどこで主張するか
    limitations:
      - "Only N=128, 256, 512 tested; the monotonic claim between those points is interpolation."
```

### Field rules（フィールド規則）

1. **`source_data`** — 主張を担う artifact は必ず実在のデータセット/ファイルを指す。データ起源が未記述の図は **untraceable**。
2. **`transformation`** — `{script, hash}` の再現可能ペア **または** section/paragraph と操作を名指しした精密な手動導出ポインタのいずれか。`"computed manually"` / `"see paper"` のような曖昧値は不十分で、integrity gate は **untraceable** 扱いにする。
3. **`caption_claim`** — caption が下す解釈的主張。**複合**（"accuracy improves AND variance decreases"）でもよいが、integrity gate は判定前に atomic な sub-claim に分解する（#213 の分解を *散文ガイダンスとしてのみ* 借用。`PARTIAL` verdict も `sub_claim_breakdown[]` スキーマも import しない）。
4. **`supported_manuscript_claims`** — この artifact が引用される原稿側の主張。各々 **claim テキスト + 任意の原稿 locator**（section/paragraph）。bare な claim ID は使わない（`visualization_agent` は draft と `claim_intent_manifest` 生成前（図は Stage 2 で outline と並行生成、manifest は drafting 中に prose agents が出す）に走りうるため `(manifest_id, claim_id)` 参照が宙に浮く）。manifest が存在する場合（改訂段階の図など）はエントリに `manifest_id` + `claim_id` を **追加** してもよいが、常に得られる primary は text + locator。
   - **双方向チェック**: 列挙した各主張は実際に artifact を引用しているか（**forward**）、かつ原稿が artifact を使う **substantive** な箇所はすべて列挙済みの主張でカバーされているか（**reverse**）。著者が見せたい support だけ宣言しておきながら原稿が未列挙の主張で図に寄りかかる片側 trace は、reverse チェックが捕まえる omission。
   - **免除**: データについて何も主張しない incidental / 構造的 mention（"see Figure N for the architecture"、"results are summarized in Table N"、裸の "(Figure N)"）は対象外で、trace に水増ししてはならない。
5. **`limitations`** — scholar が知っている caveat（例 "N=3 trials; error bars are SE not SD"）。**agent は欠けた limitation を自動検出しない。** 空の `limitations: []` は黙ってパスにせず named advisory `[FIGURE-LIMITATIONS-EMPTY]` を上げる。**非空** の limitation が原稿に一度も現れないなら blocking issue（agent が知っていたのに原稿が落とした）。

**Required keys.** 6 キー全部（`artifact_id`, `source_data`, `transformation`, `caption_claim`, `supported_manuscript_claims`, `limitations`）が各エントリに必須。`limitations` は必須だが値は `[]` でよい（空-limitations advisory がなお発火）。いずれかのキー（`artifact_id` = 図↔trace のリンクキー含む）を **省いた** エントリは malformed で、claim-bearing artifact なら integrity gate が FAIL する。

**Tables.** 原稿の表に `figure_table_trace[]` エントリがあれば同じチェックを適用。trace の無い standalone 表は、不在をパス扱いせず trace-unavailable finding を上げる。

---

## References

- Song, Y. et al. (2026). PaperOrchestra. *arXiv:2604.05018*. — Section 4 Step 2（Plotting Agent with VLM critic）。
- Zhu, D. et al. (2026). PaperBanana: Automating academic illustration for AI scientists. *arXiv:2601.23265*. — Closed-loop VLM refinement system。
- Kong, L. et al. (2026). AI for Auto-Research: Roadmap & User Guide. *arXiv:2605.18661*. — §3.4（figure/table fidelity failures; trace layer の動機）。
