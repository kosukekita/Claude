---
name: nsfw-auto-pipeline-explicit-video
description: NSFW自動生成パイプライン(Workflow)と、破綻しないexplicit動画の型(男を描かない/臍上/縦バウンド)＋胸サイズはバックエンドで扱いが真逆
metadata: 
  node_type: memory
  type: project
  originSessionId: 7f792248-9bef-40fb-8283-33d15119eae9
---

**NSFW 全自動生成パイプライン（Workflow）と explicit 動画の作り方**（2026-07-09〜10 に akitaken の ~/.claude で構築・実証）。

## パイプライン（Workflow スクリプト・再起動で毎回新ペルソナ一式）
- スクリプト: `~/.claude/projects/<スラグ>/7f792248-.../workflows/scripts/nsfw-auto-pipeline-wf_787507e5-57b.js`（Workflow ツールで scriptPath 指定で再実行）。
- 5段: **Plan**(フォルダ作成＋ペルソナ＋行為を自動決定＋4プロンプト書き出し) → **Frame**(ローカル z-image で explicit 先頭フレーム) → **Video**(AtlasCloud wan-2.7-spicy i2v・15秒＝最大) → **Clothe**(ローカル Qwen-Edit で職業の制服を着せSFW化) → **Sheet**(Codex -i で SFW 4パネルシート)。全成果物(画像3＋動画1)を `~/media-out/nsfw-auto/run_<日時>/` に保存。
- ペルソナ固定ルール: 胸カップ固定(現在**G**)・年齢25〜35・髪型自由・体型自由だが肥満禁止・職業自動。
- ★**args でフォルダを渡すと壊れる**(stringify されて undefined → スキルディレクトリ内に `undefined/` フォルダが出来て git 汚染)。**Plan 段が `date` でフォルダを作り返す**自己完結型にして回避済み。

## ★破綻しない explicit 動画の型（実証）
i2v は先頭フレームの構図しか動かせない。エロくない/破綻する主因は「フレームに行為が写っていない」「非性的モーション」「男の全身や結合部を描く」こと。対策:
1. **男の全身を描かない**: (a) POV=男をカメラにしてフレーム外(騎乗位POV/正常位POV) (b) 壁ペニス(グローリーホール)=男を「壁から出たペニス1本」に置換(フェラ/手コキ)。
2. **臍(へそ)より上の構図に固定**＝結合部・股間・ペニスを一切フレームに入れない(AIが最も破綻する部位を映さない)。プロンプトに `framed above the navel, no genitals, no crotch, no penetration, no penis visible` を明記。
3. **モーションは縦バウンド**(胸が上下に揺れる/頭が上下)。→ wan-2.7-spicy が破綻なく explicit に動かせる。
- 実証: 騎乗位POV・正常位POV・グローリーホールフェラ とも成立。逆に男の全身(顔・胴・結合部)を描くと破綻。パイズリは z-image が手コキに流れ苦手。

## ★胸サイズの扱い＝バックエンドで真逆（重要）
- **z-image（フレーム/動画・無検閲）**: `very large G-cup breasts` を**明示的に書く**→反映。
- **Qwen-Edit（着衣・無検閲）**: `very large G-cup breasts` を**明示**＋**フィットした服**にする(ゆったり白衣だと胸が潰れる。前を開けフィットインナーで胸ライン)。書かないと普通体型になる(実機事故→修正で解決)。
- **Codex（シート・image_gen 検閲あり）**: 胸/バスト等の体型強調語を**一切書くと sexual 判定で拒否**。**書かず参照画像(busty な着衣)に体型を委ねる**と通り busty も保たれる。→ [[atlascloud-nsfw-image-and-pipeline]]

## 逆変換(NSFW画像→SFWシート)も可能
NSFW フレームの女性を切り出し→ローカル Qwen-Edit で着衣SFW化→Codex -i でシート。Codex に胸を書かないのが鍵(同上)。character-sheet-template.md の(D)節に記載。

関連: [[atlascloud-nsfw-image-and-pipeline]] [[openrouter-video-models-reference-support]] [[nsfw-models-chroma-noobai-wan-lora]] [[optimal-gen-models-table-and-new-model-eval]]
