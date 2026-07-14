---
type: reference
title: 字コンテ（テキスト・ショットリスト）のテンプレート（動画生成の設計図）
description: 動画を作る前に書く「字コンテ」（テキストのショットリスト）の普遍テンプレ。マルチショット・タイムスタンプ・VISUAL/ACTION/DIALOGUE・共通STYLE・メタ情報。任意で絵コンテ画像も生成
tags: [字コンテ, storyboard, 絵コンテ, video, planning, shot-list, commercial, template]
---

# 字コンテ（テキスト・ショットリスト）のテンプレート

> **用語**: ストーリーボード／絵コンテ＝**画像**を指す語。テキスト版は「**字コンテ**」（shot list）と呼ぶ（「テキスト・ストーリーボード」とは呼ばない。2026-07-14 確定）。

動画生成の一番の土台は**字コンテ（テキストのショットリスト）**。これを書いて承認を得てから生成する。**1本の動画＝複数ショット（カット・場面転換を含んでよい）**。各ショットを生成単位に分解して作り、繋いで完成（詳細は SKILL.md「動画生成フロー」）。**15秒は上限ではない**——クリップ/ショットを繋ぐ＋モデルの長尺/延長機能で伸ばせる。

## 1) メタ情報（ヘッダー）
- **総尺**: 例 30 秒
- **形式**: アスペクト比（縦 9:16 / 横 16:9 / 正方 1:1）
- **想定視聴者**: 例 18–35 歳
- **音の方向性**: 例 環境音中心 / ソフト ASMR / BGM 有無

## 2) 全ショット共通の STYLE ブロック（毎ショットに効かせる＝一貫性の要）
画風・照明・被写界深度・カメラ・質感を1つに固定し、全ショットのプロンプト頭に付ける。実写・広告調の汎用形:
`realistic cinematic look, soft natural lighting with gentle shadows, shallow depth of field with creamy background bokeh, shot on a real camera, premium commercial style` ＋ 必要なら視点指定（例 `POV hands only, no face visible` / `eye-level handheld`）。
リアル感の底上げは `reference/realism-naturalization-prompts.md`（実写を求める／「AIっぽい」と言われたら足す）。

## 3) 各ショットの記述（ショットリスト本体）
| 欄 | 書く内容 |
|---|---|
| 番号 | 1, 2, 3 … |
| タイムスタンプ | 0–2.5s, 2.5–5s …（★1連続ショット内の隣接キーフレーム間は生成モデルの最短尺以上・15秒以下） |
| **VISUAL:** | 画面に映るもの（被写体・背景・構図・レンズ感） |
| **ACTION:** | 被写体／カメラの動き（カメラワークは `reference/camera-movements.md` の定型を使う） |
| **DIALOGUE / AUDIO:** | セリフ・環境音・効果音・BGM の示唆 |
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
