---
name: sheet-factory-daily-sfw-loop
description: 毎朝9時JSTにSFWキャラシートを自動生成しpCloudに保存するsystemdループ（akitaken）。場所・運用コマンド・設計上の決定
metadata: 
  node_type: memory
  type: project
  originSessionId: d067b6fc-7d1c-46e7-adf2-f2c98dec84b1
---

**sheet-factory** = 毎朝 09:00 JST に SFW キャラクターシート1枚を自動生成する systemd --user ループ（akitaken、2026-07-08 稼働開始・初回実走OK）。[[video-media-studio-skill]] のキャラシート入口(A)のヘッドレス版。

- **場所**: スクリプト `~/media-out/sheet-factory/daily_sfw_sheet.mjs`（/usr/bin/node）、設計書 `README.md` 同居、ユニット `~/.config/systemd/user/sheet-factory.{service,timer}`（Persistent=true）
- **保存先**: `~/pCloudDrive/Data/NSFW/AIgenaratedSheet/YYYYMMDD_<名前>/`（sheet.png + persona.json/md + prompt.txt + run.log）。pCloud未マウント時は staging/ に退避→次回自動移送
- **フロー**: ペルソナ=Ollama gpt-oss:120b→qwen3.5→内蔵表（固定: 25-35歳/顔75点/**Gカップ**はコードで強制、職業カテゴリ10種+年齢は乱数で強制多様化=LLM任せだとイラストレーターに偏る実測、婚姻等は自動設定）→ Codex「Gカップ反復強調」→Codex婉曲→Grok日本語 の3試行 → ffprobe機械検証 → Gmail通知（シート添付=毎朝の人間レビュー）
- **★プロンプト設計（2026-07-08ユーザー確定・実機比較）**: 胸は3箇所反復（ペルソナ行/最重要条件「体型（大きな胸を含む）」/服装節）＋ペルソナ細部（顔立ち長文・スリーサイズ・雰囲気）は画像プロンプトから除外（希釈防止）＋服装=ペルソナが伝わる私服で体のライン出るトップス（白シャツ×ネイビーパンツ禁止）＋「スリム」「華奢」禁止。この形でGカップが服の上から明瞭に出る（Codex）。Grokは生成可だがラベル化け頻発=保険。正本=スキルreference/character-sheet-template.md(A)とmjsの両方（変更時は両方更新）
- **設計上の決定**: ①AppArmor sysctl=1（再起動で戻る）でも**自動修復しない**（検知・報告のみ。Claude Code分類器も自動化を拒否）— Codexスキップ→Grok降格し、修復dockerコマンドをメールで人間に提示 ②NSFW派生（入口B）は絶対に自動化しない（人間チェックポイント）③1日1枚（state.jsonの日付ゲート）・試行3回・各15分・RuntimeMaxSec=2100
- **運用**: 停止=`systemctl --user disable --now sheet-factory.timer` / 手動=`... start sheet-factory.service` / 同日再実行=`--force` / **同一ペルソナで描き直し=`--persona <persona.json>`**（Ollama を呼ばず外見・profile だけ引き継ぐ。実行メタ source/backend/status/dims/created は捨てる。出力は衝突ガードで `_名前-2` になる）
- **★2026-07-09 実障害（PATH起因の誤報）**: unit の PATH に `/usr/sbin` が無く `spawnSync("sysctl")` が ENOENT → `sysctl=undefined` → 「AppArmor 制限が有効」と誤報して Codex を不当スキップ（実際の値は 0 で Codex は使えた）。同時に ffprobe も PATH 外（anaconda のみ）で `dims=0xundefined` → 合格画像を FAILED 判定し exit 1。修正: procfs 直読み＋FFPROBE 絶対パス解決＋PNG/JPEG 自前ヘッダパース＋**寸法不明は FAILED でなく WARN**＋unit の PATH に /usr/sbin 追加。詳細と一般形は [[systemd-user-path-enoent-silent-misread]]。**メールの「★AppArmor 制限が有効（sysctl=undefined）」は誤報で、docker コマンドを打つ必要は無かった**（`sysctl=1` と実数字が出ていれば本物）
- **Codex は「Gカップ明示」を拒否する**: 2026-07-09 の実走で `codex-visible-bust` は exit=0 だが画像を出さず、婉曲版 `codex-euphemism`（「とてもグラマラスで胸元にボリュームのある体型」）で初めて生成された（1536x1024/2.1MB, status OK）。Codex 経路は事実上ほぼ常に婉曲版に落ちる前提で見る
- **★pCloudクライアントの同期詰まり（2026-07-08実障害）**: FUSEマウント正常・小ファイル同期OKでも**数MBの画像だけ無言でサーバー未到達**になる（長期常駐クライアントの劣化、~/.pcloud/Cache 200GB）。対策としてスクリプトに保存120秒後の**サーバー側突合＋pCloud API直接アップロード補完**を実装済み（digest認証、creds=~/.config/pcloud-link.env）。メールの「クラウド同期:」行で検知でき、続くならクライアント再起動。pCloud書き込みは「FUSEに書けた=届いた」ではない

**Why**: SFWシート→（手動で）NSFWシート派生する2段パイプラインの上流を無人化するユーザー要望。
**How to apply**: シート関連の相談が来たらこのループの存在を前提にする。フォルダ命名や保存形式を変えるときは mjs と README を両方更新。
