# 構造化データ JSON-LD サンプル集

## Article / BlogPosting
```json
{
  "@context": "https://schema.org",
  "@type": "Article",
  "headline": "記事タイトル",
  "author": { "@type": "Person", "name": "著者名" },
  "datePublished": "2025-01-01",
  "dateModified": "2025-06-01",
  "image": "https://example.com/image.jpg"
}
```

## FAQPage
```json
{
  "@context": "https://schema.org",
  "@type": "FAQPage",
  "mainEntity": [{
    "@type": "Question",
    "name": "質問文",
    "acceptedAnswer": { "@type": "Answer", "text": "回答文" }
  }]
}
```

## Product with AggregateRating
```json
{
  "@context": "https://schema.org",
  "@type": "Product",
  "name": "[Product Name]",
  "description": "[Product Description]",
  "brand": { "@type": "Brand", "name": "[Brand Name]" },
  "aggregateRating": {
    "@type": "AggregateRating",
    "ratingValue": "[Rating]",
    "reviewCount": "[Count]",
    "bestRating": "5",
    "worstRating": "1"
  }
}
```

## SoftwareApplication
```json
{
  "@context": "https://schema.org",
  "@type": "SoftwareApplication",
  "name": "[Software Name]",
  "applicationCategory": "[Category]",
  "operatingSystem": "[OS]",
  "offers": {
    "@type": "Offer",
    "price": "[Price]",
    "priceCurrency": "USD"
  }
}
```

## ItemList (roundup pages)
```json
{
  "@context": "https://schema.org",
  "@type": "ItemList",
  "name": "Best [Category] Tools [Year]",
  "itemListOrder": "https://schema.org/ItemListOrderDescending",
  "numberOfItems": "[Count]",
  "itemListElement": [
    {
      "@type": "ListItem",
      "position": 1,
      "name": "[Product Name]",
      "url": "[Product URL]"
    }
  ]
}
```

## その他の主要スキーマ
- **BreadcrumbList** — パンくずリスト
- **LocalBusiness** — 店舗情報（住所、営業時間、電話番号）
- **HowTo** — 手順記事
- **VideoObject** — 動画コンテンツ

**検証**: Google Rich Results Test で必ずテストする。
