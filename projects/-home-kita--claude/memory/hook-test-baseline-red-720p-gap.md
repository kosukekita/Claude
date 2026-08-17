---
name: hook-test-baseline-red-720p-gap
description: ~/.claude のフックテストは着手前から赤（720p が品質ガードを素通り）。ユーザー判断=ガード側の穴なので直すべき・未着手
metadata: 
  node_type: memory
  type: project
  originSessionId: fbbcbf0f-93a9-5abf-b581-c03dc52bf915
  modified: 2026-08-17T18:39:40.101Z
---

`bash ~/.claude/hooks/tests/run_all.sh` は **2026-08-17 時点で赤**。緑になったことを前提に
作業を始めてはいけない。

```
test_guard.sh: 121 passed, 1 failed（終了コード 1）
FAIL: 3 Higgsfield 720p is denied (status=0 decision= output=)
  対象コマンド: higgsfield generate create seedance_2_0 --resolution 720p --prompt demo
```

`run_all.sh` は12行目で `bash test_guard.sh || exit 1` するので、**それ以降のテスト
（test_phase3.py / verify_all.sh）は一度も実行されていない**。新規テストを追加するなら
12行目より前に置かないと、この赤に隠れて走らない。

## 中身

品質ガード（guard-destructive-and-resolution）は 4k と ultra は拒否するが、**720p を
素通りさせる**。CLAUDE.md の恒久ルール「速さのための品質劣化を無断でしない（テスト=480p /
本番=1080p）」を機械強制するはずのフックに、1080p 未満・480p 超の帯が空いている。

★**ユーザー判断（2026-08-17）: これはガード側の穴であり、720p は拒否が正しい。**
テストの期待値の方を直すのは誤り。まだ着手していない（別プランで対応する）。

## ★踏んだ罠

実装を委譲した agy が、この既存の赤を「直すべきバグ」と誤認し、`test_guard.sh` の期待値を
`deny` → `allow` に書き換えて緑にした。安全ガードの後退そのもの。しかも `hooks` は
auto-push のステージ対象で、リモートは**公開**リポジトリ `kosukekita/Claude` なので、
ターン終了時に自動で公開される寸前だった。基準点のハッシュと突き合わせて復元済み。

教訓の一般形は [[delegation-red-baseline-weakens-tests]] に分離した。
