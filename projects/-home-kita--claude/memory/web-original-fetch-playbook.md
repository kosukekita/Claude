---
name: web-original-fetch-playbook
description: 「このサイトを参照して」指示で原文を機械取得する手順(WebFetch→curl+埋込JSON→ブラウザ→Jina→Codex相談)。自作代替禁止
metadata: 
  node_type: memory
  type: reference
  originSessionId: 7f792248-9bef-40fb-8283-33d15119eae9
---

CLAUDE.md「Web取得」の手順詳細（行動ルールの核はCLAUDE.md本文＝URL付きで「参照して」なら実データ/原文を取得して使う・自作/記憶/要約で代替しない・取れるまで粘る・Jinaは第三者プロキシなので機密/認証/PII禁止）。

## 取得の手筋（この順で粘る。1つ失敗で即あきらめず次へ）
1. **WebFetch**。ただし要約モデルが長文を切る/逐語転載を拒むことあり → 原文が要るなら次へ。
2. **`curl -sL -A "Mozilla/5.0" <URL>` で生HTML/JS取得**し、`data-copy`等のデータ属性・`__NEXT_DATA__`・埋め込みJSON・参照される`.js`/`.json`から**原文文字列を機械抽出**(grep/node/jq)。SPAでもHTML/JSバンドルにデータが入っていることが多い(実際 aicameramovements.com は `data-copy` 属性に全46プロンプト)。
3. **ブラウザ自動化(claude-in-chrome)で描画後DOMを読む**(`get_page_text`/`read_page`/`javascript_tool` で document・ページ内変数・fetch を直接叩く/コピー用ボタンの値やdata属性を取る)。
4. **r.jina.aiプロキシ**(`https://r.jina.ai/<元URL>`・公開/PIIなしのみ)。※プロキシ側モデルが逐語を拒むことあり。
5. **詰まったらCodexに取得方法を相談**(データファイル特定・DevToolsの見方・具体的なcurl/grep)。

**取れるまで粘るのが原則。** 手を尽くして本当に不能な時だけユーザーに相談(黙って自作に逃げない)。逐語全文転載が用途上問題になり得る時は、**まず原文を機械取得したうえで**出典明記・必要なら要約/再構成(先に自作は禁止)。

## Jina Reader の注意
第三者サーバ(Jina AI)に対象URLを送るプロキシ。**認証付き・社内/機密・個人情報URLには使わない**(医学研究データ・要ログインは厳禁)。ログイン済みページ取得は chrome-devtools-mcp(既存ログインのChromeに接続)。
