---
name: recommendation-letter-docx-editing
description: 候補者推薦書docxを書式保持で書き換える手順とcv-profile連携 — run単位置換・JTM論文/UKA_FEA_PINN・全角字数1200制約
metadata:
  node_type: memory
  type: reference
---

喜多氏の「候補者推薦書」(`~/Downloads/候補者推薦書_喜多洸介.docx`)を書き換えた実務知見（2026-06-28）。同種の推薦書/申請書docx編集で再利用可。

## データの出どころ
- 業績・経歴は **cv-profileスキル**（`~/.claude/skills/cv-profile/references/achievements.md` と `career.md`）が一次ソース。論文番号17 = **Journal of Translational Medicine 2026;24:8079**（筆頭, DOI 10.1186/s12967-026-08079-0）。被引用回数は **Semantic Scholar API + OpenAlex API** で確認（2026-06時点で **0回**、新しい論文ゆえ）。
- 新研究課題 **UKA_FEA_PINN** の一次資料は `P:/Code/Research/PINN/UKA_FEA_PINN/CLAUDE.md`（単顆膝関節置換UKA脛骨の設置条件θ→脛骨応力場をFEBio-FEA教師＋PINNサロゲートで高速予測、本質はデータ効率、術前安全域マップで骨折/沈下回避）。**別フォルダの `~/Downloads/PINN_膝関節接触力研究提案.docx` 等はOWHTO/TKO接触力推定の別テーマ**なので混同しない（検証AIがこれを「材料」と誤認し捏造判定する罠あり）。

## docx書式保持編集の鉄則（python-docx）
- **段落の run の `.text` を差し替える**のがフォント/サイズ/太字を温存する最安全な方法。新規に段落を `add_paragraph` すると書式が飛ぶ。
- 「見出し：値」型の段落は run0(太字ラベル)+run1(値)。値だけ置換するなら run1 を書き換え、余分な run は `.text=""` に。
- 段落を増やすには `copy.deepcopy(src._p)` して `anchor._p.addnext(new_p)` → `Paragraph(new_p, parent)` でラップしてから run を書く。
- 元テンプレ構造(実測): P0タイトル中央16pt太字 / P1研究課題中央10pt / 本文10pt / 業績9.5pt / Times New Roman。本文は元は1段落に全角スペース区切りだったが、4段落改行に変えて可読性向上。

## ★Windows固有の罠
- **コンソール出力が cp932 で文字化け/UnicodeEncodeError**（特に `—` U+2014）。検証printは避け、**結果はUTF-8ファイルに書いてRead** するか、`json.dumps(..., ensure_ascii=True)` で出す。
- パスは必ず **フォワードスラッシュ** `C:/Users/u8792/...`（バックスラッシュ+u8792はUnicodeエスケープ化けの既知問題）。
- 上書き前に必ずバックアップ(`cp ..._backup_<ts>.docx`)。

## 字数・文体の確定仕様（この推薦書）
- 本文は **全角1,200字以内**（句読点記号も1字、改行は数えない）。`len("".join(paras))` で実測。
- 文体「である」調・三人称「氏」・推薦者視点。査読者は**医師**＝工学の専門用語(教師データ/マルチモーダル/PINN)は可だが、損失関数・偏微分方程式等の内部用語は使わない。
- 数値で確定値が無いものは **全角アンダースコア `＿＿＿`** のプレースホルダ（例 `R²＝＿＿＿`）。捏造しない。「5例」「n=5」はユーザー提供の確定事実。
- **必須の論理**: 「これまでの業績が新研究にどう活きるか」の橋渡しを明示（マルチモーダル統合経験→異種情報統合の素地、欠損頑健設計→少教師PINNの素地、既存データ完結の姿勢→教師量産の発想に直結、大規模解析実装力→FEA教師生成を支える、整形外科臨床知→課題設定自体が強み）。これが無いと推薦書として不可。

関連: [[fugu-ultra-llm-reasoning-mandatory]]（日本語校正に使った）, [[academic-writing-stop-gate-criterion]]
