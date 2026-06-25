# 引用の実在検証（ハルシネーション参照の摘発）

> 投稿前に、捏造・ハルシネーション参照を機械的に摘発する手順。各参照を複数の書誌インデックスに照会してトライアンギュレーションし、タイトル類似度と DOI/ID クロスチェックで存在を確認する。**1 つのインデックスで未発見でも捏造の証拠にはならない**（未索引・新しい・非英語の可能性）。全インデックスで欠落して初めて捏造の証拠となる。

LLM が下書きを書くと、もっともらしいが実在しない参照（捏造 DOI・架空のジャーナル・著者と論文の取り違え）が紛れ込む。本リファレンスは、引用リストを投稿前に 1 件ずつ自動照会し、`VERIFIED / PLAUSIBLE / UNVERIFIABLE / FABRICATED` の verdict を付けて、捏造を投稿前に除去するためのもの。

---

## なぜ複数インデックスでトライアンギュレーションするのか

書誌インデックスはそれぞれ**ジャンル被覆（genre profile）が違う**。1 つに無くても別では当たることが多い。だから k 個のインデックスへ並行照会し、**全部で欠落したときだけ**「存在しない証拠」とみなす。一部のインデックスで当たれば「カバレッジ・ギャップ（未索引）」であって捏造ではない（例: S2 で未一致だが OpenAlex で一致 → high-coverage-gap evidence であって fabrication evidence ではない）。

| インデックス | API base | 得意ジャンル（被覆の特徴） |
|---|---|---|
| **Semantic Scholar (S2)** | `https://api.semanticscholar.org/graph/v1` | 汎用。Academic Graph で広く当たる。最初に回す Tier 0。 |
| **Crossref** | `https://api.crossref.org` | DOI 登録の正本（DOI registry of record）。**DOI 付きジャーナル論文に最強**。単行本・章は出版社の DOI 登録依存で部分的、会議録はまちまち。 |
| **OpenAlex** | `https://api.openalex.org` | OA 媒体・単行本（monograph）・**DOI を持たない業績**で S2 を補完。 |
| **arXiv** | `http://export.arxiv.org/api/query` | **CS / 物理 / 数学のプレプリント**で最強（arXiv ID を持つもの）。応答は JSON でなく **Atom 1.0 XML フィード**。 |
| **PubMed / PMC** | — | 医学・生命科学。S2/Crossref/OpenAlex/arXiv は biomedical を主目的としないため、医学引用はここで補う。 |

この被覆の非対称性は設計上の狙いで、4 インデックス（S2 + OpenAlex + Crossref + arXiv）を組み合わせると異なるジャンルプロファイルを捕捉できる。

---

## 共通マッチング規則（全インデックス共通）

1. **DOI / ID 照会を優先**。DOI（または arXiv ID）があれば exact lookup を最初に行う。無ければタイトル検索にフォールバックする。
2. **タイトル類似度の閾値は 0.70**。クエリのタイトルと各候補タイトルの類似度（Levenshtein / Python の `SequenceMatcher`）を計算し、**大小無視・約物（punctuation）除去で正規化**してから比較。類似度 **>= 0.70** のヒットのみ採用（PaperOrchestra の閾値に整合）。
3. **年が tiebreaker**。閾値を満たす候補が複数あるときは、年が一致する候補を優先（実装上は一致年に +0.05 のスコアボーナス）。次いで類似度最大、次いで DOI を持つ候補。
4. **DOI/ID クロスチェック**: DOI/ID が解決しても、返却タイトルが閾値 0.70 を下回るなら採用せず、タイトル検索へフォールスルーする（次節 `DOI_MISMATCH` 参照）。

### 照会パターン（インデックス別の具体）

**Semantic Scholar (S2)**
```
# タイトル検索（primary）
GET /paper/search?query={url_encoded_title}&limit=5&fields=title,authors,year,externalIds,venue,publicationDate
# DOI lookup（DOI があるとき）
GET /paper/DOI:{doi}?fields=title,authors,year,externalIds,venue,publicationDate,citationCount
# S2 ID 再照会
GET /paper/{paperId}?fields=title,authors,year,externalIds,venue,publicationDate,citationCount
```

**Crossref**（DOI は **`doi:` プレフィックス無し**でパスに入れる）
```
GET /works/{doi}                              # DOI lookup（title は言語バリアントの list、先頭を比較）
GET /works?query.title={url_encoded_title}&rows=5   # title search（年は issued.date-parts[0][0]）
```

**OpenAlex**（DOI は **`doi:` プレフィックス付き**）
```
GET /works/doi:{doi}?select=id,title,authorships,publication_year,doi,primary_location
GET /works?search={url_encoded_title}&per-page=5&select=id,title,authorships,publication_year,doi,primary_location
```

**arXiv**（応答は Atom XML。`<entry>` が 0 件＝ミス。404 ではない）
```
GET ?id_list={arxiv_id}                        # ID lookup（title は内部改行を単一スペースに畳んでから比較）
GET ?search_query=ti:"{title}"&max_results=5   # title search（年は <published> の先頭 4 桁）
```

### レート制限と作法

| インデックス | 制限 | polite pool / 備考 |
|---|---|---|
| S2 | 1 req/s（未認証）、10 req/s（API key 付き） | env `S2_API_KEY` 任意。30–80 件で未認証 30–80 秒、key 付き 3–8 秒。無料。 |
| Crossref | 10 req/s（polite）、~5 req/s（匿名） | User-Agent に **`mailto:`**（クエリ param ではなくヘッダ）。env `CROSSREF_POLITE_EMAIL`。 |
| OpenAlex | 10 req/s（polite, `mailto`）、1 req/s（匿名） | env `OPENALEX_POLITE_EMAIL`。 |
| arXiv | **~3 秒間隔**で投げる（固定 min-interval） | polite pool 機構なし。env なし。 |

**Degradation（落ちても止めない）**: HTTP 429 → 2 秒バックオフ、最大 3 回リトライ。HTTP 5xx / ネットワークタイムアウト（既定 30s）→ そのインデックスをスキップして他インデックスは独立に続行。**S2 等の API 障害でパイプラインをブロックしない**（graceful degradation）。あるインデックスが落ちたら、そのインデックスの `*_unmatched` 信号は「false」ではなく**省略**する（absent ≠ false）。

---

## 捏造の tell（ハルシネーション参照の赤旗）

以下のいずれかに当たれば即フラグ。

- [ ] **`DOI_MISMATCH`** — DOI（または arXiv ID）は解決するが、返却タイトルが参照タイトルに対し**類似度 < 0.70**。捏造 DOI が無関係な実在論文に解決する既知パターン（Compound Deception Pattern #5: DOI Misdirection）。arXiv 版は `ID_MISMATCH`。
- [ ] **未来の出版日** — publication date が将来。
- [ ] **不可能な巻号** — 例: 50 巻しか出ていないジャーナルの vol. 999。
- [ ] **その媒体に投稿歴のない著者** — 著者名が当該 venue のどの論文にも現れない。
- [ ] **存在しないジャーナル名** — Scopus / WoS / DOAJ のいずれにも索引されない。
- [ ] **不正な DOI 形式** — `10.xxxx/...` パターンに合致しない。
- [ ] **caveat 皆無で都合よく完璧一致** — 主張をきれいに支持しすぎて留保（caveat）が一切ない（suspiciously perfect）出典。

---

## Verdict（検証アウトカム）

| Verdict | 条件 | 扱い |
|---|---|---|
| **VERIFIED** | DOI/ID が解決し、メタデータ（タイトル類似度 >= 0.70・著者・年）が一致。または S2 API でマッチ（最も強い機械的証拠）。 | 採用。 |
| **PLAUSIBLE** | DOI は無いが、WebSearch 等の web 確認で存在・媒体・年が確認できた。 | 採用（留保付き可）。 |
| **UNVERIFIABLE** | どの方法でも存在を確認できない。 | **人手レビューへ回す**（自動除外しない）。 |
| **FABRICATED** | 全インデックス・全 tier が失敗し、非存在の証拠が揃った。 | **CRITICAL。必ず削除する。** |

照会順序の目安: Tier 0（S2 等の API 照会、100% 被覆）→ パスした参照は WebSearch スポットチェックを省略可。**FAIL したものだけ** DOI 解決と WebSearch（人手調査）へ送る。

---

## 最重要原則: 単一インデックスの欠落 ≠ 捏造

- **1 つのインデックスで未発見（例 `S2_NOT_FOUND`）は、それ単体では捏造の証拠ではない。** その論文は実在するが、そのインデックスに索引されていないだけかもしれない（very recent / 非英語 / グレーリテラチャ / OA 外）。
- arXiv は**適用が ID-gated**。arXiv ID を持たない引用は arXiv では `skipped`（`unmatched` ではない）。ジャーナル論文が arXiv に当たらないのはカバレッジ・ギャップであって非存在の証拠ではないので、トライアンギュレーション信号を出してはならない。逆に、**ID を持つのに ID が解決しない**引用は積極的な非存在の証拠になる。
- **全インデックスで欠落して初めて**、`FABRICATED` の証拠として扱う。それまでは `UNVERIFIABLE` として人手に委ねる。

### NG / OK 例

**NG**（単一インデックスの欠落で即・捏造扱い）
> S2 で見つからなかったので、この 2026 年の非英語論文を捏造（FABRICATED）として削除した。

**OK**（トライアンギュレーション後に判定）
> S2 で `S2_NOT_FOUND`。OpenAlex のタイトル検索で類似度 0.93・年一致でヒット → カバレッジ・ギャップ。verdict は **VERIFIED**（誤って削除しない）。

**NG**（DOI が解決したから無条件採用）
> DOI が doi.org で 200 を返したので VERIFIED とした。

**OK**（DOI クロスチェックを通す）
> DOI は解決したが返却タイトルの類似度が 0.41 → `DOI_MISMATCH`。タイトル検索にフォールスルーしても閾値超えのヒット無し → **FABRICATED**、削除。

---

## 投稿前チェックリスト

- [ ] 参照ごとに DOI/arXiv ID があれば exact lookup、無ければタイトル検索を実行した
- [ ] タイトル類似度を大小無視・約物除去で正規化し、**>= 0.70** のヒットのみ採用した（年で tiebreak）
- [ ] DOI/ID が解決した参照すべてに 0.70 のタイトルクロスチェックをかけ、`DOI_MISMATCH` を検出した
- [ ] S2 / Crossref / OpenAlex / arXiv（医学は PubMed/PMC）でトライアンギュレーションした
- [ ] 単一インデックスの欠落だけで捏造判定していない（全欠落のみ FABRICATED）
- [ ] 各参照に `VERIFIED / PLAUSIBLE / UNVERIFIABLE / FABRICATED` の verdict を付けた
- [ ] `FABRICATED` は本文・引用リストから削除し、`UNVERIFIABLE` は人手レビューへ回した
- [ ] レート制限（arXiv ~3s、他は polite pool）を守り、API 障害時は当該信号を省略（absent ≠ false）した

---

## References

- Semantic Scholar API: https://api.semanticscholar.org/ （API key 取得: https://www.semanticscholar.org/product/api#api-key ）
- Crossref API: https://api.crossref.org
- OpenAlex API: https://api.openalex.org
- arXiv API（利用規約・pacing）: https://info.arxiv.org/help/api/tou.html
