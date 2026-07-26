---
name: project_remote_control_default
description: Remote Control をデフォルト有効化する現行の正解は settings.json の remoteControlAtStartup:true（v2.1.220実機確認）。/config パネルの見え方の罠・claude config 廃止・PSプロファイル併用も記録
metadata: 
  node_type: memory
  type: project
  originSessionId: b9b39ba7-af29-43a5-aed1-48512021f724
---

Claude Code の Remote Control（RC）を**毎回の起動でデフォルト有効**にする設定。2026-07-26 に v2.1.220 のバイナリ文字列解析で全面更新（旧記述「公式永続キー無し」は廃止）。

## 現行の正解（v2.1.220 実機確認）

- **公式永続キーは存在する**: `~/.claude/settings.json` に `"remoteControlAtStartup": true`（**フラットなboolean**。zodスキーマ `remoteControlAtStartup: v.boolean().optional()` をバイナリ内で確認）。
- **解決順序**（バイナリの `dfE()` 相当）: `projectSettings / localSettings に false があれば強制無効` → それ以外は `policySettings ?? flagSettings ?? userSettings(=~/.claude/settings.json) ?? グローバル設定(~/.claude.json)`。
- docs や claude-code-guide が言う `remoteControl.autoConnect` は**この版のバイナリに存在しない**（`autoConnect` のヒットは全部 `autoConnectIde` = IDE自動接続で別物）。docsと実装の乖離に注意。

## 「設定が消えた」ように見える罠（2026-07-26 実発生）

- `/config` パネルの「Enable Remote Control for all sessions」は**グローバル設定（~/.claude.json）を表示**し、そこにキーが無いと "default" 表示になる。settings.json 側に true があっても**パネル上は未設定に見える**。
- セッション起動時に未ログイン（認証切れ）だと RC ブリッジが立たず、その回のセッションは RC 無しになる。→ セッション内で `/remote-control` を実行すれば有効化/再接続できる。
- `claude config set -g` サブコマンドは**廃止済み**（unknown option）。グローバル設定を CLI から書く公式手段は無く、/config パネルか settings.json を使う。

## ベルト&サスペンダー（PowerShell ラッパー・維持中）

PS7: `C:/Users/u8792/OneDrive/ドキュメント/PowerShell/Microsoft.PowerShell_profile.ps1`
PS5.1: `C:/Users/u8792/OneDrive/ドキュメント/WindowsPowerShell/Microsoft.PowerShell_profile.ps1`（2026-07-26 追設）

```powershell
function claude { & 'C:/Users/u8792/AppData/Roaming/npm/claude.cmd' --remote-control @args }
function claude-plain { & 'C:/Users/u8792/AppData/Roaming/npm/claude.cmd' @args }
```

- Documents は OneDrive リダイレクト（`~/OneDrive/ドキュメント`）。`~/Documents` 直下を探しても無い。
- **プロファイル内のパスはフォワードスラッシュ必須**: バックスラッシュ区切りで書くと「バックスラッシュ + u8792」の並びがツール引数で Unicode エスケープ解釈されて漢字1文字（U+8792）に化け、ASCII保存時に `?` になってパスが壊れる（[[feedback_u8792_path_unicode_escape]]。2026-07-26 に実際に一度壊して書き直した）。
- 脱出口は `claude-plain`。

**Why:** settings.json の userSettings は解決チェーンに入っており単体で足りるが、/config パネルの見え方の罠と過去の「消えた」報告があるため、起動経路（ラッパー）と設定（settings.json）の二重化を維持する。

**How to apply:** 「RCが消えた」と言われたら ①settings.json の `remoteControlAtStartup` 確認 ②settings.local.json / プロジェクト側に false が無いか確認 ③現セッションは `/remote-control` で復旧 ④新PCならラッパー2本＋settings.json キーを設置。
