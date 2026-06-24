# モバイルWeb の落とし穴（横はみ出し / iOS overscroll / タッチ操作）

スマホWeb（特に iOS Safari / Android Chrome）でレイアウト・タッチ周りに繰り返し出る
不具合と、その**確定的な切り分け手順**＋対処。推測で CSS をいじって往復する前に、
まず「DOM の実はみ出し」か「ブラウザのジェスチャ挙動」かを**実測で確定**すること。

---

## 症状 → 原因の対応表

| ユーザーの言葉 | 機械的な正体 | 主因 |
|---|---|---|
| 「横に引っ張るとゴムのように揺れる」 | overscroll bounce（ラバーバンド） | `overscroll-behavior` 未設定 or iOS の visual viewport バウンス |
| 「少し横に動く / 横スクロールできる」 | 実際の横スクロール | どこかの要素が `scrollWidth > clientWidth`（実はみ出し） |
| 「つまみ/スワイプ操作が効かず画面が動く」 | 指のジェスチャがページに奪われる | `touch-action` 未指定 or 横パンの遊び |

**重要**: 「揺れる」と「横に動く」は別物。揺れ＝バウンス（DOM は正常なことが多い）、
横に動く＝実はみ出し（犯人要素がいる）。両者は対処が違うので必ず切り分ける。

---

## ステップ1: まず実測する（推測で直さない）

### 1a. DOM はみ出し犯の特定（どの要素が幅を超えるか）
```js
(() => {
  const vw = document.documentElement.clientWidth;
  const bad = [...document.querySelectorAll('*')]
    .map(el => ({ el, over: Math.round(el.getBoundingClientRect().right - vw),
                  sw: el.scrollWidth, cw: el.clientWidth }))
    .filter(x => x.over > 0.5 || x.sw > x.cw + 1)
    .sort((a, b) => b.over - a.over);
  console.log(`vw=${vw} docSW=${document.documentElement.scrollWidth}`);
  console.table(bad.slice(0, 10).map(x => ({
    cls: (typeof x.el.className === 'string' && x.el.className) || x.el.tagName,
    over: x.over, sw: x.sw, cw: x.cw, pos: getComputedStyle(x.el).position })));
  if (bad[0]) bad[0].el.style.outline = '3px solid red';
})();
```
`document.scrollWidth === clientWidth` かつ 0件 → **DOM はみ出しは無い**（犯人は別）。

### 1b. 「揺れ」が DOM はみ出しか Safari バウンスかの判定（決定打）
`visualViewport.offsetLeft` を常時表示する overlay を仕込み、横に引っ張りながら見る：
- `scrollWidth - clientWidth`（= Δ）が 0 のまま **`visualViewport.offsetLeft` だけ動く**
  → **iOS Safari の visual viewport 横ラバーバンド**。DOM は正常。touch-action で対処。
- `Δ > 0` になる → **実はみ出し**。1a で出た犯人を直す。

```js
// debug overlay（Vue/React 不要・素の JS。計測後に必ず外す）
const d = document.createElement('div');
d.style = 'position:fixed;left:6px;bottom:6px;z-index:99999;background:#000;color:#0f0;font:12px monospace;padding:6px';
document.body.appendChild(d);
let maxOff = 0, maxD = 0;
setInterval(() => {
  const de = document.documentElement, vv = visualViewport;
  maxD = Math.max(maxD, de.scrollWidth - de.clientWidth);
  if (vv && Math.abs(vv.offsetLeft) > Math.abs(maxOff)) maxOff = vv.offsetLeft;
  d.textContent = `cw=${de.clientWidth} sw=${de.scrollWidth} D=${de.scrollWidth-de.clientWidth} | maxD=${maxD} off=${vv?vv.offsetLeft.toFixed(1):'?'} maxOff=${maxOff.toFixed(1)}`;
}, 100);
```
> 実例: `maxD=0, maxOff=27.0` → DOM はみ出しゼロなのに 27px 横バウンス＝Safari ラバーバンド確定。

### Chrome ヘッドレスは iOS Safari を再現しない
DevTools エンジン（Chrome headless + CDP）の実測で 0件でも、**iOS Safari 実機では
バウンスが出る**。横バウンス系は必ず実機 Safari で確認すること。Chrome 実測は
「DOM はみ出しの有無」確定には有効だが、「Safari バウンスの有無」は判定できない。

---

## ステップ2: 実はみ出しの典型原因（Δ>0 のとき）

1. **`width: 100vw` / `max-width: NNvw`** — `vw` は**縦スクロールバー幅を含む**ため
   `body`（=100%）を超える。`100vw` は横スクロールの定番 footgun。→ `100%` に置換。
2. **flex/grid 子の `min-width: auto`** — 既定で子は内容の最小幅まで縮まず、長い
   テキスト/トラックがはみ出す。→ 縮めたい子に `min-width: 0`（flex/grid アイテム）。
   `.grid > * { min-width: 0 }` も有効。
3. **`white-space: nowrap` の長文**（薬剤名・条件文・URL）→ `overflow-wrap: anywhere`。
4. **`position: absolute` の右はみ出し / 負マージン** — 親に幅予約（padding）が無いと
   ページ幅を広げる。`right: -Npx` は親の `padding-right: Npx` とセットで相殺する。
5. **固定px幅トラック**（`grid-template-columns: 1fr 380px` 等）— 狭幅で最小幅が
   ビューポートを超える。→ `minmax(0, 380px)` にして縮みを許可。

### `overflow-x: clip` の限界（なぜ効かないことがあるか）
- `clip`/`hidden` は**フロー内・absolute 子孫しかクリップしない**。
  **`position: fixed` の子孫はクリップ対象外**（fixed はビューポート基準で配置され、
  祖先の overflow を貫通する）。→ はみ出す fixed 要素は clip では消えない。fixed 要素
  側で個別に幅を閉じる（`#screen { overflow-x: hidden }` を fixed 要素自身に、
  または幅を `100%`/`min()` で cap）。
- `hidden` より `clip` を優先する理由: `overflow: hidden` は position:sticky の祖先を
  スクロールコンテナ化して sticky を壊す。`clip` は新しい formatting context を作らず
  sticky を壊しにくい。ただし clip は「原因を直す」ではなく「最後に切る」ガード。

---

## ステップ3: iOS Safari の横バウンス（Δ=0 なのに揺れる）

`overflow-x: clip` も `overscroll-behavior-x: none` も、**iOS Safari の visual viewport
横ラバーバンドには効きが弱い**（Chrome 系では overscroll-behavior が効く）。実効策は
**ページ全体の横パンジェスチャを発生させない**こと：

```css
html, body {
  overscroll-behavior-x: none;          /* Chrome 系の横バウンス止め */
  touch-action: pan-y pinch-zoom;       /* iOS: 縦パン+ピンチズームは許可、横パンは渡さない */
}
```
- `pan-y pinch-zoom` にすること。`none` はピンチズームまで殺し **WCAG 1.4.4 違反**に
  なり得る（医療/公共系は特に NG）。`pinch-zoom` を残せば a11y を保てる。
- **`user-scalable=no` / `maximum-scale=1` で viewport ズーム禁止は使わない**
  （低視力ユーザーの拡大を妨げ WCAG 1.4.4 違反）。横バウンスの正しい対処は
  touch-action であって viewport ズーム禁止ではない。
- 子要素で別の touch-action が要る場合（例: `input[type=range]` のスライダーは
  横ドラッグでつまみ操作したい）→ その要素に `touch-action: pan-y` を個別指定すれば
  body 既定より**要素側が優先**され、スライダー操作は従来どおり効く。

---

## ステップ4: タッチ操作がページに奪われる（スライダー/スワイプ）

`input[type=range]` 等で「つまみが動かず画面が動く」：
- 当該要素に **`touch-action: pan-y`**（横ドラッグをその要素の操作にし、縦だけページ
  スクロールに残す）。`none` はズームにも影響、`manipulation` は横パンを許可してしまい弱い。
- 併せてレイアウトの横はみ出し（min-width:0 等）を潰す。横パンの「遊び」があると
  横スワイプがページ横移動に化ける。

---

## まとめ（順序が大事）
1. **実測**（1a で犯人探し、1b で バウンス vs 実はみ出しを判定）— 推測で直さない。
2. 実はみ出し（Δ>0）→ 100vw/min-width:0/nowrap/absolute/固定px を潰す。clip は fixed に
   効かない点に注意。
3. Safari バウンス（Δ=0・offsetLeft だけ動く）→ `body { touch-action: pan-y pinch-zoom }`。
4. 横バウンス系は **iOS Safari 実機**で最終確認（Chrome headless では再現しない）。
5. a11y: ズーム禁止（user-scalable=no / touch-action:none）に逃げない。`pinch-zoom` を残す。
