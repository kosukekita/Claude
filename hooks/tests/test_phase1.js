const assert = require('assert');
const fs = require('fs');
const os = require('os');
const path = require('path');

const hooksDir = path.join(__dirname, '..');
const repoDir = path.join(hooksDir, '..');
const dispatchPath = path.join(hooksDir, 'dispatch.js');
const settingsPath = path.join(repoDir, 'settings.json');
const manifestPath = path.join(hooksDir, 'manifest.json');
const dispatcher = require(dispatchPath);
const registeredTargets = dispatcher.registeredTargets;

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

run('manifest and settings targets match exactly', () => {
  const settings = JSON.parse(fs.readFileSync(settingsPath, 'utf8'));
  const manifest = JSON.parse(fs.readFileSync(manifestPath, 'utf8'));
  const actual = [...registeredTargets(settings)].sort();
  const declared = Object.keys(manifest.targets).sort();
  assert.deepStrictEqual(declared, actual);
  for (const [target, metadata] of Object.entries(manifest.targets)) {
    assert(['any', 'windows', 'linux'].includes(metadata.platform), target);
    assert(['required', 'advisory'].includes(metadata.criticality), target);
    assert(
      metadata.implementation_status === undefined ||
        ['active', 'pending'].includes(metadata.implementation_status),
      target
    );
    assert.strictEqual(typeof metadata.description, 'string', target);
    assert(metadata.description.trim().length > 0, target);
  }
  for (const target of ['warn-bash-overwrite', 'memory-inject']) {
    assert.strictEqual(manifest.targets[target].platform, 'any', target);
    assert.strictEqual(manifest.targets[target].implementation_status, 'pending', target);
    assert(!/on Windows|Windows memory/i.test(manifest.targets[target].description), target);
  }
  assert(!actual.includes('protect-files'));
  assert(!Object.hasOwn(manifest.targets, 'protect-files'));
  assert(!fs.existsSync(path.join(hooksDir, 'protect-files.ps1')));
  assert(fs.existsSync(path.join(hooksDir, 'retired', 'protect-files.ps1')));
  for (const target of ['warn-tu-encoding', 'pixel-agents-shim']) {
    assert.strictEqual(manifest.targets[target].platform, 'windows', target);
    assert.notStrictEqual(manifest.targets[target].implementation_status, 'pending', target);
  }
});

run('missing applicable hook warns, records JSONL, and does not block', () => {
  const temp = fs.mkdtempSync(path.join(os.tmpdir(), 'hooks-phase1-'));
  const fixtureManifest = path.join(temp, 'manifest.json');
  fs.writeFileSync(fixtureManifest, JSON.stringify({
    version: 1,
    targets: {
      'definitely-missing-hook': {
        platform: 'any',
        criticality: 'required',
        description: 'fixture'
      }
    }
  }));
  const result = dispatcher.dispatchTarget('definitely-missing-hook', [], {
    env: { ...process.env, CLAUDE_HOOK_MANIFEST: fixtureManifest, XDG_STATE_HOME: temp }
  });
  assert.strictEqual(result.status, 0);
  assert.match(result.stderr, /HOOK DISPATCH WARNING/);
  assert.match(result.stderr, /definitely-missing-hook/);
  const events = fs.readFileSync(path.join(temp, 'claude-hooks', 'dispatch-events.jsonl'), 'utf8').trim();
  const event = JSON.parse(events);
  assert.strictEqual(event.target, 'definitely-missing-hook');
  assert.strictEqual(event.kind, 'unresolved');
});

run('platform mismatch is a silent successful skip', () => {
  if (process.platform === 'win32') return;
  const temp = fs.mkdtempSync(path.join(os.tmpdir(), 'hooks-phase1-'));
  const fixtureManifest = path.join(temp, 'manifest.json');
  fs.writeFileSync(fixtureManifest, JSON.stringify({
    version: 1,
    targets: {
      'windows-only-missing-hook': {
        platform: 'windows',
        criticality: 'advisory',
        description: 'fixture'
      }
    }
  }));
  const result = dispatcher.dispatchTarget('windows-only-missing-hook', [], {
    env: { ...process.env, CLAUDE_HOOK_MANIFEST: fixtureManifest, XDG_STATE_HOME: temp }
  });
  assert.strictEqual(result.status, 0);
  assert.strictEqual(result.stderr, '');
  assert(!fs.existsSync(path.join(temp, 'claude-hooks', 'dispatch-events.jsonl')));
});

run('retired protect-files is unregistered, undeclared, and archived', () => {
  const settings = JSON.parse(fs.readFileSync(settingsPath, 'utf8'));
  const manifest = JSON.parse(fs.readFileSync(manifestPath, 'utf8'));
  const inspected = dispatcher.inspectTarget('protect-files');
  assert(!registeredTargets(settings).has('protect-files'));
  assert(!Object.hasOwn(manifest.targets, 'protect-files'));
  assert(!fs.existsSync(path.join(hooksDir, 'protect-files.ps1')));
  assert(fs.existsSync(path.join(hooksDir, 'retired', 'protect-files.ps1')));
  assert.match(inspected.error, /not declared in manifest/);
});

run('spawn errors are visible and remain fail-open', () => {
  const temp = fs.mkdtempSync(path.join(os.tmpdir(), 'hooks-phase1-'));
  const result = dispatcher.dispatchTarget('guard-destructive-and-resolution', [], {
    env: { ...process.env, XDG_STATE_HOME: temp },
    spawnSync: () => ({ error: new Error('fixture spawn failure') })
  });
  assert.strictEqual(result.status, 0);
  assert.match(result.stderr, /HOOK DISPATCH WARNING/);
  assert.match(result.stderr, /spawn failure/);
  const events = fs.readFileSync(path.join(temp, 'claude-hooks', 'dispatch-events.jsonl'), 'utf8').trim();
  assert.strictEqual(JSON.parse(events).kind, 'spawn-error');
});

run('resolved hook exit status and output are propagated unchanged', () => {
  const result = dispatcher.dispatchTarget('guard-destructive-and-resolution', [], {
    spawnSync: (command) => {
      if (command === 'which' || command === 'where') return { status: 0 };
      return {
        status: 2,
        stdout: Buffer.from('fixture-stdout'),
        stderr: Buffer.from('fixture-stderr')
      };
    }
  });
  assert.strictEqual(result.status, 2);
  assert.strictEqual(result.stdout.toString('utf8'), 'fixture-stdout');
  assert.strictEqual(result.stderr.toString('utf8'), 'fixture-stderr');
});

run('log-commands is unregistered and archived', () => {
  const settings = JSON.parse(fs.readFileSync(settingsPath, 'utf8'));
  assert(!registeredTargets(settings).has('log-commands'));
  assert(!fs.existsSync(path.join(hooksDir, 'log-commands.ps1')));
  assert(fs.existsSync(path.join(hooksDir, 'retired', 'log-commands.ps1')));
});

run('third-party hook paths are not detected as self-registered targets', () => {
  const fixtureSettings = {
    hooks: {
      PreToolUse: [
        {
          hooks: [
            { command: 'node "C:\\Users\\u8792\\.pixel-agents\\hooks\\claude-hook.js"' },
            {
              command:
                'if [ -f "${HOME-}/.orca/agent-hooks/claude-hook.sh" ] && [ -r "${HOME-}/.orca/agent-hooks/claude-hook.sh" ]; then "${HOME-}/.orca/agent-hooks/claude-hook.sh"; fi'
            },
            { command: 'node "$HOME/.claude/hooks/pixel-agents-shim.js"' },
            { command: 'node "$HOME/.claude/hooks/dispatch.js" warn-tu-encoding' }
          ]
        }
      ]
    }
  };
  const actual = registeredTargets(fixtureSettings);
  assert(!actual.has('claude-hook'));
  assert(actual.has('pixel-agents-shim'));
  assert(actual.has('warn-tu-encoding'));
  assert.strictEqual(actual.size, 2);
});

run('verification suite has no ambiguous 0-or-2 assertions', () => {
  const source = fs.readFileSync(path.join(__dirname, 'verify_all.js'), 'utf8');
  assert(!/status\s*===\s*0\s*\|\|\s*[^\n]*status\s*===\s*2/.test(source));
});
