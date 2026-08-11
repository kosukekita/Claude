const fs = require('fs');
const os = require('os');
const path = require('path');

const hooksDir = path.join(__dirname, '..');
const repoDir = path.join(hooksDir, '..');
const settingsPath = path.join(repoDir, 'settings.json');
const manifestPath = path.join(hooksDir, 'manifest.json');
const dispatch = require(path.join(hooksDir, 'dispatch.js'));

function registeredTargets(settings) {
  const targets = new Set();
  for (const groups of Object.values(settings.hooks || {})) {
    for (const group of groups) {
      for (const hook of group.hooks || []) {
        const command = hook.command || '';
        const throughDispatch = command.match(/dispatch\.js\"?\s+([A-Za-z0-9._-]+)/);
        if (throughDispatch) {
          targets.add(dispatch.baseNameFor(throughDispatch[1]));
          continue;
        }
        const direct = command.match(/hooks\/([A-Za-z0-9._-]+)\.(?:mjs|cjs|js|sh|py|ps1)/);
        if (direct) targets.add(direct[1]);
      }
    }
  }
  return targets;
}

function sameMembers(left, right) {
  return left.size === right.size && [...left].every((item) => right.has(item));
}

const settings = JSON.parse(fs.readFileSync(settingsPath, 'utf8'));
const manifest = JSON.parse(fs.readFileSync(manifestPath, 'utf8'));
const registered = registeredTargets(settings);
const declared = new Set(Object.keys(manifest.targets || {}));
const tempHome = fs.mkdtempSync(path.join(os.tmpdir(), 'hooks-verify-'));
fs.mkdirSync(path.join(tempHome, '.claude'), { recursive: true });
const testEnv = {
  ...process.env,
  HOME: tempHome,
  CLAUDE_HOME: path.join(tempHome, '.claude'),
  CODEX_HOME: path.join(tempHome, '.codex'),
  XDG_STATE_HOME: path.join(tempHome, '.state'),
  CLAUDE_HOOK_MANIFEST: manifestPath
};

let failed = 0;
let passed = 0;
let skipped = 0;
let pending = 0;
const targetResults = [];

console.log('=== Hook registration and functional verification ===');
if (sameMembers(registered, declared)) {
  console.log(`PASS manifest coverage (${registered.size} unique targets)`);
  passed += 1;
} else {
  const missing = [...registered].filter((target) => !declared.has(target));
  const extra = [...declared].filter((target) => !registered.has(target));
  console.log(`FAIL manifest coverage missing=[${missing}] extra=[${extra}]`);
  failed += 1;
}

for (const target of [...registered].sort()) {
  const inspected = dispatch.inspectTarget(target, { env: testEnv });
  if (!inspected.applicable) {
    const result = { target, result: 'SKIP', platform: inspected.metadata.platform };
    targetResults.push(result);
    skipped += 1;
    console.log(`SKIP ${target} (platform=${inspected.metadata.platform})`);
    continue;
  }
  if (inspected.metadata.implementation_status === 'pending') {
    if (!inspected.error) {
      const result = { target, result: 'FAIL', reason: 'pending declaration has a runnable implementation' };
      targetResults.push(result);
      failed += 1;
      console.log(`FAIL ${target}: ${result.reason}`);
      continue;
    }
    targetResults.push({ target, result: 'PENDING', reason: inspected.error });
    pending += 1;
    console.log(`PENDING ${target}: ${inspected.error}`);
    continue;
  }
  if (inspected.error) {
    const result = { target, result: 'FAIL', reason: inspected.error };
    targetResults.push(result);
    failed += 1;
    console.log(`FAIL ${target}: ${inspected.error}`);
    continue;
  }
  targetResults.push({ target, result: 'PASS' });
  passed += 1;
  console.log(`PASS ${target} (runnable implementation resolved)`);
}

const invalidSkips = targetResults.filter(
  (entry) => entry.result === 'SKIP' && entry.platform !== 'windows'
);
if (invalidSkips.length > 0) {
  failed += invalidSkips.length;
  console.log(`FAIL non-Windows skips: ${invalidSkips.map((entry) => entry.target).join(', ')}`);
}

console.log(`SUMMARY PASS=${passed} PENDING=${pending} SKIP=${skipped} FAIL=${failed}`);
process.exitCode = failed === 0 ? 0 : 1;
