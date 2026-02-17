# Request Mocking

## Basic Route Commands

```shell
# Block all images
playwright-cli route "**/*.jpg" --status=404
playwright-cli route "**/*.png" --status=404

# Mock API response
playwright-cli route "https://api.example.com/data" --body='{"mock": true}' --content-type=application/json

# Mock with specific status
playwright-cli route "https://api.example.com/users" --status=200 --body='[{"id":1,"name":"Test"}]'

# List active routes
playwright-cli route-list

# Remove specific route
playwright-cli unroute "**/*.jpg"

# Remove all routes
playwright-cli unroute
```

## Advanced Mocking with run-code

```shell
# Mock with custom headers
playwright-cli run-code "async page => {
  await page.route('**/api/**', route => {
    route.fulfill({
      status: 200,
      contentType: 'application/json',
      headers: { 'X-Custom': 'value' },
      body: JSON.stringify({ success: true })
    });
  });
}"

# Modify response body
playwright-cli run-code "async page => {
  await page.route('**/api/users', async route => {
    const response = await route.fetch();
    const json = await response.json();
    json.push({ id: 999, name: 'Injected User' });
    await route.fulfill({ response, body: JSON.stringify(json) });
  });
}"

# Abort specific requests
playwright-cli run-code "async page => {
  await page.route('**/*.{png,jpg,jpeg}', route => route.abort());
}"
```

## URL Pattern Matching

- `**/*.jpg` — 全ての .jpg ファイル
- `https://api.example.com/**` — 特定ドメインの全パス
- `**/api/v1/**` — パス内のパターンマッチ
