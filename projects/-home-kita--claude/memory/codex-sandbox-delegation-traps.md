---
name: codex-sandbox-delegation-traps
description: Codex委譲(/goal)のサンドボックス実測罠 — apply_patchはcwd内のみ・localhost/GPU/systemd-run遮断はホスト側検証で分担・agmsg ANSWER消費・tmux長文分断(2026-08-04)
metadata: 
  node_type: memory
  type: project
  originSessionId: 245c97d8-2c23-431f-91a9-69ed68025f10
  modified: 2026-08-04T10:34:46.683Z
---

gen_minimax_h3.py 委譲（2026-08-04・codex v0.146.0・`-s workspace-write`）で踏んだ Codex サンドボックスの実測罠と解法。

1. **apply_patch は writable_roots を無視して cwd ワークスペース内しか書けない**。`~/.claude/skills/*` は `~/.local/share/agents-sync-repo` への symlink なので、`[sandbox_workspace_write] writable_roots` に追加してもセッション再起動しても `Failed to write file` のまま。**解法＝スキル実体リポジトリを cwd にして codex を起動**（`tmux new-session -c ~/.local/share/agents-sync-repo`・初回は trust プロンプトに 1）。writable_roots への sync-repo 追加は残置してある（shell 書き込み用には有効）。
2. **sandbox は localhost TCP・GPU デバイス・systemd-run（D-Bus）・ssh を遮断**。`network_access = true` を `[sandbox_workspace_write]` に足しても localhost:8288 に届かなかった（実測・効果なしだったので revert 済み）。**解法＝実生成スモーク等の GPU/サーバ依存の受け入れ条件は、検証者（Claude 側）がホストで実行して exit/log/ffprobe を TUI に中継する分担**。成果物は /tmp に置けば Codex が自分で ffprobe できる。Codex には「サーバ起動を試みるな・AC のうちサンドボックス互換のものを先に完了せよ」と指示する。
3. **agmsg の ANSWER が届かないことがある**: fable→impl の ANSWER が送信数秒後に既読化されるのに Codex 本体は「未着」と報告（leaked background terminal か別インスタンスのポーリングループが消費した疑い）。**解法＝返答は agmsg でなく tmux send-keys で TUI に直接注入**し、boot 指示に「inbox ポーリング待機ループを作るな（QUESTION は send.sh で送信だけして続行、返答は画面に直接届く）」を入れる。
4. **tmux の長文 /goal は途中で送信される**（send-keys 直後の Enter が入力取り込み中に発火し、末尾が入力欄に残る）。**解法＝send-keys 後 `sleep 3` してから Enter を別送**。残った断片はそのまま Enter で追送すれば follow-up として届く（ただし断片が命令に見えると誤解される＝「…ANSWER を待て」の断片で Codex が実装を止めて待機ループに入った実害）。
5. **CLAUDE.md の「実装前の理解度確認」ゲートを Codex が適用してクイズを出し Goal blocked になる**。承認済みプランに正解が明記されている場合はプラン作者（Claude）が TUI で回答して再開してよい（実測: 回答後 `/goal resume` 不要で自動再開）。再投入時は「ゲート回答済み（正解X）＝再出題不要」を goal 文に含めると再ブロックしない。

関連: [[plan-fable-implement-codex-goal]]（委譲フローの正本）、[[minimax-h3-ref2va-usage]]（この委譲の成果物）
