# Swiss-Modernism — Vignelli Canon & Müller-Brockmann Grid

> グリッド駆動・グロテスク書体・原色・厳格な規律による「Swiss / International Typographic Style」のデザインを、**原則だけでなく Web 上で load-bearing なグリッドとして実装し、0px 単位で検証する**ところまでカバーする。
>
> **いつ参照するか**: スタイル選択で「Swiss-modernism / International Typographic Style / editorial / magazine / grid-driven / Vignelli / Müller-Brockmann / wayfinding・サイン計画」を選んだとき。INDUSTRY DEFAULTS で Editorial/Publishing・Portfolio/Creative を扱うときの第一候補。
>
> 同梱スクリプト（`scripts/`、いずれもネットワーク・認証不要の決定論的ツール）:
> `vignelli_system.py`（トークン生成）／ `grid_tokens.py`（グリッド scaffold 生成）／ `verify_grid.js`（Puppeteer グリッド検証）。

---

## 共通の規律（両者に通底）

- **グリッドは装飾でなく倫理。** 「自分（エゴ）ではなくシステムがページを組織する」。Müller-Brockmann: *"The grid system is an aid, not a guarantee … one must learn how to use the grid; it is an art that requires practice."*
- **グロテスク・サンセリフ**（Helvetica / Akzidenz-Grotesk、Web では Inter / Helvetica Now / Archivo）。書体は自己表現でなく客観的組織のための道具。
- **flush-left / ragged-right（左揃え・右ラグ）が基本。justified（両端揃え）は避ける。**
- **階層はスケールとウェイトと余白で作る。色では作らない。**
- **色数を絞り、原色（特に赤）を1アクセントに。** purple/pink グラデは禁止（AI 生成バレ＆Swiss 様式に反する）。warm-cream の "Claude look" も避ける。
- **白（余白）が主役。** *"It is really the white that makes the black sing."* ページを埋めない。

---

## PART A — The Vignelli Canon（Massimo Vignelli, 1931–2014）

NYC 地下鉄ダイアグラム＆サイン標準（1972）、American Airlines、Knoll、National Park Service Unigrid、Grandi Stazioni(伊鉄道) などを手がけた。原典は彼自身の著書 *The Vignelli Canon*。**「デザインは様式の上位にある一つの規律。創造性は知識の支えを必要とする。」**

### Intangibles（描く前に決める）
1. **Semantics — まず意味を探す。** 主題・歴史・市場・送り手/受け手を調べ、本質を抽出。"Design without semantics is shallow."
2. **Syntactics — 関係を統制する。** グリッド、書体、見出し/本文/画像の関係、ページ間。"God is in the details."
3. **Pragmatics — 理解されねばならない。** 説明なしで自立する。"We love complexity but hate complications."
4. **Discipline / Appropriateness / Timelessness.** 杜撰さゼロ。"Listen to what a thing wants to be." 原形・原色・流行を超える書体を選ぶ。
5. **Equity — 長寿命のマークは集合文化。** 変更のための変更でなく**洗練（refine）する。置換しない。**

### Tangibles（具体ルール）
- **グリッド = 情報の組織化。** 「問題ごとに無限のグリッド、しかし最適は1つ」。**外マージン狭い=緊張、広い=静謐。ガターは狭く（〜本文1行分）**、type と画像が同一グリッドに吸い付くように。Canon の5グリッド（columns × modules）: **2×4, 5×4, 3×6, 6×6, 4×8**。
- **書体は生涯6書体で足りる:** Garamond(1532), Bodoni(1788), Century Expanded(1900), Futura(1930), Times(1931), **Helvetica(1957)**。＋Optima/Univers/Caslon/Baskerville。**house face は Helvetica。** *"I don't believe that when you write dog the type should bark."* 区別は**新奇な書体でなく space / weight / alignment** で。
- **1ページ最大2サイズ。見出し ≒ 本文の2倍**（例 10/20）。bold/light/roman/italic は機能的に控えめに。
- **カラム幅別の size/leading:** ≤70mm → 8/9・9/10・10/11、≤140mm → 12/13・14/16、>140mm → 16/18・18/20。
- **Rulers（罫）: major 2pt / minor 0.5–1pt。type は罫から hang する（罫にぶら下げる）。**
- **Scale で視覚的パワー**（巨大見出し vs 小本文）。声高でなくコントラストで強くする。
- **Color as Identifier（"Chromotype"）— 装飾でなく識別子。** 原色パレット（赤・青・黄）を基本。identity では色＝アイデンティティの一部。

### Transit & Wayfinding（地下鉄＋Grandi Stazioni）
- **路線ダイアグラム:** 45°/90° のみ。駅ドットは地理に関係なく等間隔。1線=1色。**実心ドット=必ず停車／中空リング=通過。** 陸/水はフラットな中立面。全面 Helvetica。
- **駅サイン:** **signal-blue パネルに白 Helvetica**、flush-left。cap height でヒエラルキー（駅名最大・内照／方向サイン頭上・矢印は cap box 共有／案内/規制は小・2pt 罫から hang）。**プラットフォーム番号は正方フラグ**。矢印・ピクトは type の cap box を共有。
- **ピクトグラム:** 幾何学・原形ベース、一定ストローク・cap box。図解でなく意味。

### HOW TO APPLY（手順）
1. **Intangibles パス:** semantics / appropriateness / timelessness を各1行で言語化。
2. **システムを1つに絞る:** グリッド1つ・**Helvetica**・**2サイズ**（body + 約2×見出し）・**識別子色1つ**。
3. **トークン生成:** `vignelli_system.py`（下記）。
4. **組版:** グリッド上に flush-left。白で階層を運ぶ。罫＋ウェイトで区別。scale でパワー。
5. **自己批評:** 2サイズ超？ justified？ 装飾的な色？ レイアウトが見えている／散らかっている？ 新奇書体？ → 削る。**"If you see the layout, it is probably a bad layout."**

### Canon palette（色＝識別子）
Vignelli vermilion `#F04E23` ／ Signal blue `#0039A6` ／ Signal yellow `#FFCC00` ／ Ink `#0A0A0A` ／ Warm paper `#F4F1EA` ／ White `#FFFFFF`。

### `scripts/vignelli_system.py`
決定論的トークン生成器（ネットワーク/認証不要）。Windows/Mac/Linux いずれも UTF-8 出力。
```
python scripts/vignelli_system.py                      # CSS（既定: Helvetica, vermilion）
python scripts/vignelli_system.py --primary "#0039A6"  # 識別子色を指定
python scripts/vignelli_system.py --base 16 --format css|scss|json
python scripts/vignelli_system.py --grid 4x8           # 1グリッドの列×モジュール図
python scripts/vignelli_system.py --signage            # 鉄道サインの cap-height モジュール表
```
出力 CSS の `--v-face` は `'Helvetica Neue', Helvetica, Arial, 'Liberation Sans', sans-serif` の順で、ヘッドレス描画でも実グロテスクに落ちるよう **'Liberation Sans' を generic fallback の前**に置く（下記「型の忠実性」参照）。

---

## PART B — Müller-Brockmann Grid（Josef Müller-Brockmann, 1914–1996）

原典 *Grid Systems in Graphic Design*(1981)。雑誌/レポート/longform を**本物の**モジュラーグリッドに乗せる。多くの実装が外す部分＝「グリッドを Web 上で真に load-bearing にする工学」と「それを証明するハーネス」までを含む。

> このスキルが防ぐ2つの実レビュー指摘:
> 1. *"グリッドが上に貼っただけでズレてる"* → オーバーレイがコンテンツと同じ content box に居なかった（§2.2）。
> 2. *"見出しの H がグリッドから外れて見える"* → 見出しの**箱**は線上だが**インク**が外れていた。大きな字は side-bearing を持つ（§2.6）。**Box-on-grid ≠ ink-on-grid。**

### 1. 規律（描く前に）
- **客観的秩序。** グリッドは "constructive thought"・可読性・客観性をもたらす。抑制が要点。
- **モジュラーグリッド。** type area を**列 AND 行**のモジュール群に分割、一定**ガター**、定義された**マージン**。要素はモジュール単位で占有。Müller-Brockmann の典型 field 数 8/20/32。**Web の堅実な既定は 12列 + 8px baseline**、行も見せたいなら 6×6 / 4×8。
- **Baseline グリッドは神聖。** **leading = baseline 単位の整数倍**、全要素が baseline に吸い付く。これが対向カラムや画像をページ越しに揃える。
- **タイポ:** グロテスク・サンセリフ、**flush-left ragged-right**、少ないサイズで大きなスケール跳躍。**数値/データを大きく**は署名的な手。
- **パレット:** 純白紙・ほぼ黒インク・**1アクセント＝赤が正統**。blue/purple グラデ禁止。
- **白 + 非対称。** 寛大なマージン、グリッドが張力で支える非対称構図。

### 2. グリッドを Web 上で実在させる（load-bearing な工学）
`scripts/grid_tokens.py` がこの scaffold 全体を正しく吐く。以下は「なぜそう作るか」。

**2.1 単一の真実源（one source of truth）** — 全グリッドパラメータを `:root` の CSS 変数に（`--cols, --gutter, --margin, --bl(baseline), --lh(leading=3×bl), --maxw`）。**コンテンツとオーバーレイが同じ変数を読む。**

**2.2 オーバーレイはコンテンツと同じ content box に置く ← 最頻バグ** — コンテンツが中央寄せ `max-width` コンテナ内、オーバーレイが section の**全幅 sibling** だと、`--maxw` より広い viewport で列位置がズレる＝「貼っただけ/ズレてる」。**修正:** `.guides` を同じ `.wrap` の**内側**に置き、列ガイドを `left/right = var(--margin)` ＋ **同じ** `repeat(var(--cols),1fr)` ＋ `column-gap:var(--gutter)` で描く。これでオーバーレイ列＝コンテンツ列が全幅で一致。

**2.3 全要素を列 LINE で置く（subgrid bands）** — span を目分量で置かない。各**band** が全列を張り subgrid で再公開:
```css
.band{grid-column:1 / -1; display:grid; grid-template-columns:subgrid; column-gap:var(--gutter); align-items:start;}
@supports not (grid-template-columns:subgrid){ .band{grid-template-columns:repeat(var(--cols),1fr);} }
```
子は `grid-column: <startline> / <endline>`（例 `1 / 6`, `6 / 13`）で置く。見出し・段落・写真・キャプションが同一線に吸い付く。

**2.4 縦リズムを baseline にロック** — leading = `--lh`（例 24px=3×8）。**display type の line-height は px で baseline の倍数**（unitless は箱が線から外れる）。全 margin/padding も baseline 倍数。**メディア高 = leading の倍数**（写真の上下とも線に乗る）。

**2.5 トグル（sizzle の中の sizzle）** — ボタン **+ `G` キー**で `body.grid-on` をトグル、オーバーレイを 0→1 フェード。番号付き列フィールド・baseline（`--lh` ごと major・`--bl` ごと minor）・マージン線を描く。**ページが実際に乗っているグリッドを見せること自体がデモ。**

**2.6 OPTICAL ALIGNMENT — 箱でなくインクを線に乗せる ← 微妙なバグ** — 180px の見出しは箱が線1にあってもインクが side-bearing 分だけ内側に入り、本文に対しズレて見える。実行時に補正:
```js
// document.fonts.ready 後とリサイズ時:
var cvs=document.createElement('canvas'),ctx=cvs.getContext('2d');
document.querySelectorAll('.masthead,.numeral,.shead h2,.h2b').forEach(function(el){
  el.style.marginLeft='0px';
  var cs=getComputedStyle(el),ch=(el.textContent||'').trim()[0]; if(!ch) return;
  if(cs.textTransform==='uppercase') ch=ch.toUpperCase();
  ctx.font=cs.fontStyle+' '+cs.fontWeight+' '+cs.fontSize+' '+cs.fontFamily; ctx.textAlign='left';
  var abl=ctx.measureText(ch).actualBoundingBoxLeft;     // +ve = インクが箱の左へはみ出す
  if(isFinite(abl)) el.style.marginLeft=abl.toFixed(2)+'px'; // 箱をずらしインクを線へ
});
```
masthead・大きな数値・section 見出しに適用。fluid type でも resize 再実行で追従し、**実際に読み込まれた**フォントで測るのでブラウザ上で正しい。
**測定の重大な注意:** side-bearing は**フォント固有**。ヘッドレス/サンドボックスの Chrome は webfont 欠落で別グロテスクに落ち、同じ `H` で**実 Inter は −7px、fallback は −16px**とズレる。オフライン検証では `@font-face`（ローカル TTF）で**実 webfont を埋め込む**こと。本番は実行時 JS が読込済みフォントを測るので正しい。

### 3. 検証 — 信じず測る → `scripts/verify_grid.js`
ヘッドレス Chrome(Puppeteer) で描画し、**`--maxw` を跨ぐ複数幅**（例 1440/1180/900。中央寄せドリフトを捕える）で assert:
1. **列遵守** — 全 `.band > *` の左が列 START に、右が列 END に吸い付く（≈0px）。**optical 整列した display 要素は除外**（箱は意図的に side-bearing オフセット、4で検証）。**罠:** START 集合と END 集合を両方作る。"line N まで"張る item はガターの遠い側で終わるので片端計算だと1ガター誤差を誤報する。
2. **オーバーレイ一致** — 各 `.guides .col` 矩形＝算出列矩形（≈0px）。
3. **Baseline** — テキスト上端 mod baseline ≈0（許容≈半 baseline）。
4. **Optical ink** — 各 display 要素のインク左（箱 − `actualBoundingBoxLeft`、実フォント）＝**その要素自身の**列線（常に線1ではない）。

サンドボックス Chrome で効くフラグ: `--headless=new --no-sandbox --disable-gpu --disable-dbus --use-gl=angle --use-angle=swiftshader`。`file://` は非ESモジュールページで可。CLI `--screenshot` は縦長で固まることがあるので Puppeteer で viewport ごとに撮る。PNG を image 対応 Read で**左上の拡大クロップ**（masthead vs 本文 vs 列線）を目視するのが最速の人間チェック。
合格例: `col=0px overlay=0px baseline≤4px ink=0px` → `GRID VERIFY: PASS`。

### 4. 仕上げの既定（揃うだけでなく秀逸に）
- **パレット:** 白 `#fff`・インク `#111`・1アクセント（Swiss red `#e4002b`）。warm-cream なし、blue/purple グラデなし。
- **書体:** display/body に実グロテスク webfont（Inter / Helvetica Now / Archivo）＋ folio/キャプション/グリッド注記に**モノ**（Space Mono / IBM Plex Mono）で技術的レジスタを補強。非ラテンは Noto Sans JP 等。
- **階層は scale + weight + 白で**（色でなく）。キーデータは**大きな数値**。kicker はモノ大文字。
- **実写真を使う。** 実被写体を実写真に。
- **spread モデル:** 全幅 section ごとに per-spread の `.grid` + `.guides`、一貫マージン/folio。

### 5. ワークフロー
1. 主題を選び、実写真を用意。
2. scaffold 生成: `python scripts/grid_tokens.py`（`--scaffold` で完結HTML1ページ。`--cols/--baseline/--gutter/--margin/--maxw/--accent` で調整。gutter/margin が baseline 倍数でないと stderr に WARNING）。
3. **subgrid bands** で spread を組み、全要素を**列線**で配置、spacing/line-height/メディア高を **baseline** にロック。
4. オーバーレイ（同一 content box）+ トグル + optical-alignment JS を追加（scaffold に同梱済み。セレクタリストを自分の display 要素に向ける）。
5. 公開後 **検証**: `CHROME=… PUP=… node scripts/verify_grid.js <file-or-url> --widths=1440,1180,900`。左上拡大クロップを目視。直して再公開。

### `scripts/grid_tokens.py` / `scripts/verify_grid.js`
- **`grid_tokens.py`** — 決定論的 scaffold 生成。`:root` トークン、`.grid`/`.band`(subgrid)、`.guides` オーバーレイ CSS、トグル JS、optical-alignment JS を**単一真実源**に配線して吐く。`--scaffold` で完結 HTML。ネットワーク/認証不要、UTF-8 出力（Windows でも動作）。
- **`verify_grid.js`** — Puppeteer ハーネス。上記4チェックを両端列計算・optical 除外・要素別列線 ink ターゲティング込みで実装、複数幅で PASS/FAIL。Env: `CHROME`(chrome バイナリ), `PUP`(puppeteer-core モジュールパス)。

---

## 型（タイプ）の忠実性 — ラスタライズ/画像生成での #1 の罠（両 PART 共通の普遍知見）

Helvetica は**多くのヘッドレス環境に未インストール**。SVG/HTML を `Helvetica`/`Arial`/`sans-serif` スタックでラスタライズ（cairosvg・ヘッドレス Chromium スクショ）すると、描画系が黙って **Noto Sans** に落ちる — Calibri 様の丸い humanist で、グロテスクが壊れる。「なぜ Calibri に見えるの？」と聞かれるまで気づかない不可視の失敗。
- **修正:** Helvetica/Arial メトリックの実グロテスクで描く — **Liberation Sans**（大抵入っている。`fc-match "Liberation Sans:bold"` で確認）か、`~/.fonts` に Helvetica/Arimo TTF を埋め込み `fc-cache`。`fc-match Helvetica` で fallback が判る。**信じる前に必ず1枚目視する。**
- **コード→画像→（任意で）現実 のパイプライン:** まずコードで正しいグロテスクで型/図を描く（真実源）→ 画像生成ツールに**参照画像として渡し、プロンプトで書体名を明示しドリフトを禁止**（"Helvetica Bold / Swiss neo-grotesque; NOT Calibri, NOT Noto Sans, NOT a rounded humanist sans"）。参照フォントが間違っていればモデルは忠実に間違いを再現する — プロンプトを責める前に**参照を直す**。
- **型が主役のヒーローに動画生成を避ける:** 多くの動画モデルは字形をフレーム間でドリフトさせる — 読ませるサインには致命的。型が主役なら**静止画**か**インタラクティブページの画面キャプチャ**で。

> ※ 公開/埋め込みの注意: 生成物をサンドボックス iframe に埋め込む場合、認証付きの相対 API URL は読めないことがある。画像は公開到達可能な URL（ビルド出力に同梱した静的ファイル等）で参照する。

---

## Source / 帰属

- 統合元: [alexmcdonnell-airtable/hyperagent-public-skills](https://github.com/alexmcdonnell-airtable/hyperagent-public-skills)（`skill-vignelli-canon-design-system` / `skill-muller-brockmann-grid-systems`）。Hyperagent 固有ツール参照（PublishWebpage 等）は本リポジトリ向けに汎用化済み。
- 原典: Massimo Vignelli, *The Vignelli Canon*（無料 PDF として公開）／ Josef Müller-Brockmann, *Grid Systems in Graphic Design*（1981）。
- 同梱スクリプト3点は元スキルの決定論的ツールをそのまま採用し、Windows コンソールでの UTF-8 出力のみ追加修正。
