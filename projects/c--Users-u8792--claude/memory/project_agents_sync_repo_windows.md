---
name: agents-sync-repo-windows
description: スキル正本はgithub.com/kosukekita/agents（agents-sync-repo）へ移行済み。Windows機は未インストールで全スキル破損中→修復はinstall.ps1一発。skip-worktree防御適用済み
metadata: 
  node_type: memory
  type: project
  originSessionId: dfa0f49a-e019-46aa-bec2-d0f781950a94
  modified: 2026-07-30T06:53:12.782Z
---

2026-07-29 に全スキルの正本が **github.com/kosukekita/agents**（プライベート、通称 agents-sync-repo）へ移行された。Claude Code と Codex が同一ファイルを共有する設計（`~/.claude/skills/<name>` と `~/.agents/skills/<name>` は正本へのリンク）。Linux 機は systemd タイマーで2分毎に commit/rebase/push 同期。

**Windows 機（u8792）の状態（2026-07-30 時点）**: 移行コミットが Linux 絶対パスの symlink を ~/.claude git に載せたため、Windows では symlink がただのテキストファイルとして展開され **Skill ツールから全スキルが Unknown になる破損状態**。修復手順は repo README の正規手順どおり:

```powershell
# クローンは実施済み（%LOCALAPPDATA%\agents-sync-repo）。残りはこれだけ:
& "$env:LOCALAPPDATA\agents-sync-repo\install.ps1"
```

install.ps1 は既存物をバックアップ後、Claude/Codex 両方の skills へ**ジャンクション**を張り、2分毎の AgentSkillsSync スケジュールタスクを登録する（2026-07-30 に auto-mode 分類器がスクリプト実行・ジャンクション作成をブロックしたため未完。ユーザーが手動実行する必要あり）。

**適用済みの防御（Windows ローカル限定・同期に載らない）**: `~/.claude` の auto-push フックは `skills/` を明示的にステージするため、ジャンクション化後にゴミ差分（symlink削除＋実ファイル追加）をコミットして Linux 側を壊す危険があった。対策として skills/* 全53エントリに `git update-index --skip-worktree`、`.git/info/exclude` に `skills/` を追加済み。副作用: Linux 側で skills/* の symlink エントリが変更/削除されると auto-pull の rebase がエラーになりうる（可視エラーなので気づける）。

**スキル編集の正しい手順（Windows）**: `%LOCALAPPDATA%\agents-sync-repo\skills\<name>` を編集 → そのリポで commit → `git pull --rebase` → push。Linux 側は2分で自動反映。~/.claude/skills 側を直接編集しない（ポインタ/ジャンクションであり正本ではない）。関連 [[claude-sync-windows-linux]]
