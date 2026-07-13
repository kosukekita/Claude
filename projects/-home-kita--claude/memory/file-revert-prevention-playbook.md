---
name: file-revert-prevention-playbook
description: ユーザーの手動編集をrevertさせない機構詳細(guard/snapshotフック・absorb-before-regenerate・3-wayベース照合)
metadata: 
  node_type: memory
  type: reference
  originSessionId: 7f792248-9bef-40fb-8283-33d15119eae9
---

CLAUDE.md「ファイルの手動編集を壊さない」の機構・実装詳細（行動ルールの核はCLAUDE.md本文に残す＝ディスクの現物が正／編集前に再読込／渡した成果物は最小差分で局所編集／手動削除は復活させない／再生成が必要なら手編集を先にソースへ吸収／迷ったら確認）。

## 補足フック（2026-07-13導入・全fail-open）
- PreToolUse `guard-file-revert.ps1`: Write/Edit対象が「最後に見た/書いた」内容から外部変更されていれば exit2 でブロック。
- PostToolUse `record-file-snapshot.ps1`: Read/Write/Editごとにhashを `~/.claude/state/file-snapshots/` に記録。
- `warn-bash-overwrite.ps1`: 上書き系Bashに助言。
- ★**Bashサブプロセス内の書き込みは機械的に止められない**ので、この規律(特に丸ごと再生成の禁止)が最終防波堤。

## 生成スクリプトの型: absorb-before-regenerate / 3-wayベース照合
ソース(本文.txt)→出力(.docx)を再生成するスクリプトは、前回生成時の本文を「ベース」として横に保存し、再生成直前に:
- **出力==ベース** → 手編集なし。ソースから普通に再生成。
- **出力≠ベース かつ ソース==ベース** → ユーザーだけが出力を直した → **出力→ソースへ吸収**してから再生成(手編集保持)。これが「手編集をソースへ自動反映」の壊れない実装。
- **出力≠ベース かつ ソース≠ベース** → 両方直した=**競合**。出力を触らず停止、出力の現内容を別ファイルに書き出して人手照合(自動マージしない)。
成功したら「ベース:=書き込んだソース」に更新。編集前に手編集を吸い上げる `--sync-only` も用意すると `①出力→ソース吸収→②ソース編集→③再生成` で安全。
- 参照実装: `P:/Code/Research/PINN/UKA_FEA_PINN/grant_IFPMR_overseas/figures/build_abroad_figure.py`(docxセルから本文抽出し `abroad_body.txt`+`abroad_body.base.txt` で3-way判定)。
- docx↔テキストのような**往復可能な形式**でのみ吸収成立。往復でロスする要素(図位置・書式)はソースを正とし、ユーザーに「本文はWordで直してよい/図はソースから」と伝える。

関連: [[recommendation-letter-docx-editing]] [[concurrent-claude-autopush-clobbers-merge]]
