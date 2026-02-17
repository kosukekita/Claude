# Running Playwright Code

## run-code コマンド

`run-code` で任意の Playwright コードを実行できる。`page` オブジェクトが引数として渡される。

```shell
playwright-cli run-code "async page => { /* your code */ }"
```

## 使用例

### 権限の付与

```shell
# 位置情報の許可
playwright-cli run-code "async page => {
  await page.context().grantPermissions(['geolocation']);
}"

# 位置情報を設定
playwright-cli run-code "async page => {
  await page.context().setGeolocation({ latitude: 35.6762, longitude: 139.6503 });
  await page.context().grantPermissions(['geolocation']);
}"
```

### メディアエミュレーション

```shell
# ダークモード
playwright-cli run-code "async page => {
  await page.emulateMedia({ colorScheme: 'dark' });
}"

# モバイルビューポート
playwright-cli run-code "async page => {
  await page.setViewportSize({ width: 375, height: 812 });
}"
```

### 待機

```shell
# セレクタの出現を待つ
playwright-cli run-code "async page => {
  await page.waitForSelector('.results');
}"

# ネットワーク応答を待つ
playwright-cli run-code "async page => {
  const response = await page.waitForResponse('**/api/data');
  console.log(response.status());
}"

# ナビゲーション完了を待つ
playwright-cli run-code "async page => {
  await page.waitForLoadState('networkidle');
}"
```

### ページ情報の取得

```shell
# ページタイトル
playwright-cli eval "document.title"

# 特定要素のテキスト
playwright-cli eval "el => el.textContent" e5

# カスタム JavaScript
playwright-cli run-code "async page => {
  const title = await page.title();
  const url = page.url();
  console.log(JSON.stringify({ title, url }));
}"
```
