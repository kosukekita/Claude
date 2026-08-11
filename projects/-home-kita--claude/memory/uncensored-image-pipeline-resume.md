---
name: uncensored-image-pipeline-resume
description: 【再開用】HauhauCS無検閲LLM→z-image-turbo 2段CLIの続き。GPU開放後にJSON廃止修正＋U1/U2/U6を一気に通す
metadata: 
  node_type: memory
  type: project
  originSessionId: 0ed7d245-95b1-436b-8b15-d958d57a966b
  modified: 2026-08-11T01:59:22.839Z
---

2026-08-11 着手・GPU争奪でペンディング（ユーザーが「研究優先」選択）。GPU（研究ジョブ run_ab_physics が
GPU1、ComfyUI-mmh3 が GPU0）が空いたら再開する。

## できているもの
- Ollama 登録済み: `hf.co/wowmonkey/Qwen3.6-35B-A3B-Uncensored-HauhauCS-Aggressive-Q4_K_M:latest`
  （21GB Q4_K_M・35B-A3B MoE=active約3B・**思考モデル**）
- 実装済み: `skills/video-media-studio/scripts/gen_uncensored_image.py`（委譲型・6要素/リアル化/
  禁止語positive除外/clean_env/uv run 子プロセスで gen_image.py --backend z-image-turbo）
- 合格: U3(dry-run) / U4(引数エラー) / U5(モデル不在案内)
- プランは `~/.claude/.agent-plan-uncensored-image.md`

## ★確定した欠陥（GPU開放後にagyへ差し戻す・2件）
1. **`format:json` モードだとこの思考モデルは空の `{}` を返す**（4トークンで即終了・実装バグでない）。
   → generate_prompt を **JSON強制廃止**に変える: `format:json` を外し、system で
   `/no_think` ＋「ONLY the prompt text, no JSON, no preamble」を指示してプレーンテキストの
   画像プロンプトを直接生成させ、`<think>...</think>` を除去してから、コード側で
   `{prompt, negative}` に包む。few-shot（Idea:→Prompt:）で安定化。
2. **generate_prompt の urlopen にタイムアウトが無い**（現状 timeout 指定なし＝無限待ち）。
   → `timeout=600` を付ける（direct_video/haruka と同じ）。

## 再開手順（GPUが空いたら）
1. GPU 空き確認。HauhauCS がフルVRAMに載れば MoE で数秒応答になる（今はCPUオフロードで7秒/tok・激遅）
2. 上記2欠陥を agy に差し戻し（プレーンテキスト方式＋timeout）
3. 私が U1（--prompt-only で実プロンプト全文）→ U2（tattoo/文字/隆起ホクロがpositiveに無いか機械チェック）
4. U6: --prompt-only を外し z-image-turbo で実画像1枚→NSFW人物が破綻なく出るか目視
5. 合格で完了。用途はNSFW人物画像全般（フォトリアル）

関連: [[local-llm-roster-ollama]]（ローカルLLM台帳・HauhauCS追記候補）、[[background-waiter-design]]
（待ちは完了マーカーファイルで・pgrep -f 自爆に注意）
