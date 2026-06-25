# CRediT 14役割＋ICMJE 著者4要件＋AI著者方針

> 誰を著者にし誰を謝辞に回すか、各著者の貢献をどう CRediT で整形するか、AI ツールをどう開示・引用するか。`著者名・所属の整形` が扱わない「著者資格・貢献記述」の機構をまとめる。

CRediT（Contributor Roles Taxonomy）は CASRAI と NISO が 2015 年に共同策定した著者貢献の標準タクソノミー。現在 Elsevier・Springer Nature・Wiley・Taylor & Francis・PLOS など 50 以上の主要出版社が採用している。CRediT は **14 の貢献役割**を定義し、各著者は 1 つ以上の役割を割り当てられ、各役割は 1 人以上の著者が担いうる。

---

## CRediT 14 Contribution Roles（全列挙＋定義）

各役割の英語名はそのまま残す（投稿システムのチェックボックスや誌面表記がこの綴りで固定されているため）。「–」（en dash）を含む 2 つの Writing 役割は綴りに注意。

| # | Role（英語表記固定） | Definition（要旨） |
|---|---|---|
| 1 | **Conceptualization** | Ideas; 研究の包括的なゴール・狙いの定式化や発展。 |
| 2 | **Data curation** | メタデータ作成・データのクレンジング・研究データ（データ解釈に必要なソフトコードを含む）の初期利用と再利用に向けた維持管理。 |
| 3 | **Formal analysis** | 統計的・数理的・計算的その他の formal な手法を適用してデータを解析・統合すること。 |
| 4 | **Funding acquisition** | この出版に至るプロジェクトへの財政的支援の獲得。 |
| 5 | **Investigation** | 研究・調査プロセスの遂行、特に実験の実施やデータ／エビデンスの収集。 |
| 6 | **Methodology** | 方法論の開発・設計；モデルの作成。 |
| 7 | **Project administration** | 研究活動の計画・実行に対する管理・調整の責任。 |
| 8 | **Resources** | 試料・試薬・材料・患者・検体・動物・機器・計算資源・その他解析ツールの提供。 |
| 9 | **Software** | プログラミング・ソフト開発；プログラム設計；コードとアルゴリズムの実装；既存コード部品のテスト。 |
| 10 | **Supervision** | 研究活動の計画・実行に対する監督・統率の責任（コアチーム外へのメンタリングを含む）。 |
| 11 | **Validation** | 結果・実験・その他の研究成果の再現性／再現可能性の検証（活動の一部としてでも別個にでも）。 |
| 12 | **Visualization** | 公表物の準備・作成・提示、特に可視化／データ提示。 |
| 13 | **Writing – Original Draft** | 公表物の準備・作成・提示、特に初稿の執筆（実質的な翻訳を含む）。 |
| 14 | **Writing – Review & Editing** | 元の研究グループのメンバーによる公表物の準備・作成・提示、特に批判的レビュー・コメント・改訂（出版前後の段階を含む）。 |

### 医学・研究文脈での割当て例（役割の判定に迷ったとき）

- Conceptualization … リサーチクエスチョンの設定・研究フレームワークの設計
- Data curation … 生データのクレンジング、欠損値・外れ値の処理、メタデータ対応表の構築
- Formal analysis … SEM・DEA・テキストマイニング等の統計／計算解析の実行
- Funding acquisition … 競争的研究費（科研費等）の申請・獲得
- Investigation … サーベイ実施・インタビュー・記録の収集
- Methodology … 混合研究デザインの設計、評価ツール・指標体系の開発
- Project administration … 多施設チームの進捗調整、複数年グラントの段階的成果管理
- Resources … データベースアクセス権・データ利用許諾・高性能計算資源の提供
- Software … 解析コード（Python/R）の記述、ダッシュボードや NLP システムの構築
- Supervision … 大学院生の指導、PI として研究品質を監督、方法論的助言
- Validation … 感度分析でのロバストネス検証、トライアンギュレーション、データソース間の整合確認
- Visualization … トレンド図・概念モデル図・ヒートマップの作成
- Writing – Original Draft … 初稿全体や特定章（literature review / methodology 等）の執筆、初稿の英訳
- Writing – Review & Editing … 共著者初稿のレビュー・改訂、査読コメント対応、最終版の校正

---

## ICMJE Authorship Criteria（著者4要件・全て満たす必要）

International Committee of Medical Journal Editors（ICMJE）の著者基準は医学に限らず全分野で広く参照される。著者として記載するには **4 条件すべて**を満たす必要がある（どれか 1 つでも欠ければ著者ではなく謝辞へ）。

| # | Condition | Description |
|---|---|---|
| 1 | **Substantial contributions** | 構想・デザインへの実質的貢献；または データの取得・解析・解釈への実質的貢献 |
| 2 | **Drafting or revising** | 原稿の起草への参加；または 重要な知的内容に関わる批判的改訂 |
| 3 | **Final approval** | 投稿する最終版の承認 |
| 4 | **Accountability** | 研究全体への accountability（任意の部分の正確性・integrity に関する疑義が適切に調査・解決されることを保証することへの同意） |

---

## 著者／謝辞の境界（Authorship vs Acknowledgments）

以下の貢献は**通常それ単独では著者資格を満たさない**。Acknowledgments に記載する。

- 資金提供のみ（研究そのものへの関与なし） — Providing funding support only
- 管理／資源の提供のみ — Providing administrative support or resources only
- 言語編集／翻訳のみ — Language editing or translation only
- データ入力／転記のみ — Data entry or transcription only
- 研究に実際は関与していない部門長 — Serving as a department head only (without actual research involvement)

### 判定対照表（List as Author ↔ List in Acknowledgments）

| List as Author | List in Acknowledgments |
|---|---|
| 研究フレームワークを設計した | 管理的サポートを提供した |
| 原稿を執筆または実質的に改訂した | 言語編集／翻訳 |
| データ解析を実施した | データ入力／転記 |
| 研究費を獲得し **かつ** 研究に参加した | 研究に関与せず資金提供のみ |
| 研究方法論を設計した | 実験室／機器を提供した |
| 研究を監督し学術的指導を提供した | 管理上の長を務めただけ |

> tell: 「資金は取ったが研究には関わっていない」「機器/データだけ貸した」「英文校正だけ」「データ入力だけ」は著者落ち。逆に「funding acquisition AND 研究参加」の両方があれば著者になりうる。

### Acknowledgments セクション例（テンプレ英文）

```
The authors would like to thank [Name] from [Institution] for administrative
support, [Name] for language editing, and the anonymous reviewers for their
constructive feedback. This study was conducted with the support of the
[Funding body].
```

---

## 貢献の整形：Author × Role マトリクス

各著者の貢献は「貢献文」または「著者×役割マトリクス」で整形する。マトリクスは **Lead / Supporting / –** の 3 値でラベリングする。

| Role | Author A (Corresponding) | Author B | Author C |
|---|:---:|:---:|:---:|
| Conceptualization | Lead | Supporting | – |
| Data curation | – | Lead | Supporting |
| Formal analysis | Supporting | Lead | – |
| Funding acquisition | Lead | – | – |
| Investigation | Supporting | Lead | Lead |
| Methodology | Lead | Supporting | – |
| Project administration | Lead | – | – |
| Resources | Lead | – | – |
| Software | – | Lead | – |
| Supervision | Lead | – | – |
| Validation | Supporting | Supporting | Lead |
| Visualization | – | Lead | Supporting |
| Writing – original draft | Lead | Supporting | – |
| Writing – review & editing | Lead | Supporting | Supporting |

- **Lead**: その貢献に主たる責任を負う（Primarily responsible）
- **Supporting**: 補助的・補完的役割（Assisting or auxiliary）
- **–**: 関与せず（Did not participate）

---

## CRediT Statement テンプレート（貢献文形式）

**Author Contributions Statement**:

```
[Author A]: Conceptualization, Methodology, Funding acquisition,
Writing – original draft, Supervision, Project administration.
[Author B]: Data curation, Formal analysis, Software, Visualization,
Writing – original draft, Writing – review & editing.
[Author C]: Investigation, Validation, Writing – review & editing.
```

---

## ジャーナルごとの CRediT 要件（記載場所の判断）

CRediT が必須か任意か、誌面のどこに書くかは出版社で異なる。投稿前に投稿先の要件を確認する。

| Journal/Publisher | CRediT Requirement | Format |
|---|---|---|
| Most **Elsevier** journals | Mandatory | 投稿システムで役割を選択 |
| **PLOS ONE** | Mandatory | 本文中に記載 |
| Some **Springer Nature** journals | Encouraged | 本文中に記載 |
| Some **Wiley** journals | Encouraged | 本文中の文章または表 |
| All **MDPI** journals | Mandatory | 原稿末尾の専用セクション |
| Some **Taylor & Francis** journals | Encouraged | 本文中に記載 |

---

## AI 著者方針（AI は著者にしない／開示と引用）

### 主要出版社・団体のスタンス

| Organization/Publisher | Policy Summary | Effective |
|---|---|---|
| **ICMJE** | AI ツールは著者4要件を満たさない（accountability 不可・承認不可）。著者として記載してはならない | 2023 |
| **APA** | AI を著者にしない。AI 利用は Methods か Acknowledgments で開示 | 2023 |
| **Nature/Springer Nature** | LLM を著者にしない。Methods か Acknowledgments で利用を開示 | 2023 |
| **Science/AAAS** | AI 生成テキストをオリジナルの成果として提示してはならない。AI 利用を開示 | 2023 |
| **Elsevier** | AI ツールを著者にしない。原稿中で開示 | 2023 |
| **Wiley** | AI を著者にしない。Acknowledgments で利用を記述 | 2023 |
| **Taylor & Francis** | AI を著者にしない。投稿時に AI 利用を開示 | 2023 |
| **IEEE** | AI を著者・共著者にしてはならない | 2023 |

### AI 開示のベストプラクティス

1. **Methods か Acknowledgments に明記** — どの AI ツールを、どう使ったかを具体的に記す。
2. **著者が全責任を負う** — AI 支援で得たすべての出力内容について著者が full responsibility を持つ。
3. **AI 生成テキストをオリジナルの研究知見として直接提示しない**。
4. **AI ツールは著者ではなく引用で扱う**。APA 7th 形式の推奨フォーマット:

```
OpenAI. (2024). ChatGPT (Version GPT-4) [Large language model]. https://chat.openai.com/
```

> tell: AI を著者欄や ORCID に載せている／AI 利用を一切開示していない／AI 出力を一次的な研究結果としてそのまま提示している、はいずれも主要誌でリジェクト要因。AI は「著者欄」ではなく「Methods/Acknowledgments での開示」＋「引用」で処理する。

---

## References

- CRediT official taxonomy: https://credit.niso.org/
- ICMJE authorship criteria: https://www.icmje.org/recommendations/browse/roles-and-responsibilities/defining-the-role-of-authors-and-contributors.html
- APA AI policy: https://www.apa.org/pubs/journals/resources/ai-policy
- Nature AI policy: https://www.nature.com/nature-portfolio/editorial-policies/ai
