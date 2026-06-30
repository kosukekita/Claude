---
name: nonreal-nsfw-default-set
description: 非リアル系(アニメ/漫画/絵画調)NSFWの既定モデルセット。Chroma(manga,paint)+Pony V6XL(anime,manga)の4本。NoobAIは不採用。2026-06-30の9枚グリッド実機比較でユーザー確定
metadata:
  node_type: memory
  type: feedback
  originSessionId: 8fa33f41-3f7a-4f60-88ef-8e22b991175d
---

**非リアル系（アニメ／白黒漫画／絵画調）の NSFW 画像を出すときは、次の4組み合わせを既定で出す**（ユーザー恒久ルール・2026-06-30 確定）:

| スタイル | モデル | バックエンド |
|---|---|---|
| 油彩・絵画 | **Chroma** | `gen_image.py --backend chroma`（paint プロンプト） |
| 白黒漫画 | **Chroma** | `--backend chroma`（manga プロンプト） |
| 白黒漫画 | **Pony V6XL** | `--backend pony`（manga プロンプト） |
| カラーアニメ | **Pony V6XL** | `--backend pony`（anime プロンプト） |

**NoobAI-XL は不採用**（同条件で見劣りした）。白黒漫画も既定は Chroma manga と Pony manga の2本で、NoobAI / Manga Vision IL は予備に降格。

**Why**: 2026-06-30、同一被写体（絵画NSFW・跨ぎ見上げ・厚塗り筆致・温かい親密光・ニーリング）で **3モデル(Chroma/Pony/NoobAI) × 3スタイル(アニメ/白黒漫画/油彩) = 9枚グリッド**を出してユーザーが直接比較。結果、良かったのは **Chroma の manga と paint、Pony の anime と manga**。NoobAI は3スタイルとも微妙でユーザーが明確に外した。「次から非リアル系NSFWはこの4つを使うように設定して」と指示。

**How to apply**:
- 非リアル系NSFW（実写でない＝アニメ/漫画/絵画/イラスト調）の人物画像依頼では、まずこの4本（Chroma paint/manga・Pony anime/manga）で出して見せる。スタイル指定が1つに絞られていれば該当する1〜2本だけ使う。
- **Pony V6XL の必須作法**: ポジティブ先頭に `score_9, score_8_up, score_7_up, score_6_up,` を付け、**`source_anime` を使う（`source_pony` は furry/MLP 化するので絶対禁止）**。さらに negative に furry 系（`furry, anthro, animal ears, fur, pony, my little pony, snout`）を入れる。Pony は `gen_image.py` に導入済み（allowlist＋force_euler スケジューラ。EDMDPMSolver だと純ノイズになるため EulerDiscreteScheduler 強制）。
- **Chroma** は自然言語英語が最良。`oil painting / visible brush strokes` をポジ、`photo/photorealistic` をネガに。
- 入れ墨除去は全モデルとも negative に `tattoo, tattoos, body ink, lettering on skin`。
- フォトリアル（実写系）NSFW はこの話と別軸。写実は Klein True-V3、油彩写実は Chroma（[[nsfw-painterly-models-research]] [[flux2-klein-truev3-setup]] 参照）。
- 正本は video-media-studio SKILL.md「NSFW 画像のモデル使い分け」表（更新済み）。この記憶はそれを横断検索可能にする補助。

関連: [[optimal-gen-models-table-and-new-model-eval]] [[nsfw-painterly-models-research]] [[nsfw-models-chroma-noobai-wan-lora]] [[manga-bw-nsfw-models]] [[person-image-6elements-confirm-before-fill]] [[video-media-studio-skill]]
