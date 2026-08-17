---
name: natural-japanese-skill-install
description: natural-japanese スキル導入の構成・ローカル改変3点・スキル実体はagents-sync-repoに置く規約と自己参照symlinkの罠・自分の日本語の実測癖
metadata: 
  node_type: memory
  type: project
  originSessionId: fbbcbf0f-93a9-5abf-b581-c03dc52bf915
  modified: 2026-08-17T13:08:30.424Z
---

日本語文書の AI 臭除去スキル [coji/natural-japanese](https://github.com/coji/natural-japanese) を 2026-08-17 に導入した（v1.4.0 / commit `0f1cc1c` / MIT）。設計は「検出は機械（sudachipy の lint.py）、判断は AI」＋「事後修正より生成時制約（文体憲法12箇条）」。

## ★スキル導入の場所の規約（ここを間違えた）

`~/.claude/skills/*` は**全て symlink** で、実体は `~/.local/share/agents-sync-repo/skills/`（remote = kosukekita/agents）。`~/.agents/skills/*`（Codex 側）も同じ実体を指す。

- 新規スキルは**必ず sync repo 側に実体を置き**、`bash ~/.local/share/agents-sync-repo/install.sh` でリンクを張る。これで全PC＋Codex に同期される
- `~/.claude/skills/` は `.gitignore` の `/skills/` 対象なので、そこに実体を置くと ~/.claude の git には一切乗らない
- **罠**: `~/.claude/skills/<名前>` に実体ディレクトリを作った状態で sync/install が走ると、`ln -s A B` の B が既存ディレクトリのため**リンクが中に生える**（`<名前>/<名前>` → 自分自身の自己参照 symlink）。ツリー走査が無限再帰しうる。実体を sync repo へ移したあと `find <skill> -type l` で 0 件を確認する
- `__pycache__` は sync repo の .gitignore（`**/__pycache__/`）で除外済み。lint 実行のたび再生成されるが放置でよい
- 外部スキルの自動追従枠 `external-skills.tsv` は **SKILL.md がリポジトリ直下にある場合のみ**使える。natural-japanese は `skills/natural-japanese/SKILL.md` と入れ子なので使えず、`skills/` に vendoring した

## ローカル改変（更新時はこの3点だけ残して差分マージ）

1. description 末尾2文＝ネガティブトリガー（学術論文は academic-writing／チャット応答には適用しない）
2. 「## この環境での運用（ローカル追記）」節＝出所・パス・他スキル境界・実測癖
3. `uv run scripts/*.py` → `uv run ~/.claude/skills/natural-japanese/scripts/*.py`（上流は cwd=スキルディレクトリ前提で、この環境では動かない。上流内でも表記が2種類に割れていた）

`scripts/*.py` は上流の資産なので自分で書き換えず Codex に委譲する。

## ★自分の日本語の実測癖（2026-08-17・導入前ベースライン）

過去の日本語文書107件（memory と `.agent-plan-*.md`）を lint にかけた結果、findings 35件。内訳は `low_burstiness`（文長が揃いすぎ）24件、`uniform_paragraph_structure`、`antithesis_repetition`（「〜ではなく」の反復）、`forbidden_phrase` 1件のみ。

弱点は語彙ではなくリズムと構造の側にある。禁止語を避けるだけでは自分の AI 臭は消えないので、書く時点で長短を混ぜ、節ごとに厚みを変えるほうが効く。関連: [[claude-config-overhaul-2026-08]]
