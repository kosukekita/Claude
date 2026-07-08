---
name: grok-prompt-json-acp-images
description: "Grok CLIのヘッドレス画像添付の実態(2026-07-08実測): --prompt-jsonのACPブロックで「見る」は可能、「参照して生成」は依然不可"
metadata: 
  node_type: memory
  type: reference
  originSessionId: d067b6fc-7d1c-46e7-adf2-f2c98dec84b1
---

**Grok CLI（0.2.60）のヘッドレス参照画像の実態**（2026-07-08 実機検証。[[grok-prompt-keep-japanese]] の image_edit 不発火知見の更新版）。

- **✅ 画像を「見せる」ことは可能になった**: `grok --prompt-json '<ACPコンテンツブロックのJSON配列>'`。受理される type は `text, image, audio, resource_link, resource`（`image_url` は不可）。
  - `{"type":"image","data":"<base64>","mimeType":"image/jpeg"}` — argv 上限（1引数128KB）があるので縮小画像向け。
  - **`{"type":"resource_link","uri":"file:///abs/path.png","name":"x.png","mimeType":"image/png"}` が本命** — フル解像度のローカルファイルを渡せ、モデルはシートの服装の細部まで正確に読めた。
- **❌「参照画像から生成」（image_edit / 同一人物生成）は依然ヘッドレス不可**: `-p` でも `--prompt-json`+resource_link でも、生成を指示すると **400秒無応答でハング**（ツールが発火しない。2026-06-23 の知見は 0.2.60 でも有効）。
- **運用結論**: 同一人物のリファレンス付き生成は **SFW=Codex `-i`＋stdin / NSFW=ローカルQwen-Edit** の従来ルール継続。Grok は「画像の内容分析・レビュー」用途にだけ prompt-json 添付を使う（ヘッドレスで画像批評ができるようになったのは大きい）。
- Codex に `-i` で参照+プロンプトを渡すときは **stdin 必須**（位置引数と併用すると即 exit 1、エラーメッセージなしのことがある。スクリプトでは `input:` オプションで渡す）。

**Why**: ユーザーから「Grokは参照画像を取れるはず」と指摘され再検証→添付(vision)と参照生成(image_edit)で可否が分かれることが判明。
**How to apply**: Grokにヘッドレスで画像を見せたい場合のみ --prompt-json + resource_link。生成はさせない（ハングする）。
