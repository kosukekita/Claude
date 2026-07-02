# Color Selection Guidelines

Color theory and role-based color selection only. For everything else, use the dedicated references:

- **Font choice / typography pairings** → `google-fonts-selection.md`
- **Chart / data-visualization choice** → `chart-selection.md` (comprehensive) or `ui-decision-data.md` (Chart Choice quick rules)
- **Concrete color token values (hex) by product type** → `product-color-palettes.md`

---

## COLOR PALETTE GUIDELINES

### カラー選定ルール
1. **Primary**: ブランドアイデンティティを代表する色
2. **Secondary**: Primary を補完する色
3. **CTA (Accent)**: Action ボタン用の目立つ色（Primary と異なること）
4. **Background**: 主要背景色
5. **Text**: 本文テキスト色（背景とのコントラスト比 4.5:1 以上）

### 業界別カラームード（色の方向性）

具体的なトークン値（hex）は `product-color-palettes.md` を参照。ここでは色の方向性を言語で示すのみ。

- **SaaS/Tech**: 信頼感のあるブルー系を primary に、補色にバイオレット。ダーク背景も選択肢。
- **Healthcare**: 落ち着いたグリーンと穏やかなブルー。明るくクリーンな背景。
- **Fintech**: 権威あるネイビーを基調に、利益=グリーン / 損失=レッドで状態を明示。
- **E-commerce**: ブランド固有色 + 目立つ CTA（オレンジまたはレッド）。
- **Wellness**: 柔らかいピンク、セージグリーン、ゴールドの上品な組み合わせ。ネオンは避ける。
- **Education**: 温かみのあるイエローとパープル。明るくフレンドリーな配色。
- **Gaming**: シアンとマゼンタなど高彩度のネオン。ダーク背景で映えさせる。
- **Nothing / Technical**: モノクロのグレースケール階調を主体に、アクセントとして最小限のレッド、状態色にグリーン（success）とアンバー（warning）。

---

## 参照先まとめ

- タイポグラフィのペアリング表・フォント選定ルールは `google-fonts-selection.md` に一本化。
- チャート種別の選定は `chart-selection.md`（詳細）/ `ui-decision-data.md`（クイック）に一本化。
- 各プロダクト種別ごとの hex トークンは `product-color-palettes.md` に一本化。
