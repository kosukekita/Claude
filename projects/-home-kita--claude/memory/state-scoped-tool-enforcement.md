---
name: state-scoped-tool-enforcement
description: statewright(2026-08-10評価・不採用)から抽出した「状態ごとのツール制限」の設計アイデア。Iron Law違反が再発したらネイティブフックで実装する
metadata: 
  node_type: memory
  type: reference
  originSessionId: 0ed7d245-95b1-436b-8b15-d958d57a966b
  modified: 2026-08-10T10:16:06.501Z
---

statewright（状態機械でエージェントのツール空間を状態別に制限する枠組み）は FSL ライセンス＋
クラウド依存で**不採用**（ユーザー確定 2026-08-10）。ただし中核アイデアは我々の訂正OS
（機械判定できる違反はフックで実行前ブロック）と同型なので、**ネイティブ実装の設計案**として抽出:

1. **フェーズファイル方式のツール封鎖（本命・Iron Law の機械的強制）**
   `~/.claude/phase` に現在フェーズ（plan / implement / verify）を書き、PreToolUse フックが
   Edit/Write の対象パスを見て判定: フェーズが implement 以外のとき**コードファイル
   （.py .js .mjs .sh .ts 等）への Edit/Write をブロック**。プラン(.agent-plan*.md)・記憶・
   SKILL.md・台帳JSONは常に許可。フェーズ変更はユーザー指示があった時だけ書き換える運用。
   → 「Claude はコードを書かない」が規律文書でなく**実行前拒否**になる。
2. **状態別コマンド接頭辞許可**: 既存 block-dangerous をフェーズ対応に拡張（verify 中は
   テスト実行系のみ許可等）。
3. **編集ガード**: 1回の Edit の行数上限・1状態あたりのファイル数上限（暴走編集の検知）。
4. **遷移承認**: フェーズ遷移自体を「ユーザーの明示発言のみ」とする（フックはフラグファイルの
   タイムスタンプ/作成者を検査するだけでよい）。
5. **裏付けになる知見**: statewright の実測で、ツール空間を状態で絞ると小型ローカルモデルの
   SWE-bench 通過が 2/10→10/10。**「安いモデル×狭いツール」は品質戦略として成立**＝
   我々の Workflow 層別け（finder=sonnet読み取り専用）や Explore エージェント（read-only）の
   方向性を独立に支持する。

**実装トリガー**: Iron Law 違反（Claude が自分でコードを書く/直す）が次に実際に起きたとき、
訂正OSの手順で 1 を Codex/agy に実装させる（先回りで作らない＝「痛みが出てから足す」）。
関連: [[claude-config-overhaul-2026-08]]（設定は足すより削る方針の当日に枠組み導入は逆行、の判断記録）
