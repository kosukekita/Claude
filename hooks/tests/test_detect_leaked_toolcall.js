const assert = require('assert');
const fs = require('fs');
const os = require('os');
const path = require('path');
const { spawnSync } = require('child_process');

const hooksDir = path.join(__dirname, '..');
const hookPath = path.join(hooksDir, 'detect-leaked-toolcall.mjs');
const repoDir = path.join(hooksDir, '..');
const memoryPath = path.join(repoDir, 'projects/-home-kita--claude/memory/leaked-toolcall-hook-linux.md');

const tempDir = fs.mkdtempSync(path.join(os.tmpdir(), 'test-leaked-toolcall-'));

process.on('exit', () => {
  try {
    fs.rmSync(tempDir, { recursive: true, force: true });
  } catch {}
});

function run(name, fn) {
  try {
    fn();
    console.log(`PASS: ${name}`);
  } catch (error) {
    console.error(`FAIL: ${name}`);
    console.error(error.stack || error.message);
    process.exitCode = 1;
  }
}

function runHook(payload, env = {}) {
  const input = typeof payload === 'string' ? payload : JSON.stringify(payload);
  const result = spawnSync(process.execPath, [hookPath], {
    input,
    encoding: 'utf8',
    env: { ...process.env, ...env },
  });
  return result;
}

function createTranscript(assistantText, role = 'assistant') {
  const transcriptPath = path.join(tempDir, `transcript-${Date.now()}-${Math.random().toString(36).slice(2)}.jsonl`);
  const line = JSON.stringify({
    type: role,
    message: {
      role: role,
      content: [
        {
          type: 'text',
          text: assistantText,
        },
      ],
    },
  });
  fs.writeFileSync(transcriptPath, line + '\n', 'utf8');
  return transcriptPath;
}

// #1: インラインコードスパンの中にだけマークアップがある
run('Case #1: inline code span containing markup yields exit 0', () => {
  const text = 'Here is an inline snippet: `<invoke name="read_file"><parameter name="path">foo.txt</parameter></invoke>` as example.';
  const transcriptPath = createTranscript(text);
  const result = runHook({ transcript_path: transcriptPath });
  assert.strictEqual(result.status, 0);
  assert.strictEqual(result.stderr, '');
});

// #2: フェンス済みコードブロックの中にだけマークアップがある
run('Case #2: fenced code block containing markup yields exit 0', () => {
  const text = [
    'Here is an example code block:',
    '```xml',
    '<invoke name="write_file">',
    '  <parameter name="TargetFile">/tmp/test.txt</parameter>',
    '</invoke>',
    '```',
    'This block is excluded.',
  ].join('\n');
  const transcriptPath = createTranscript(text);
  const result = runHook({ transcript_path: transcriptPath });
  assert.strictEqual(result.status, 0);
  assert.strictEqual(result.stderr, '');
});

// #3: 引用ブロックの中にだけマークアップがある
run('Case #3: blockquote containing markup yields exit 0', () => {
  const text = [
    'Quoting previous turn:',
    '> <invoke name="bash">',
    '>   <parameter name="command">echo test</parameter>',
    '> </invoke>',
  ].join('\n');
  const transcriptPath = createTranscript(text);
  const result = runHook({ transcript_path: transcriptPath });
  assert.strictEqual(result.status, 0);
  assert.strictEqual(result.stderr, '');
});

// #4: 地の文に裸でマークアップがある
run('Case #4: bare markup in plain text yields exit 2', () => {
  const text = [
    'Now running tool:',
    '<invoke name="bash">',
    '  <parameter name="command">echo test</parameter>',
    '</invoke>',
  ].join('\n');
  const transcriptPath = createTranscript(text);
  const result = runHook({ transcript_path: transcriptPath });
  assert.strictEqual(result.status, 2);
  assert.match(result.stderr, /LEAKED TOOL CALL DETECTED/);
});

// #5: 縮退トークンの直後行にマークアップ（いずれもコード・引用の外）
run('Case #5: degraded token followed by markup in plain text yields exit 2', () => {
  const text = [
    'court',
    '<invoke name="bash">',
  ].join('\n');
  const transcriptPath = createTranscript(text);
  const result = runHook({ transcript_path: transcriptPath });
  assert.strictEqual(result.status, 2);
  assert.match(result.stderr, /LEAKED TOOL CALL DETECTED/);
});

// #6: 縮退トークンとマークアップがフェンスの中にある
run('Case #6: degraded token and markup inside fence yields exit 0', () => {
  const text = [
    '```',
    'court',
    '<invoke name="bash">',
    '```',
  ].join('\n');
  const transcriptPath = createTranscript(text);
  const result = runHook({ transcript_path: transcriptPath });
  assert.strictEqual(result.status, 0);
  assert.strictEqual(result.stderr, '');
});

// #7: マークアップが1つも無い普通の日本語の文章
run('Case #7: normal Japanese text with no markup yields exit 0', () => {
  const text = '修正が完了しました。テストを実行して動作を確認します。';
  const transcriptPath = createTranscript(text);
  const result = runHook({ transcript_path: transcriptPath });
  assert.strictEqual(result.status, 0);
  assert.strictEqual(result.stderr, '');
});

// #8: 同一ターン内で、コード内に引用がありつつ地の文にも裸のマークアップがある
run('Case #8: code with markup plus bare markup in plain text yields exit 2', () => {
  const text = [
    'Here is code:',
    '`<invoke name="example">`',
    'And here is a bare leak:',
    '<invoke name="actual_leak">',
  ].join('\n');
  const transcriptPath = createTranscript(text);
  const result = runHook({ transcript_path: transcriptPath });
  assert.strictEqual(result.status, 2);
  assert.match(result.stderr, /LEAKED TOOL CALL DETECTED/);
});

// #9: transcript_path が無い / JSON が壊れている / ファイルが読めない
run('Case #9: missing transcript_path / corrupt JSON / unreadable file yields exit 0', () => {
  // Empty input
  let result = runHook('');
  assert.strictEqual(result.status, 0);

  // Corrupt JSON
  result = runHook('{ invalid json');
  assert.strictEqual(result.status, 0);

  // Missing transcript_path
  result = runHook({});
  assert.strictEqual(result.status, 0);

  // Nonexistent transcript_path
  result = runHook({ transcript_path: path.join(tempDir, 'does-not-exist.jsonl') });
  assert.strictEqual(result.status, 0);
});

// #10: stop_hook_active が真で、地の文に裸のマークアップがある
run('Case #10: stop_hook_active true with bare markup yields exit 0', () => {
  const text = [
    'Bare leak but hook is already active:',
    '<invoke name="bash">',
  ].join('\n');
  const transcriptPath = createTranscript(text);
  const result = runHook({
    transcript_path: transcriptPath,
    stop_hook_active: true,
  });
  assert.strictEqual(result.status, 0);
  assert.strictEqual(result.stderr, '');
});

// #11: 地の文の漏洩の前後に、空行をまたいでバッククォートが1つずつある
run('Case #11: bare leak flanked by backticks across blank lines yields exit 2', () => {
  const text = [
    'コマンドは ` を使う。',
    '',
    '実行します:',
    '<invoke name="bash">',
    '',
    '以上 ` 完了。',
  ].join('\n');
  const transcriptPath = createTranscript(text);
  const result = runHook({ transcript_path: transcriptPath });
  assert.strictEqual(result.status, 2);
  assert.match(result.stderr, /LEAKED TOOL CALL DETECTED/);

  // Without backticks should behave identically (exit 2)
  const textNoBackticks = [
    'コマンドは  を使う。',
    '',
    '実行します:',
    '<invoke name="bash">',
    '',
    '以上  完了。',
  ].join('\n');
  const resultNoBackticks = runHook({ transcript_path: createTranscript(textNoBackticks) });
  assert.strictEqual(resultNoBackticks.status, 2);
  assert.match(resultNoBackticks.stderr, /LEAKED TOOL CALL DETECTED/);
});

// #12: 閉じられていないフェンスが先にあり、その後の地の文に漏洩がある
run('Case #12: unclosed fence preceding bare leak in plain text yields exit 2', () => {
  const text = [
    '```',
    'Some text inside unclosed fence',
    '<invoke name="bash">',
  ].join('\n');
  const transcriptPath = createTranscript(text);
  const result = runHook({ transcript_path: transcriptPath });
  assert.strictEqual(result.status, 2);
  assert.match(result.stderr, /LEAKED TOOL CALL DETECTED/);

  // Unclosed fence with language specifier followed by leak in subsequent plain text
  const textWithLang = [
    '```js',
    'const x = 1;',
    'Now in plain text:',
    '<invoke name="bash">',
  ].join('\n');
  const resultWithLang = runHook({ transcript_path: createTranscript(textWithLang) });
  assert.strictEqual(resultWithLang.status, 2);
  assert.match(resultWithLang.stderr, /LEAKED TOOL CALL DETECTED/);
});

// #13: 除外処理の内部で例外が起きた場合
run('Case #13: exception during markdown exclusion yields exit 0 (fail-open)', () => {
  const text = [
    'Bare markup that would trigger leak detection under normal circumstances:',
    '<invoke name="bash">',
  ].join('\n');
  const transcriptPath = createTranscript(text);
  const result = runHook(
    { transcript_path: transcriptPath },
    { __TEST_FORCE_STRIP_ERROR: '1' }
  );
  assert.strictEqual(result.status, 0);
  assert.strictEqual(result.stderr, '');
});

// Regression: 実物記憶ファイル leaked-toolcall-hook-linux.md の本文
run('Regression: memory file leaked-toolcall-hook-linux.md content yields exit 0', () => {
  assert(fs.existsSync(memoryPath), `Memory file should exist at ${memoryPath}`);
  const memoryContent = fs.readFileSync(memoryPath, 'utf8');
  const transcriptPath = createTranscript(memoryContent);
  const result = runHook({ transcript_path: transcriptPath });
  assert.strictEqual(result.status, 0);
  assert.strictEqual(result.stderr, '');
});
