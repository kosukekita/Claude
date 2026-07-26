---
type: reference
title: 学術API 実測レシピ（deep-research-pro）
description: OpenAlex/PubMed/Europe PMC/Crossref/arXiv の到達性・撤回判定・全文取得・ペイウォール回避を、このマシンで実測して確定させた手順
---

# 学術API — 実測済みレシピ

すべて 2026-07-26 にこのマシンから実際に叩いて確認したもの。**キー不要**。

## なぜ web 検索より先に叩くのか

web 検索が返すのは、多くの場合その分野の**派生的なコメンタリー**（ニュース記事・ブログ・
まとめサイト）。学術APIは**被引用数で並んだ正典**を返す。二次記事は数値を丸め、
但し書きを落とし、方法の限界を消す。レポートの価値はまさにそこにある。

研究文献のある主題では、**必ず学術APIを先に叩く。**

## 到達性（実測）

| API | 状態 | 用途 |
|---|---|---|
| OpenAlex | 到達可 | **第一候補。** 被引用数・撤回フラグ・OA状況が1回で取れる |
| PubMed E-utilities | 到達可 | 生物医学。MeSH による正規化が強い |
| Europe PMC | 到達可 | **全文の可否が分かる**（ペイウォール回避の要） |
| Crossref | 到達可 | DOI メタデータ・撤回/訂正の追跡 |
| arXiv | 到達可 | プレプリント（CS/物理/数学） |
| Semantic Scholar | **429（レート制限）** | キー無しでは信頼できない。**必須経路にしない** |

Semantic Scholar は落ちる前提で設計する。同じ情報は OpenAlex から取れる。

## OpenAlex — 第一候補

`select=` で必要な欄だけ取ると軽い。`mailto=` を付けると優先度が上がる（polite pool）。

```bash
curl -s "https://api.openalex.org/works?search=<クエリ>&per-page=25&mailto=<メール>&select=id,doi,title,publication_year,cited_by_count,is_retracted,primary_location,open_access"
```

**`is_retracted` が直接返る。**これが撤回判定の第一手。実測で `false` が正しく返ることを確認済み。
`cited_by_count` が被引用数。`open_access` に OA 状況と、あれば全文URL。

## 撤回の判定（3経路・どれか1つでも当たれば撤回扱い）

撤回論文が結論を支えていると、レポート全体が崩れる。**出荷前に必ず洗い直す**
（キャッシュではなく、その場で。昨日出た撤回は今日捕まえる必要がある）。

1. **OpenAlex**: 上の `is_retracted` フィールド
2. **PubMed**: 出版種別で絞る
   ```bash
   curl -s 'https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi?db=pubmed&term=%22Retracted+Publication%22%5BPublication+Type%5D+AND+<主題>&retmode=json'
   ```
   実測で件数が返ることを確認済み。
3. **Crossref**: DOI を直接引き、`update-to` を見る
   ```bash
   curl -s "https://api.crossref.org/works/<DOI>?mailto=<メール>"
   ```
   `update-to` に撤回・訂正・懸念表明の関係が入る（無ければ `null`）。

撤回が見つかったソースは品質を床値に落とす。**撤回を明記せずに引用したまま出荷しようとすると
出荷ゲートが落ちる**（明記した上で「この主張は撤回された」と論じるのは正当）。

## ペイウォールで止まらない（実測で最多の失敗）

RED 実測では、3体中3体がペイウォールで探索を打ち切り「抄録＋業界紙で代用」した。
代用してはいけない。順に試す:

### 1. Europe PMC で全文の有無を確認する

```bash
curl -s "https://www.ebi.ac.uk/europepmc/webservices/rest/search?query=<クエリ>&format=json&pageSize=25&resultType=core"
```

各結果の `isOpenAccess` と `inEPMC` を見る。`inEPMC` が `Y` なら Europe PMC に全文がある。
全文XMLは **`PMC` 接頭辞を含む PMCID をそのまま1セグメントで渡す**:

```bash
curl -s "https://www.ebi.ac.uk/europepmc/webservices/rest/PMC13006392/fullTextXML"
```

**この形式でしか通らない（実測）。** よくある間違いは全部 404 になる:

| URL | 結果 |
|---|---|
| `/rest/PMC13006392/fullTextXML` | **200**（167KB） |
| `/rest/PMC/PMC13006392/fullTextXML` | 404（source セグメントを付けた） |
| `/rest/PMC/13006392/fullTextXML` | 404（接頭辞を分離した） |
| `/rest/MED/41850248/fullTextXML` | 404（PMID では取れない。PMCID が要る） |

PMCID は検索結果の `pmcid` 欄にある。PMID しか無いときは、先に検索して PMCID を得る。
**404 を「全文が無い」と読み違えないこと**（URLの形が違うだけのことが多い）。

### 2. PubMed Central のミラー

PMCID があれば `https://www.ncbi.nlm.nih.gov/pmc/articles/<PMCID>/`

### 3. プレプリント版を探す

同じ研究の査読前版が公開されていることが多い。arXiv / bioRxiv / medRxiv / 著者の所属機関リポジトリ。
OpenAlex の `open_access.oa_url` にOA版のURLが入っていることがある。

### 4. DOI 解決先とは別のホスト

出版社サイトが 403 でも、同じ論文が学会サイト・著者ページ・機関リポジトリにあることがある。

### 5. それでも取れないなら、取得失敗として明示的に記録する

**抄録しか読んでいないのに本文を読んだかのように扱わない。**
「本文未取得」と記録し、その制約がレポートまで運ばれるようにする。

## やらないこと

- ログイン・CAPTCHA・2要素認証の自動突破（**恒久的にスコープ外**）
- 有料APIキーを必須にすること（すべて任意のフォールバックに留める）
- 第三者プロキシ経由での取得を、認証付き・機密・個人情報を含むURLに使うこと

## Windows 実行時の注意

Python から叩くときは `PYTHONIOENCODING=utf-8` を前置する（付け忘れると cp932 で落ちる）。
