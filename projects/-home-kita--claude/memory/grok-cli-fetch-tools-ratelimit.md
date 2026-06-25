---
name: grok-cli-fetch-tools-ratelimit
description: Grok Build CLIの取得系ツール(X取得/web検索)は連打でレート制限化し0件/タイムアウトになる。モデルは生きてもツールだけ抑制。Premium枠不足の疑いも
metadata: 
  node_type: memory
  type: reference
  originSessionId: 2d9b8ff1-3d69-49bb-bc7b-ba61669f3448
---

Grok Build CLI（`~/.grok/bin/grok`、X Premium/SuperGrokのOAuth認証）の**取得系ツール（X投稿取得・web検索）には実用上のレート制限がある**（2026-06-25に実証）。自動化でGrokに繰り返しデータ取得させる設計の前に必ず考慮する。

## 実証された挙動
- **最初の数回（間隔が空いた状態）は成功**: 1アカウントのX取得が3分20秒かけて完走、`===POST===`整形・URL・リポスト数・日本語要約まで正確に返した
- **連続で叩くと崩れる**: 11アカウントを連続呼び出ししたら全部10秒程度で「取得します」と言ったまま0件。間隔を空けて再試行しても0件のまま
- **web検索ツールも同様**: 複数SNSバズ集約をweb検索で頼んだら3分でタイムアウト（Terminated）、何も返さず
- **モデル本体は生きている**: 同じ状態で `grok models`→`logged in`、「1+1=?」→「2」即答。**認証もモデルも正常で、取得系ツールの実行だけが抑制される**のが特徴的な症状

## 原因（Claude+Codex両AI調査 2026-06-25、確証は得られず）
- **最有力(A)**: 短時間連打による一時的レート制限/クールダウン。時間を空ければ回復する性質。最初成功→連打で失敗のパターンが合致
- **否定できない(B)**: **公式上 Grok Build CLI は X Premium+ / SuperGrok 向け**（https://x.ai/cli に明記）。**Premium（無印）はプラン枠不足の可能性**。Premium+はGrok上限が高い。ユーザーも「今のプランでは難しそう」と見立て（2026-06-25）
- 公式ドキュメント(docs.x.ai)にCLI経由取得の制限明記なし。載っているのはAPI従量課金のRPS/TPMだけ
- 2026-05にxAIが有料Grokの動画/画像/音声機能をスロットリングした報道あり→ツール抑制は全般的傾向

## 対策・運用指針
- **連続呼び出しは避ける**: アカウント/クエリ間に90秒以上のウェイト＋0件時リトライ(指数バックオフ)。それでも連打が続くと詰まる
- **切り分け手順(Codex推奨)**: 24時間以上完全停止→1回だけ実行で取れれば(A)確定。24h後もダメなら同じ取得をGrok Web/Xアプリで試す→Webで取れCLIだけ0件ならCLI問題、Webでも制限ならプラン枠→Premium+/SuperGrok検討
- **Grok取得に依存する自動化は今のPremiumでは不安定**。確実にWeb集約したいなら Claude(WebSearch/WebFetch)が安定だが、それはsystemdタイマー無人実行から使えない（→ /schedule クラウドClaude cron が代替候補だが未検証）

## ★解決策(2026-06-25): 要約はローカルLLM、Web取得はr.jina.aiでGrok依存を消せる
- **Grokが要る工程は「取得」だけ。厳選・要約はGrok不要**: 厳選=数値ならJSソート、主観なら**ローカルLLM Ollama**。要約=**Ollama(qwen3.5)がGrok同等品質**(`localhost:11434/api/generate`, stream=false, /no_think, 約33秒/件, A6000で動作。`ollama list`で確認)。systemdタイマー無人からHTTP直叩きで使える(Claudeのツールと違いタイマーで動く)
- **Web取得は r.jina.ai プロキシでbot対策突破**: `curl -sL https://r.jina.ai/https://<URL>` でCloudflare/ModSecurityを突破しLLM向けクリーンMarkdown取得。生curlが403/Cloudflareで弾かれるサイト(socialbee等)も読める。**X特定アカウント以外のWeb情報なら、curl+r.jina.ai+Ollamaで完全にGrokゼロの自動化が組める**(MasukiResumaのsns-trends.mjsで実証)
- **Xの特定アカウント投稿取得だけはGrok固有**(Instagram APIも他人投稿不可、Web版はログイン壁)。ここだけGrok依存が残り、レート制限の影響を受ける
- 共通ヘルパー実装例: MasukiResuma `platforms/_lib/ollama-summarize.mjs`(summarizeJa/selectTopJa/ollamaUp)

関連: [[grok-prompt-keep-japanese]]（日本語プロンプト維持）, [[video-media-studio-skill]]（Grok画像/動画はサブスク枠で別挙動）
