---
type: reference
title: 字コンテ（テキスト・ショットリスト）のテンプレート（動画生成の設計図）
description: 動画を作る前に書く「字コンテ」（テキストのショットリスト）の普遍テンプレ。マルチショット・タイムスタンプ・VISUAL/ACTION/DIALOGUE・矢印凡例・共通STYLE・メタ情報
tags: [字コンテ, storyboard, 絵コンテ, video, planning, shot-list, commercial, template, 矢印, 凡例]
---

# 字コンテ（テキスト・ショットリスト）のテンプレート

> **用語**: テキスト版＝「**字コンテ**」（shot list）。**画像版＝演出ボード（StoryBoard）＝鉛筆ラフ＋矢印**（作り方は `reference/directing-board.md`）。i2v に入れるフォトリアルの実画像は「**キーフレーム画像**」と呼んで区別する（3層の定義は SKILL.md「動画生成フロー」）。

動画生成の一番の土台は**字コンテ（テキストのショットリスト）**。これを書いて承認を得る（**ゲート1**）→ 字コンテを**演出ボード**の絵にして承認を得る（**ゲート2**）→ 生成、の順（詳細は SKILL.md「動画生成フロー」）。**1本の動画＝複数ショット（カット・場面転換を含んでよい）**。**15秒は上限ではない**——クリップ/ショットを繋ぐ＋モデルの長尺/延長機能で伸ばせる。

## 1) メタ情報（ヘッダー）
- **総尺**: 例 30 秒
- **形式**: アスペクト比（縦 9:16 / 横 16:9 / 正方 1:1）
- **想定視聴者**: 例 18–35 歳
- **音の方向性**: 例 環境音中心 / ソフト ASMR / BGM 有無

## 2) 全ショット共通の STYLE ブロック（毎ショットに効かせる＝一貫性の要）
画風・照明・被写界深度・カメラ・質感を1つに固定し、全ショットのプロンプト頭に付ける。実写・広告調の汎用形:
`realistic cinematic look, soft natural lighting with gentle shadows, shallow depth of field with creamy background bokeh, shot on a real camera, premium commercial style` ＋ 必要なら視点指定（例 `POV hands only, no face visible` / `eye-level handheld`）。
リアル感の底上げは `reference/realism-naturalization-prompts.md`（実写を求める／「AIっぽい」と言われたら足す）。

## 2b) ★矢印の凡例（必ずここで定義する・2026-07-17 ユーザー確定）
演出ボード（鉛筆ラフの絵コンテ）はこの凡例に従って矢印を描く。**字コンテに書いた矢印だけがボードに現れる**。
**凡例の"説明"を持つのはこの字コンテ側だけ**——ボード画像には凡例ストリップを描かない（重複させない。ボードに載るのは矢印そのものと各パネルの注記だけ）。

| 色 | 意味 |
|---|---|
| **RED = BODY MOVEMENT** | キャラクターの身体の動き・アクションの軌道 |
| **BLUE = CAMERA MOVEMENT** | カメラの動き・カメラワーク |
| **GREEN = FRAMING / COMPOSITION**（矢印＋テキスト） | 構図の決定・フレーミングの意図 |
| **ORANGE = LIGHTING DIRECTION** | 光源の方向・ライティングの設計 |
| **YELLOW = ELEMENTAL VFX / ENERGY** | エフェクト・エネルギーの流動 |
| **BLACK TEXT = LENS / SHOT NOTE** | レンズの選定・カットに関する技術的メモ |

## 3) 各ショットの記述（ショットリスト本体）
| 欄 | 書く内容 |
|---|---|
| 番号 | 1, 2, 3 … |
| タイムスタンプ | 0–2.5s, 2.5–5s …（★1連続ショット内の隣接キーフレーム間は生成モデルの最短尺以上・15秒以下） |
| **VISUAL:** | 画面に映るもの（被写体・背景・構図・レンズ感） |
| **ACTION:** | 被写体／カメラの動き（カメラワークは `reference/camera-movements.md` の定型を使う） |
| **DIALOGUE / AUDIO:** | セリフ・環境音・効果音・BGM の示唆 |
| **矢印指示** | 上の凡例のうち、そのカットで指示したいものを明記（例 `RED: 右下→左上へ跳ね上がる / BLUE: 低い位置から右へオービット / ORANGE: 右奥からの逆光 / BLACK: 35mm ハンドヘルド`）。**テキスト欄を矢印記号で省略しない**（凡例＋具体記述の両方を書く） |
| （任意）SFX テロップ | 画面に乗せる短い擬音／掛け声（例 POP! / TEAR! / POUR~）。※オンスクリーン文字は画中テキストが得意なバックエンドで。**人物実写では画中テキスト抑制ルール**（SKILL.md「文字を書かせない」）に注意 |

**ショットの割り方**: カメラのカット・場面転換・時間ジャンプがあれば別ショット（＝別の生成単位、最後に `ffmpeg concat`）。カット無しで滑らかに繋がる区間は1連続ショット（i2v キーフレーム連鎖）。判定基準は `reference/storyboard-shot-boundary.md`。

## 4) フッター
- 総尺 / 形式（アスペクト比）/ スタイル一言。

## 5)（任意）字コンテを"1枚の絵コンテ画像"にする（クライアント提示用）
字コンテが本命。見せ方として、ショットリストを**インフォグラフィック画像**（3列×N行グリッド・番号バッジ・タイムスタンプ・各コマ画像・VISUAL/ACTION/DIALOGUE の3欄）に出す汎用プロンプト骨子:
> Create a clean, premium **storyboard infographic**. White minimalist layout. Title "STORYBOARD" + [PROJECT NAME] + subtitle [CONCEPT]. Info boxes: Duration / Style / Audience / Audio. **N panels in a 3-column grid**, each panel = numbered badge + timestamp + a realistic cinematic scene image + three text sections **VISUAL: / ACTION: / DIALOGUE:**. Footer: total duration, format (aspect ratio), style. Professional creative-agency look, clean spacing, rounded panel borders, accent color.

差し替え: `[PROJECT NAME]` / `[CONCEPT]` / パネル数 / 尺 / アスペクト / アクセント色。**案件固有語（ASMR 開封・商品名など）はこの骨子に残さない**。

---
骨子は商品コマーシャル用ストーリーボード指示を汎用化したもの（案件固有部分は除外）。
