# HTML 実装パターン集

## 画像最適化

### picture 要素（フォーマットフォールバック）
```html
<picture>
  <source srcset="image.avif" type="image/avif">
  <source srcset="image.webp" type="image/webp">
  <img src="image.jpg" alt="Description" width="800" height="600" loading="lazy" decoding="async">
</picture>
```

### レスポンシブ画像
```html
<img src="image-800.jpg"
  srcset="image-400.jpg 400w, image-800.jpg 800w, image-1200.jpg 1200w"
  sizes="(max-width: 600px) 400px, (max-width: 1200px) 800px, 1200px"
  alt="Description">
```

### LCP / Hero 画像（fetchpriority）
```html
<img src="hero.webp" fetchpriority="high" alt="Hero image" width="1200" height="630">
```

### Below-fold 画像（lazy + async decoding）
```html
<img src="photo.webp" alt="Description" width="600" height="400" loading="lazy" decoding="async">
```

## Hreflang

### HTML link tags
```html
<link rel="alternate" hreflang="en-US" href="https://example.com/page" />
<link rel="alternate" hreflang="fr" href="https://example.com/fr/page" />
<link rel="alternate" hreflang="x-default" href="https://example.com/page" />
```

### XML Sitemap with hreflang
```xml
<?xml version="1.0" encoding="UTF-8"?>
<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9"
        xmlns:xhtml="http://www.w3.org/1999/xhtml">
  <url>
    <loc>https://example.com/page</loc>
    <xhtml:link rel="alternate" hreflang="en-US" href="https://example.com/page" />
    <xhtml:link rel="alternate" hreflang="fr" href="https://example.com/fr/page" />
    <xhtml:link rel="alternate" hreflang="x-default" href="https://example.com/page" />
  </url>
</urlset>
```

## 比較ページ Feature Matrix
```
| Feature          | Your Product | Competitor A | Competitor B |
|------------------|:------------:|:------------:|:------------:|
| Feature 1        | ✅           | ✅           | ❌           |
| Feature 2        | ✅           | ⚠️ Partial   | ✅           |
| Pricing (from)   | $X/mo        | $Y/mo        | $Z/mo        |
```
