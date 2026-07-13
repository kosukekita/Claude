---
name: storyboard-text-first-procedure
description: 動画storyboard作成の恒久手順。不確かならCodex確認→テキスト先行→ユーザー承認→画像(秒数ラベルで対応)。参照+リアル+シネマ
metadata: 
  node_type: memory
  type: feedback
  originSessionId: 7f792248-9bef-40fb-8283-33d15119eae9
---

★★ユーザー恒久手順（2026-07-13 指示「次からこの手順でstoryboardを作って」）。動画のstoryboardは必ずこの順で作る（video-media-studio スキルの storyboard フローを、この具体規律で運用する）:

1. **実世界の工程/仕組みが不確かなら、まず Codex に確認して正確にする**（例: バーテンダーの本物のシェイク工程＝材料はグラスでなくシェーカーのティンに入れる→氷→密閉→両手でシェイク→濾してグラス）。推測で描かない。
2. **テキスト storyboard を先に作る**（画像より先）。各カットに **番号 / タイムスタンプ（0–4s 等）/ VISUAL（映るもの・道具・構え）/ ACTION（動作）/ AUDIO** ＋ **共通STYLEブロック** ＋ **メタ（総尺/形式9:16/音/参照）**。Seedance/i2v は1クリップ4秒以上なので**カットは4秒刻み**が無難。
3. **ユーザーに提示して承認を得る**。承認前に画像/動画を作らない。
4. **承認後に画像 storyboard を生成**。★**各パネルに秒数ラベル（「① 0–4s 動作」等）を焼き込み、テキストと1対1で対応**させる（ラベル無しの2x2は「どれが何秒か分からない」とNG＝2026-07-13指摘）。ラベルは Noto Sans CJK JP で drawtext。
5. **参照＋スキルのリアル質感・シネマを"ふんだん"に**: キャラ/人物リファレンス画像＋ペルソナ設定＋関連素材（カクテル等）を元に、realism-naturalization（毛穴/実カメラ/no-CG）＋シネマティック（アナモルフィック・浅い被写界深度・実用光＋リム・フィルムグレイン・カラーグレード）を効かせる。
6. **カメラの"動き"（dolly/pan/tilt/orbit等）は静止画storyboardに入れず、動画生成の段階で付与**（静止画には"シネマティックな画作り"＝構図/光/質感だけ）。
7. 画像モデルは Seedream（`cloud_openrouter.py image`・bytedance/seedream）、動画は SFW=Seedance / NSFW=wan-2.7-spicy。**Seedance/Seedream を混同しない**（Seedance=動画、Seedream=画像）。

**違反履歴（2026-07-13）**: (a) テキスト承認前にいきなり2x2画像を作った (b) 秒数ラベルが無く対応が不明 (c) 工程を間違えた（素材をカクテルグラスに注ぐと描いた＝正しくはシェーカーのティン）。→ 本手順をルール化。

関連: [[quality-over-speed-media-gen]] [[person-image-6elements-confirm-before-fill]] [[realism-naturalization-default-on]] [[reference-selection-use-swipe-app]]
