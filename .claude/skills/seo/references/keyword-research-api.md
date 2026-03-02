# Google API + AI キーワードリサーチ

## セットアップ

### 1. Google Ads API（Keyword Planner）

**前提条件**:
- Google Ads アカウント（出稿不要、アカウント作成のみでOK）
- Developer Token（Google Ads API Center で申請）
- OAuth 2.0 認証情報

```bash
pip install google-ads
```

**設定ファイル** (`google-ads.yaml`):
```yaml
developer_token: "YOUR_DEVELOPER_TOKEN"
client_id: "YOUR_CLIENT_ID"
client_secret: "YOUR_CLIENT_SECRET"
refresh_token: "YOUR_REFRESH_TOKEN"
login_customer_id: "YOUR_CUSTOMER_ID"  # ハイフンなし10桁
```

**Developer Token 取得手順**:
1. Google Ads にログイン → ツールと設定 → API Center
2. Developer Token を申請（Test Account なら即時発行、本番は審査あり）
3. Test Account でも Keyword Planner API は利用可能（データは本番と同等）

### 2. Google Search Console API

```bash
pip install google-api-python-client google-auth-oauthlib
```

### 3. DataForSEO（オプション）

```bash
pip install dataforseo-client  # または requests で直接呼び出し
```

---

## コード例

### Keyword Planner API — シードからキーワード候補を一括取得

```python
# /// script
# requires-python = ">=3.11"
# dependencies = ["google-ads>=25.0.0", "pandas"]
# ///
"""Google Ads Keyword Planner API でキーワード候補を一括取得"""

import pandas as pd
from google.ads.googleads.client import GoogleAdsClient


def get_keyword_ideas(
    client: GoogleAdsClient,
    customer_id: str,
    seed_keywords: list[str],
    language_id: str = "1005",  # 日本語
    location_id: str = "2392",  # 日本
) -> pd.DataFrame:
    """シードKWからキーワード候補+ボリューム+競合度を取得"""
    keyword_plan_idea_service = client.get_service("KeywordPlanIdeaService")
    request = client.get_type("GenerateKeywordIdeasRequest")

    request.customer_id = customer_id
    request.language = f"languageConstants/{language_id}"
    request.geo_target_constants.append(f"geoTargetConstants/{location_id}")
    request.keyword_plan_network = (
        client.enums.KeywordPlanNetworkEnum.GOOGLE_SEARCH
    )
    request.keyword_seed.keywords.extend(seed_keywords)

    results = keyword_plan_idea_service.generate_keyword_ideas(request=request)

    rows = []
    for idea in results:
        metrics = idea.keyword_idea_metrics
        rows.append({
            "keyword": idea.text,
            "avg_monthly_searches": metrics.avg_monthly_searches,
            "competition": metrics.competition.name,
            "competition_index": metrics.competition_index,
            "low_top_of_page_bid": metrics.low_top_of_page_bid_micros / 1_000_000,
            "high_top_of_page_bid": metrics.high_top_of_page_bid_micros / 1_000_000,
        })

    return pd.DataFrame(rows)


if __name__ == "__main__":
    client = GoogleAdsClient.load_from_storage("google-ads.yaml")
    customer_id = "1234567890"

    seeds = ["SEO対策", "キーワード選定", "検索順位"]
    df = get_keyword_ideas(client, customer_id, seeds)

    # ボリューム降順でソート
    df = df.sort_values("avg_monthly_searches", ascending=False)
    df.to_csv("keyword_ideas.csv", index=False)
    print(f"取得件数: {len(df)}")
    print(df.head(20))
```

### GSC API — 既存サイトの実クエリデータ取得

```python
# /// script
# requires-python = ">=3.11"
# dependencies = [
#     "google-api-python-client",
#     "google-auth-oauthlib",
#     "pandas",
# ]
# ///
"""Google Search Console API で既存サイトのクエリデータを取得"""

import pandas as pd
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build


def get_gsc_queries(
    credentials: Credentials,
    site_url: str,
    start_date: str,
    end_date: str,
    row_limit: int = 25000,
) -> pd.DataFrame:
    """GSCから全クエリデータを取得（最大25,000行/リクエスト）"""
    service = build("searchconsole", "v1", credentials=credentials)

    all_rows = []
    start_row = 0

    while True:
        response = (
            service.searchanalytics()
            .query(
                siteUrl=site_url,
                body={
                    "startDate": start_date,
                    "endDate": end_date,
                    "dimensions": ["query", "page"],
                    "rowLimit": row_limit,
                    "startRow": start_row,
                },
            )
            .execute()
        )

        rows = response.get("rows", [])
        if not rows:
            break

        for row in rows:
            all_rows.append({
                "query": row["keys"][0],
                "page": row["keys"][1],
                "clicks": row["clicks"],
                "impressions": row["impressions"],
                "ctr": row["ctr"],
                "position": row["position"],
            })

        start_row += row_limit
        if len(rows) < row_limit:
            break

    return pd.DataFrame(all_rows)
```

### AI 統合 — Claude でキーワード分類・クラスタリング

```python
# /// script
# requires-python = ">=3.11"
# dependencies = ["anthropic", "pandas"]
# ///
"""Claude API でキーワードを意図分類・クラスタリング"""

import json

import anthropic
import pandas as pd

client = anthropic.Anthropic()


def classify_keywords(keywords: list[str], batch_size: int = 200) -> pd.DataFrame:
    """キーワードを意図×ファネルで分類（バッチ処理）"""
    all_results = []

    for i in range(0, len(keywords), batch_size):
        batch = keywords[i : i + batch_size]

        response = client.messages.create(
            model="claude-sonnet-4-6",
            max_tokens=4096,
            messages=[
                {
                    "role": "user",
                    "content": f"""以下のキーワードを分類してください。

キーワード:
{json.dumps(batch, ensure_ascii=False)}

各キーワードについて以下を判定:
- intent: informational / commercial / transactional / navigational
- funnel: tofu (認知) / mofu (検討) / bofu (購入)
- cluster: トピッククラスター名（自動命名）
- priority: high / medium / low（商業的価値ベース）

JSON配列で返してください:
[{{"keyword": "...", "intent": "...", "funnel": "...", "cluster": "...", "priority": "..."}}]""",
                }
            ],
        )

        parsed = json.loads(response.content[0].text)
        all_results.extend(parsed)

    return pd.DataFrame(all_results)


def find_content_gaps(
    kw_ideas: pd.DataFrame,
    gsc_data: pd.DataFrame,
) -> pd.DataFrame:
    """Keyword Planner候補 vs GSC既存データでギャップ分析"""
    existing = set(gsc_data["query"].str.lower().unique())
    gaps = kw_ideas[~kw_ideas["keyword"].str.lower().isin(existing)].copy()
    gaps = gaps.sort_values("avg_monthly_searches", ascending=False)
    return gaps
```

---

## 統合ワークフロー（1000KW 選定パイプライン）

```
[シード 10-20語]
    │
    ▼
[Keyword Planner API] ── 候補 2000-5000 KW
    │
    ▼
[GSC API] ── 既存ランキング KW 取得
    │
    ▼
[コンテンツギャップ分析] ── 未カバー KW 抽出
    │
    ▼
[Claude 分類] ── 意図 × ファネル × クラスター
    │
    ▼
[スコアリング] ── volume / (difficulty × 既存順位)
    │
    ▼
[上位 1000KW] ── ピラー × クラスター構造で CSV 出力
```

### 実行例

```python
# 1. Keyword Planner からアイデア取得
seeds = ["SEO対策", "Web集客", "コンテンツマーケティング", "検索順位"]
kw_ideas = get_keyword_ideas(ads_client, customer_id, seeds)
# → 約3000候補

# 2. GSC から既存データ取得
gsc_data = get_gsc_queries(credentials, "https://example.com", "2026-01-01", "2026-02-28")
# → 既存ランキング1500クエリ

# 3. ギャップ分析
gaps = find_content_gaps(kw_ideas, gsc_data)
# → 未カバー2100KW

# 4. Claude で分類
classified = classify_keywords(gaps["keyword"].tolist())
# → 意図×ファネル×クラスター付き

# 5. スコアリング＆上位1000選定
merged = gaps.merge(classified, on="keyword")
merged["score"] = merged["avg_monthly_searches"] / (merged["competition_index"] + 1)
top_1000 = merged.nlargest(1000, "score")
top_1000.to_csv("top_1000_keywords.csv", index=False)
```

---

## コスト比較

| 方法 | 月間処理量 | コスト | 所要時間 |
|------|-----------|--------|---------|
| 手動（Ubersuggest等） | 100-300 KW | 無料-$50 | 10-20時間 |
| Google Ads API + AI | 10,000+ KW | 実質無料（API無料+AI $1-5） | 10-30分 |
| DataForSEO + AI | 50,000+ KW | $50-200 + AI $5-20 | 1-2時間 |

---

## 注意事項

- **Developer Token**: Test Account は即時発行。本番アカウントは「Basic Access」審査に1-3営業日
- **レート制限**: Keyword Planner API はシード10語/リクエスト推奨。大量処理はバッチ+sleep(1)
- **データ精度**: Test Account でもボリュームデータは本番と同等だが、範囲表示の場合あり（アクティブキャンペーンがあると正確な数値）
- **AI分類の精度**: 200KW/バッチが最適。多すぎると分類精度が低下
- **pytrends（Google Trends）**: 非公式APIのためレート制限厳しい。sleep(2-5)必須、IP制限あり
