---
name: realism-naturalization-default-on
description: スタイル未指定の実写画像は「リアル化(自然化)プロンプト」を提案せず既定で自動適用する（2026-07-09ユーザー確定）
metadata: 
  node_type: memory
  type: feedback
  originSessionId: 7f792248-9bef-40fb-8283-33d15119eae9
---

**★恒久ルール（2026-07-09 ユーザー確定）: 画像生成でユーザーがスタイルを指定しない場合、フォトリアル＋「リアル化(自然化)プロンプト」を既定で自動適用する。** 以前の『自然化プロンプトは提案して OK をもらってから足す』は撤回。「何も言われなければリアル画像を作るスキルを既定で使う」。

- **既定で足すスターター3個**: ①「SNSに実在しそうな自然な写真にしてください」②「過度な加工感・つるつるした肌をなくし、毛穴や肌の細かい質感を残してください」③「CG・3Dレンダーっぽさをなくし、実際のカメラで撮った写真にしてください」。症状が具体的なら `reference/realism-naturalization-prompts.md` の対応表で 2〜3 個追加。30個一括投入はしない（薄まる）。
- **外すのは**: ユーザーが明示的にイラスト/アニメ等のスタイルを指定した時、または「リアル化不要」と言った時**だけ**。
- **★「リアル感」＝人間の肌のリアル感（2026-07-13 ユーザー確定・恒久）**: ユーザーが「リアル感」「リアルにして」「リアル感をもっと」と言ったら、一般的な"実写っぽさ"でなく **人間の肌の質感を最優先で強く出す**。具体= `hyper-realistic human skin with visible pores, fine skin texture, subtle natural imperfections and vellus hair, realistic subsurface scattering and a faint natural sheen of sweat, no airbrushing, no smooth plastic doll skin, no CGI, no 3d render, looks like a real unretouched photograph`。スターター②「毛穴/肌質感」を最強度で効かせる。実例: バーテンダーcocktail storyboard(2026-07-13)で「肌のリアル感をもっと」と指示され、肌リアリズム句を強化して解決。
- **渡し方はバックエンド別**: 指示追従系（Codex/Grok/OpenRouter画像=Nano Banana等/Qwen-Edit）は日本語自然文のまま追記（Grokは翻訳禁止）。ローカル diffusion（z-image/FLUX/SDXL/Chroma/Klein）は同ファイルのキーワード変換表でポジ/ネガに変換。
- **キャラシート等の資料形式**では、肌質感・自然光・no-CG の naturalization は足すが、SNS 的な生活感背景などレイアウトと矛盾する項目は入れない。character-sheet-template.md（入口A）と sheet-factory `daily_sfw_sheet.mjs` の SFW プロンプトにも「リアルさの指定」節を組み込み済み（毎朝の Codex 自動シートも既定でリアル化される）。

**Why**: Nano Banana 2（OpenRouter `google/gemini-3.1-flash-image` / AtlasCloud `google/nano-banana-2`）で素のプロンプト（「実写調」の一文だけ）を投げたら、CG・3Dレンダー臭のツルツル肌になった（2026-07-09 実機）。リアル化3行を足したら肌の毛穴・自然光が出て実写らしくなった。同じシートでも Codex 版の方が元々実写寄りだが、Nano Banana 系は特にリアル化が要る。

**How to apply**: 実写人物/シート画像を作るとき、ユーザーがスタイルを言っていなければ黙ってスターター3個を仕上げ層に足す（確認不要）。ただし**内容（6要素=衣装/シーン/光/構図/枚数、動画のシーン・動作）は従来どおり勝手に足さず確認**する＝「内容＝ユーザーの領域／品質(リアル化)＝既定で底上げ」の切り分け。関連: [[person-image-6elements-confirm-before-fill]] [[optimal-gen-models-table-and-new-model-eval]] [[openrouter-image-gen-quirks]]
