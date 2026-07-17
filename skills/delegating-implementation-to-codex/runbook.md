---
type: reference
title: Codex /goal + agmsg 実行 runbook
description: Fable5がプラン、Codex+GPT-5.6 Sol+/goalが自走実装、agmsgで相談するフローの実コマンド集（2026-07-17 実機検証済み）
tags: [codex, goal, agmsg, workflow]
---

# Runbook — 実機検証済みコマンド（2026-07-17 / Linux akitaken）

検証済みの実測値: Codex TUI 起動 ≈15秒 / 単純 `/goal` 完走 10秒 /
agmsg 相談を挟んだ `/goal` 完走 50秒。

## 0. 前提セットアップ（各PC 1回・べき等）

```bash
bash ~/.claude/bin/setup-codex-latest-model.sh
```

これ1本で全部入る（正本。ここ以外にセットアップ手順を書かない）:
CLI最新化 → **PATH上の古い codex の影を現行版へ貼り替え** → `model = "gpt-5.6-sol"` →
`codex features enable goals` → **agmsg の導入/更新**。

agmsg のインストール先は `~/.agents/skills/agmsg/`（DB: `db/messages.db`、SQLite WAL）。
Claude Code には `/agmsg` コマンド、Codex には `$agmsg` スキルとして入り、
`~/.codex/config.toml` の `writable_roots` に db/teams/run が自動追加される。

## 1. チーム作成（プロジェクトごとに1回）

`join.sh` は**位置引数**（`--team` 等のフラグは受け付けない。フラグを渡すと
`team '--team' has no registered agents` という紛らわしいエラーになる）。

```bash
S=~/.agents/skills/agmsg/scripts
bash $S/join.sh <team> fable claude-code "$(pwd)"   # あなた（計画者・検証者）
bash $S/join.sh <team> impl  codex      "$(pwd)"   # Codex（実装者）
bash $S/team.sh <team>                              # 確認
```

## 2. Codex を起動して /goal を渡す

### 方法A: agmsg spawn（tmux 内にいるとき最短）

```bash
bash ~/.agents/skills/agmsg/scripts/spawn.sh codex impl \
  --project "$(pwd)" --team <team> --model gpt-5.6-sol \
  --boot-prompt '/goal <目標>。プランは ./.agent-plan.md。プランに無い判断が要るときは
bash ~/.agents/skills/agmsg/scripts/send.sh <team> impl fable "QUESTION: ..." で fable に聞き、
bash ~/.agents/skills/agmsg/scripts/inbox.sh <team> impl を20秒間隔でポーリングして返答を待て。'
```

`--boot-prompt` は codex に必須級（codex は Monitor を持たないので、spawn 後に
送ったメッセージはアイドルのセッションに届かない）。

### 方法B: tmux 直（spawn が使えない/細かく見たいとき）

```bash
T="env LD_LIBRARY_PATH= /usr/bin/tmux"     # anaconda の libtinfo 汚染回避（この環境固有）
$T new-session -d -s impl -c "$(pwd)" -x 220 -y 50
$T send-keys -t impl "codex -s workspace-write" Enter
# 起動を待つ（15秒前後）
until $T capture-pane -t impl -p | grep -q "directory: $(pwd)"; do sleep 2; done
$T send-keys -t impl "/goal <目標>"
$T send-keys -t impl Enter                  # ★ Enter は必ず別コマンドで送る
```

**罠:** `send-keys "text" Enter` を1コマンドで送ると文字列だけ入って未送信のまま
止まることがある。Enter は別に送る。

進捗の読み方（`capture-pane -t impl -p | tail -20`）:
- `• Goal active Objective: ...` → 受理された
- 右下 `Pursuing goal (Ns)` → 自走中
- 右下 `Goal achieved (Ns)` → 完了主張（**証拠ではない。SKILL.md の VERIFY へ**）
- `• Unrecognized command '/goal'` → セットアップ未了（§0へ）

## 3. 相談を受ける・答える（あなた側）

`send.sh` / `inbox.sh` も**位置引数**:

```bash
S=~/.agents/skills/agmsg/scripts
bash $S/inbox.sh <team> fable                      # 未読を見る（既読になる）
bash $S/send.sh  <team> fable impl "ANSWER: ..."   # 答える
bash $S/history.sh <team>                          # 全履歴
```

Claude Code 側は `/agmsg mode monitor` にすると SessionStart フック +
Monitor ツールで約5秒のプッシュ受信になる（推奨）。Codex 側は monitor 非対応
（`monitor=no`）なので、**Codex には自分でポーリングさせる**（boot-prompt に書く）。

実測ログ（この形が動く）:
```
impl → fable: QUESTION: what format should greet() return?
fable → impl: ANSWER: greet(name) must return exactly 'Konnichiwa, {name}-san!'
→ Codex: "Fable specified the exact format... implementing that now" → Goal achieved (50s)
```
Codex は `$agmsg` スキルを自発的に読んで送受信した（boot-prompt に手順を書けば確実）。

## 4. 片付け

```bash
S=~/.agents/skills/agmsg/scripts
bash $S/despawn.sh <team> fable impl        # spawn した場合
bash $S/leave.sh <team> impl
bash $S/leave.sh <team> fable               # 最後の1人が抜けるとチームも消える
env LD_LIBRARY_PATH= /usr/bin/tmux kill-session -t impl
```

## Fable 5 が使えないとき（バイオ系）

プランも Codex に作らせるが、**計画セッションと実装セッションは必ず分ける**
（同一セッションだと生成器＝評価者に戻る）。

```bash
# 1) プランだけ作らせる（実装させない）
codex exec -s read-only -m gpt-5.6-sol \
  "要件: <...>。実装はするな。.agent-plan.md に、目的/変更対象/受け入れ条件(pass-fail判定可能な形)/やらないこと だけを書け。" \
  > /dev/null

# 2) ユーザーが .agent-plan.md を承認

# 3) 別セッションで実装（§2）
```

## トラブルシュート

| 症状 | 原因 | 対処 |
|---|---|---|
| `The 'gpt-5.6-sol' model requires a newer version of Codex`（400） | PATH上に古い codex。npm prefix 外の孤児は `codex update` が永久に届かず、ログインシェル/tmux でだけ影になる | `bash ~/.claude/bin/setup-codex-latest-model.sh`（§0。影を検出して現行版へ貼り替える） |
| `Unrecognized command '/goal'` | CLI が古い / goals フラグ未設定 | 同上（`codex features enable goals` を含む） |
| tmux 内の codex だけ古い | ログインシェルの PATH 順が対話シェルと違う | 同上。`tmux` 内で `codex --version` を確認 |
| Codex が起動しっぱなしで無反応 | `send-keys "text" Enter` で文字列が未送信のまま | Enter を**別コマンド**で送る（§2 方法B） |
| Codex が質問を投げたまま止まる | あなたが inbox を見ていない | `inbox.sh` を定期的に回す（§3） |
| `team '--team' has no registered agents` | agmsg にフラグを渡した | 位置引数で渡す（§1・§3） |
| spawn した codex にメッセージが届かない | codex は monitor 非対応 | `--boot-prompt` にポーリング手順を書く（§2 方法A） |

方針・上限（人間チェックポイント2つ、トークン上限、サンドボックス）は **SKILL.md** が正本。
