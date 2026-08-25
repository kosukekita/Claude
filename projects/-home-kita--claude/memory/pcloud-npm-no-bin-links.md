---
name: pcloud-npm-no-bin-links
description: pCloud配下では npm install に --no-bin-links が要る。FUSEがsymlinkを実装していないため
metadata:
  type: reference
---

ユーザー指示（2026-08-26）: **pCloud配下で npm を使うときは `npm install --no-bin-links` で実行する。**

## 症状と原因（実測 2026-08-25）

```
npm ci / npm install
  → npm error code ENOSYS
    npm error syscall symlink
    npm error dest .../node_modules/.bin/esbuild
```

pCloud は FUSE（`pCloud.fs`）で **`symlink()` を実装していない**。
npm は `node_modules/.bin/` に実行ファイルへの symlink を張るので、そこで落ちる。

**誤解しやすい点**: npm 自体は PC 側（`/usr/bin/npm`）にある。問題はツールの置き場所ではなく、
**`node_modules` の生成先**。`npm install` は cwd の下に作るので、cwd が pCloud なら pCloud に作られる。

```
ln -s で検証:  pCloud配下 ❌「関数は実装されていません」 / /tmp ✅ / $HOME(xfs) ✅
```

## 回避策と、その副作用

```bash
npm install --no-bin-links     # → added N packages ✅
```

パッケージの読み込みは正常（`require()` も import も通る）。

**ただし `node_modules/.bin/` が空になる**ので、副作用がある。

```
npm run <script>  でパッケージのコマンド名を呼ぶと  → sh: 1: xxx: not found
node node_modules/<pkg>/<bin>.js  と書けば          → 動く
```

つまり `npm run build` のような**標準的な script が全部動かなくなる**。
Astro / Vite / webpack など**ビルドを伴うツールを常用するなら、リポジトリを pCloud の外
（例 `~/Code/<project>`）に移すのが素直**。フラグで回避し続けると、公式手順から外れ、
npm の更新でパスが変わるたびに壊れる。

## 使い分け

| 状況 | やること |
|---|---|
| 単発でパッケージを入れて `require` したいだけ | `--no-bin-links` で足りる |
| CLI を叩きたい | `npx <pkg>@<version>` （npmキャッシュはpCloud外なので普通に動く） |
| ビルド工程を常用する | **リポジトリを pCloud の外へ移す** |

wrangler の実行は `npx --yes wrangler@<version>` で回避した実績あり（polaro）。

関連: [[claude-config-overhaul-2026-08]]
