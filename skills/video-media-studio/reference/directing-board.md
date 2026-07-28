---
type: reference
title: 演出ボード（StoryBoard）＝鉛筆ラフ＋矢印の作り方
description: 字コンテを鉛筆モノクロのラフ絵コンテ（色矢印つき）にしてユーザー承認を取り、承認済みボード＋参照で動画を生成するための実機検証済みプロンプト定型と罠
tags: [storyboard, 絵コンテ, 演出ボード, codex, image_gen, video, pencil, 矢印]
---

# 演出ボード（StoryBoard）— 鉛筆ラフ＋矢印

**位置づけ**: 字コンテ（テキスト）を**絵にした設計図**。動画生成の**ゲート2**（SKILL.md「動画生成フロー」2b）。
**キーフレーム画像とは別物** — ボードは構図・動き・カメラ・光・VFX の設計を担い、人物の同一性は参照写真が担う。
だから**人物はラフでよい**（似せる必要がない）。

**実機検証済み（2026-07-17 / Codex 0.144.5 + GPT Image）**: 下の定型で、鉛筆モノクロのラフに
赤=身体・青=カメラ・橙=光・黄=VFX・緑=フレーミング注記・黒=ショット注記が正しく描き分けられたボードが出た。
**4パネル・12パネル（4列×3行）とも成功**。12パネルでもレンズ表記（`24mm WIDE / ESTABLISHING`）・
秒数（`00:01`）・緑のフレーミング注記まで破綻せず描けた。**所要 約6〜18分/枚**（12パネルは長め）。
`timeout` は **900 秒以上**取る。**待ち方**: ログの最後が「still running / waiting」で止まって見えても
生きているので即断で殺さない。ファイルの出現をポーリングして待つ。

## 生成コマンド

```bash
codex exec -s workspace-write --skip-git-repo-check --cd <out_dir> -m gpt-5.6-sol - < board_prompt.txt
```

参照写真を人物の当たりに使いたいときだけ `-i <ref.png>`（**似せるためではなく、体型・衣装の当たり用**）。

### ★罠1: Codex が「rendering now」と言って画像を作らずにターンを終える（実機で再現）
`codex exec` が終了したのに PNG が無く、ログの最後が「The storyboard is rendering now」「The generation
is still running; I'm waiting...」で終わる。**画像生成は数分かかるので、これを"失敗"と即断しない**
（12パネルは実測で ~9分。`timeout` を 900 秒以上にして待つ）。そのうえでプロンプト末尾に**完了条件を明示**する:

```
IMPORTANT: Actually call the image_gen tool and WAIT for it to finish. Do NOT end your turn
saying it is 'rendering'. Your turn is only complete once the file <out_dir>/board.png exists
on disk — verify with ls before finishing. If image generation is refused, say REFUSED and the reason.
```

### ★罠2: PNG が保存されない（sandbox 初期化失敗）
`cat /proc/sys/kernel/apparmor_restrict_unprivileged_userns` が `1` なら bwrap が死んでいる。
記憶 [[codex-imagegen-bwrap-apparmor-docker-fix]] の docker ワンライナーで `0` にする。
`bwrap --ro-bind / / --unshare-user --uid 0 echo BWRAP_OK` が通れば復活。

## プロンプト定型（`<>` を差し替え）

```
Generate a single image: a hand-drawn PENCIL STORYBOARD sheet, <N> panels in a <cols>x<rows> grid
on off-white paper.

ART STYLE (critical): rough monochrome graphite pencil sketch, loose gestural linework, visible
construction lines and hatching, smudged shading. NOT photoreal, NOT painted, NOT 3D render, NOT
colored artwork. It must look like a film director's rough storyboard drawn by hand in pencil.

Each panel has a thin black rectangular border, a small panel number in the top-left corner, and a
small timestamp label (e.g. "0-1.25s").

Subject in all panels: <人物・衣装・場所の一言。ラフでよい>
Panel 1: <字コンテ shot1 の VISUAL を一行で>
Panel 2: <...>
（カット数ぶん並べる。1カット＝1パネル）

ANNOTATIONS drawn ON TOP of the pencil art (these are the ONLY colored elements — everything else
stays monochrome pencil):
- RED curved arrows = the body movement / action trajectory
- BLUE arrows = the camera movement
- GREEN short handwritten text labels inside each panel = framing/composition note
  (panel1 "<...>", panel2 "<...>", ...)
- ORANGE arrows = the lighting direction. ALWAYS draw these as a pair of two or three SHORT,
  STRAIGHT, PARALLEL arrows entering from the very edge or corner of the panel and pointing inward.
  Never long, never curved, never in the middle of the action.
- YELLOW arrows = elemental VFX / energy flow. ALWAYS draw these as LONG strokes that follow the
  effect itself inside the scene (rising energy, a vortex, impact rays). Never a short parallel
  pair at the panel edge.
（オレンジと黄色は色が近いので、上の"形と配置の文法"で区別させる＝下の解説参照）

Under each panel, small black handwritten-style caption text = lens / shot note:
1 "<WIDE / ORBITING / HANDHELD>", 2 "<...>", ...

Do NOT draw a legend, key, or colour-explanation strip anywhere on the sheet. No "RED = ..." /
"BLUE = ..." captions. The only text is the panel numbers, the timestamps, the green framing
notes inside panels, and the black lens/shot note under each panel.

Landscape 16:9 sheet. Save the image to <out_dir>/board.png
```

**★凡例（各矢印の説明）はボードに描かない**（2026-07-17 ユーザー確定・実機検証済み）。**凡例は字コンテ側で定義済み**なので
ボードに載せると重複。ボードに載るのは**矢印そのもの＋各パネルの注記（番号・秒数・緑のフレーミング注記・黒のレンズ注記）だけ**。
GPT Image は放っておくと凡例ストリップを描くので、上の `Do NOT draw a legend...` を明示的に入れる
（`Fill the full sheet ... leave no reserved band for a legend` まで書くと確実）。
**副次効果: 凡例帯が消えた分、同じ12コマでも1コマが大きく描かれる**（実測 2026-07-17・絵の情報量が上がるので歓迎）。

### ★オレンジ（光）と黄色（VFX）は「形と配置」で区別する — 凡例を足さない
2026-07-17 にユーザーから「オレンジと黄色は色が似ていて紛らわしい。ボードにも凡例を復活させるべきか？」と
検討が入り、**Claude と Codex が独立に同じ結論**（＝復活させない）に達したので確定した。以後この議論を蒸し返さない。

- **凡例は今回の問題を解決しない**: 凡例が教えるのは「オレンジ＝光／黄色＝VFX」という**色の意味**であって、
  目の前の矢印が**どちらの色か**は教えない。混同しているのは意味ではなく**色の知覚**なので、凡例を足しても
  「2色ある」と分かるだけで照合の手間が増える。
- 復活の代償: ボードは r2v の参照に渡すので**文字が増えるほど映像への漏れリスクが上がる**／1コマが小さくなる。
  凡例は字コンテに必ずあり、レビューは字コンテと並べて行うのでボード単独で読む場面が無い。
- **採用した解**: 上のプロンプト定型のとおり**線の文法を固定**する（オレンジ＝画面端から入る短い平行な2〜3本／
  黄色＝現象に沿う長いストローク）。実測ではモデルは放っておいてもこう描き分けており、明文化するだけで足りる。
- **不採用**: 「黄色をマゼンタに変える」（Codex の第一推奨で色としては最も確実だが、**6色はユーザーが提示した
  参照ボードの規約そのもの**なので、規約自体の変更はユーザーの決定事項。勝手に変えない）。
- 弱点として自覚しておく: 縮小表示・低彩度印刷・色調変換が挟まると色の接近が効いてくる。**そのときは形の文法が
  最後の砦**なので、文法を崩したボードが出てきたら再生成する。

**矢印は字コンテに書いたものだけ描く**。字コンテに `BLUE:` が無いカットに青矢印を勝手に足さない
（＝動画のシーン・動作を無断で足さないルールと同じ。SKILL.md「6要素」）。

## ★人物は「無個性プロキシ」で描く＋ボードは2枚立て（ユーザー確定 2026-07-28・Codex 相談済み）

**ボードのラフ画に描いた顔・髪型・服が、生成映像の人物に引っ張られる（汚染される）。** 同一性は人物リファレンス写真が担うのだから、**ボードからは同一性情報を物理的に消す**。

### 人物の描き方＝(b) 無個性の輪郭プロキシ

| 案 | 判定 |
|---|---|
| (a) 木製ドール風マネキン | **非推奨**。木目・球体関節・裸に見える表面が映像に混入する |
| **(b) 輪郭のみの人型＋最小限の関節・向き** | **★これを使う**。頭は卵形、顔は十字の補助線だけ、髪は描かない。肩/骨盤/肘/膝/重心線は残す |
| (c) 棒人間 | プリビズ専用。胸郭の向き・画面内占有率・奥行きが曖昧 |
| (d) 普通の人物ラフ | **最も汚染リスクが高い**（無意識に描いた顔立ち・前髪・襟・体型をモデルが採用する） |

- **顔**: 目鼻を描かない。ただし**頭部の角度・目線・顎の向きは十字補助線で指定**（表情設計が抜けるのを防ぐ）。
- **髪**: **一切描かない**（実機 2026-07-28: 「髪を解く」カットでモデルが毛流れ・前髪を描いてしまい、ユーザーに「02に髪型が入ってる」と指摘された）。髪の動きが要るカットは **RED 矢印＋薄いグレーの点線（髪が落ちる範囲）だけ**で示す。プロンプトに `ABSOLUTELY NO HAIR ANYWHERE — no strands, no fringe, no bangs, no hairstyle, no locks, no hair silhouette; the head stays completely bald and blank in all panels` を明示する（1回言うだけでは描かれる）。
- **服**: **薄いグレーのシルエット包絡線のみ**（袖幅・裾丈・襟の開き・揺れ範囲だけ）。柄・ボタン・縫い目・素材・襟デザインは描かない。色/柄/素材は**ワードローブ参照だけに持たせる**。胸元は服でなく**ネックライン境界と露出範囲**を線・面で示す。
- ボード人物を実人物に**中途半端に似せない**（似せるほど「別バージョンの本人」と解釈される）。背景も描き込まず、主要物と遮蔽物の線だけ。

### ボードは2枚書き出す（確認版／生成投入版）

| 版 | 中身 | 用途 |
|---|---|---|
| **人間確認版** | カット番号・秒数ラベル・色矢印・注記あり | **ゲート2のユーザー承認用**（これまでどおり） |
| **生成投入版（クリーン）** | **矢印・文字・数字・注記・枠マークを全部除去**。構図・ポーズ・カメラの寄り・光の明暗だけ | **動画生成の参照に渡すのはこちら** |

- **否定文だけでは防ぎ切れない**（Veo はスタイル画像を画風に反映、Seedance は構図・カメラ・動作・ビジュアルを横断参照する）。**入力から不要情報を物理的に消す方が強い**。
- クリーン版のプロンプト末尾定型（実機で矢印・文字ゼロを確認済み）:
  > `ABSOLUTELY NO ARROWS of any colour, NO coloured marks, NO text, NO letters, NO numbers, NO panel labels, NO time codes, NO handwritten notes, NO captions, NO corner framing marks, NO legend, NO annotations anywhere in the image. Completely clean panels showing only the drawn composition.`
- **矢印は焼き込まず、動きはプロンプト文章に変換して渡す**（例:「人物は画面左から右へ2歩移動。カメラは同速度で右へトラック。ズームなし」）。
- プロンプトで**参照の役割分離を毎回同じ文言で**書く: `Image 1 = composition, pose and camera direction ONLY / face, hair and body identity from Image 2 ONLY / wardrobe from Image 3 ONLY`。
- Codex 推奨だが未採用の選択肢（必要なら検討）: **原則1カット1画像**（1枚に並べない）。※本プロジェクトは3カット1枚で運用し、実機で問題が出たら分割する。

## 承認後 — 動画生成への渡し方

**★ユーザー確定（2026-07-17）: ボード画像も参照に入れる。**（2026-07-28 以降は**クリーン版**を渡す）

```bash
"$UV" run scripts/cloud_atlascloud.py video \
  --model bytedance/seedance-2.0/reference-to-video \
  --reference-image board.png \
  --reference-image ref1.png --reference-image ref2.png \
  --prompt "<字コンテ本文＋ボードの矢印を文章化＋下の否定文>" --duration 15
```

**必ず初回出力を目視する（漏れ検査）**: r2v は参照を強くコピーするので、**鉛筆のモノクロ画風や
矢印そのものが映像に出る**危険がある（既知の実測: 参照写真の服装・裸足をそのまま採用する挙動）。
否定文を必ず入れる:

> `photoreal live-action footage, NOT a pencil sketch, no drawn arrows or annotations in frame`

**それでも漏れるならボードを参照から外し、字コンテ＋ボードの文章化だけで生成する**（構図はプロンプトで担保）。
漏れたまま納品しない。

## チェックリスト（提出前）

- [ ] パネル数＝字コンテのカット数（1カット＝1パネル）
- [ ] 鉛筆モノクロ。有彩色は凡例の矢印・注記だけ（フォトリアル化・彩色・リアル化スターターを足していない）
- [ ] 各パネルにカット番号と秒数ラベル
- [ ] 字コンテに書いた矢印が全部描かれている／書いていない矢印が増えていない
- [ ] **凡例ストリップが描かれていない**（凡例は字コンテ側。描かれていたら再生成）
- [ ] **オレンジ（光）＝画面端から入る短い平行な2〜3本／黄色（VFX）＝現象に沿う長いストローク**になっている
      （色が近いので形で区別する。文法が崩れて両者が同じ形になっていたら再生成）
- [ ] **人物が無個性プロキシになっている**（顔立ちなし・**髪を1本も描いていない**・服はグレーのシルエット包絡線のみ。
      1パネルでも髪型や襟デザインが描かれていたら再生成＝同一性汚染源）
- [ ] **生成投入版（クリーン）を別に書き出した**（矢印・文字・数字・注記・枠マークがゼロ）。生成に渡すのはクリーン版
- [ ] ユーザーに提示して**承認を取った**（字コンテの承認はボードの承認ではない）
