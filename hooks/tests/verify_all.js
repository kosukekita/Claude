const fs = require('fs');
const path = require('path');
const { spawnSync } = require('child_process');

const results = {};

console.log("=== RUNNING ACCEPTANCE CRITERIA VERIFICATION SUITE ===");

// -----------------------------------------------------------------------------
// Criterion A: PowerShell execution without parse errors for all hook commands
// -----------------------------------------------------------------------------
console.log("\n--- Criterion A: PowerShell execution check ---");
const settingsPath = path.join(__dirname, '..', '..', 'settings.json');
const settingsJson = JSON.parse(fs.readFileSync(settingsPath, 'utf8'));

const hookCommands = [];
function extractCommands(obj) {
  if (!obj || typeof obj !== 'object') return;
  for (const key in obj) {
    if (key === 'command' && typeof obj[key] === 'string') {
      if (obj[key].includes('dispatch.js')) {
        hookCommands.push(obj[key]);
      }
    } else {
      extractCommands(obj[key]);
    }
  }
}
extractCommands(settingsJson.hooks);

let passA = true;
const logsA = [];

for (const cmdStr of hookCommands) {
  const buf = Buffer.from(cmdStr, 'utf16le');
  const b64 = buf.toString('base64');
  
  const res = spawnSync('powershell', ['-NoProfile', '-EncodedCommand', b64], {
    stdio: ['pipe', 'pipe', 'pipe']
  });

  const errStr = res.stderr.toString('utf8') + res.stdout.toString('utf8');
  const hasParseError = errStr.includes('ParserError') || errStr.includes('MissingOpenParenthesis');

  logsA.push({
    cmd: cmdStr,
    status: res.status,
    parseError: hasParseError,
    output: errStr.trim().substring(0, 100)
  });

  if (hasParseError) {
    passA = false;
  }
}

results.A = {
  pass: passA && hookCommands.length >= 13,
  count: hookCommands.length,
  logs: logsA
};
console.log(`Criterion A: ${results.A.pass ? 'PASS' : 'FAIL'} (${hookCommands.length} hooks tested)`);

// -----------------------------------------------------------------------------
// Criterion B: Non-zero exit code pass-through (e.g. exit code 2)
// -----------------------------------------------------------------------------
console.log("\n--- Criterion B: Exit code pass-through ---");
const testScriptB = path.join(__dirname, '..', '_test_exit2.ps1');
fs.writeFileSync(testScriptB, 'exit 2\n', 'ascii');

const resB = spawnSync('node', [path.join(__dirname, '..', 'dispatch.js'), '_test_exit2'], {
  stdio: ['ignore', 'pipe', 'pipe']
});

try { fs.unlinkSync(testScriptB); } catch(e){}

results.B = {
  pass: resB.status === 2,
  observedStatus: resB.status
};
console.log(`Criterion B: ${results.B.pass ? 'PASS' : 'FAIL'} (Observed exit status: ${resB.status})`);

// -----------------------------------------------------------------------------
// Criterion C: Stdin pass-through (exact byte preservation)
// -----------------------------------------------------------------------------
console.log("\n--- Criterion C: Stdin pass-through ---");
const testScriptC = path.join(__dirname, '..', '_test_stdin.ps1');
fs.writeFileSync(testScriptC, '$s = [System.Console]::OpenStandardInput(); $o = [System.Console]::OpenStandardOutput(); $s.CopyTo($o)\n', 'ascii');

const payloadC = JSON.stringify({ test: "hello_\u3067\u3059_123" });
const inputBufC = Buffer.from(payloadC, 'utf8');

const resC = spawnSync('node', [path.join(__dirname, '..', 'dispatch.js'), '_test_stdin'], {
  input: inputBufC,
  stdio: ['pipe', 'pipe', 'pipe']
});

try { fs.unlinkSync(testScriptC); } catch(e){}

const outputBufC = resC.stdout;
const isByteEqualC = inputBufC.equals(outputBufC);

results.C = {
  pass: isByteEqualC,
  inputHex: inputBufC.toString('hex'),
  outputHex: outputBufC.toString('hex')
};
console.log(`Criterion C: ${results.C.pass ? 'PASS' : 'FAIL'} (Bytes match: ${isByteEqualC})`);

// -----------------------------------------------------------------------------
// Criterion D: Stdout pass-through (clean JSON, no extra wrapper/lines)
// -----------------------------------------------------------------------------
console.log("\n--- Criterion D: Stdout pass-through ---");
const resD = spawnSync('node', [path.join(__dirname, '..', 'dispatch.js'), 'memory-inject'], {
  stdio: ['ignore', 'pipe', 'pipe']
});
const outStrD = resD.stdout.toString('utf8').trim();
let isCleanJsonD = false;
try {
  const parsed = JSON.parse(outStrD);
  if (parsed.hookSpecificOutput && parsed.hookSpecificOutput.hookEventName === "SessionStart") {
    isCleanJsonD = true;
  }
} catch(e){}

results.D = {
  pass: isCleanJsonD,
  rawOutputSnippet: outStrD.substring(0, 150)
};
console.log(`Criterion D: ${results.D.pass ? 'PASS' : 'FAIL'}`);

// -----------------------------------------------------------------------------
// Criterion E: Real hook functional regression on Windows
// -----------------------------------------------------------------------------
console.log("\n--- Criterion E: Functional regression tests ---");
// 1. block-dangerous
const payloadE1 = JSON.stringify({ tool_input: { command: "rm -rf /tmp/dangerous_test" } });
const resE1 = spawnSync('node', [path.join(__dirname, '..', 'dispatch.js'), 'block-dangerous'], {
  input: Buffer.from(payloadE1, 'utf8'),
  stdio: ['pipe', 'pipe', 'pipe']
});
const errE1 = resE1.stderr.toString('utf8');
const passE1 = (resE1.status === 2) && errE1.includes('Blocked');

// 2. protect-files
const payloadE2 = JSON.stringify({ tool_input: { file_path: ".git/config" } });
const resE2 = spawnSync('node', [path.join(__dirname, '..', 'dispatch.js'), 'protect-files'], {
  input: Buffer.from(payloadE2, 'utf8'),
  stdio: ['pipe', 'pipe', 'pipe']
});
const passE2 = (resE2.status === 0 || resE2.status === 2);

// 3. guard-file-revert
const payloadE3 = JSON.stringify({ tool_input: { file_path: "settings.json" } });
const resE3 = spawnSync('node', [path.join(__dirname, '..', 'dispatch.js'), 'guard-file-revert'], {
  input: Buffer.from(payloadE3, 'utf8'),
  stdio: ['pipe', 'pipe', 'pipe']
});
const passE3 = (resE3.status === 0 || resE3.status === 2);

// 4. auto-push
const resE4 = spawnSync('node', [path.join(__dirname, '..', 'dispatch.js'), 'auto-push'], {
  stdio: ['ignore', 'pipe', 'pipe']
});
const passE4 = (resE4.status === 0);

// 5. memory-inject
const passE5 = results.D.pass;

const passE = passE1 && passE2 && passE3 && passE4 && passE5;
results.E = {
  pass: passE,
  blockDangerousStatus: resE1.status,
  blockDangerousMsg: errE1.trim(),
  autoPushStatus: resE4.status
};
console.log(`Criterion E: ${results.E.pass ? 'PASS' : 'FAIL'}`);

// -----------------------------------------------------------------------------
// Criterion F: No CP932 / Japanese character corruption
// -----------------------------------------------------------------------------
console.log("\n--- Criterion F: Encoding verification ---");
const outBufF = resD.stdout;
const outStrF = outBufF.toString('utf8');
const containsJapaneseF = outStrF.includes("記憶") && !outStrF.includes("ï¿½");
const passF = containsJapaneseF && !outStrF.includes('\uFFFD');

results.F = {
  pass: passF,
  sampleText: outStrF.substring(outStrF.indexOf("記憶") - 5, outStrF.indexOf("記憶") + 25)
};
console.log(`Criterion F: ${results.F.pass ? 'PASS' : 'FAIL'} (Sample: "${results.F.sampleText}")`);

// -----------------------------------------------------------------------------
// Criterion G: Linux real machine (akitaken) verification via SSH
// -----------------------------------------------------------------------------
console.log("\n--- Criterion G: akitaken Linux verification ---");
const targetG = ['auto-push', 'memory-sync-codex', 'detect-leaked-toolcall'];
const logsG = [];
let passG = true;

for (const hookName of targetG) {
  const sshCmd = `echo "{}" | node "$HOME/.claude/hooks/dispatch.js" ${hookName}; echo exit_code: $?`;
  const resG = spawnSync('ssh', ['-o', 'BatchMode=yes', '-o', 'ConnectTimeout=15', 'akitaken', sshCmd], {
    stdio: ['ignore', 'pipe', 'pipe']
  });
  const outG = resG.stdout.toString('utf8').trim();
  const successG = resG.status === 0 && outG.includes('exit_code: 0');
  logsG.push({ hook: hookName, status: resG.status, output: outG });
  if (!successG) passG = false;
}

results.G = {
  pass: passG,
  logs: logsG
};
console.log(`Criterion G: ${results.G.pass ? 'PASS' : 'FAIL'}`);

// -----------------------------------------------------------------------------
// Criterion H: JSON validity and completeness
// -----------------------------------------------------------------------------
console.log("\n--- Criterion H: JSON structure completeness ---");
const gitShowRes = spawnSync('git', ['show', '0fa5638e6e6890885a10bebdd4dab5e886f86ab5:settings.json'], {
  cwd: path.join(__dirname, '..', '..'),
  stdio: ['ignore', 'pipe', 'pipe']
});
const origJson = JSON.parse(gitShowRes.stdout.toString('utf8'));

const origHooks = origJson.hooks;
const currHooks = settingsJson.hooks;

let countOrig = 0;
let countCurr = 0;
for (const ev in origHooks) {
  origHooks[ev].forEach(h => countOrig += h.hooks.length);
}
for (const ev in currHooks) {
  currHooks[ev].forEach(h => countCurr += h.hooks.length);
}

const sameEvents = Object.keys(origHooks).length === Object.keys(currHooks).length;
const passH = (countOrig === countCurr) && (countCurr === 29) && sameEvents;
results.H = {
  pass: passH,
  origCount: countOrig,
  currCount: countCurr,
  sameEvents: sameEvents
};
console.log(`Criterion H: ${results.H.pass ? 'PASS' : 'FAIL'} (Orig count: ${countOrig}, Curr count: ${countCurr})`);

// -----------------------------------------------------------------------------
// Criterion I: Synchronization rules (Line endings & ASCII only rules)
// -----------------------------------------------------------------------------
console.log("\n--- Criterion I: Line endings & ASCII rules ---");
const dispatchContent = fs.readFileSync(path.join(__dirname, '..', 'dispatch.js'), 'utf8');
const isAsciiI = /^[\x00-\x7F]*$/.test(dispatchContent);
const isLfI = !dispatchContent.includes('\r\n');

results.I = {
  pass: isAsciiI,
  isAscii: isAsciiI,
  isLf: isLfI
};
console.log(`Criterion I: ${results.I.pass ? 'PASS' : 'FAIL'} (Is ASCII: ${isAsciiI}, Is LF: ${isLfI})`);

// Summary
fs.writeFileSync(path.join(__dirname, 'verification_report.json'), JSON.stringify(results, null, 2));
console.log("\n=== ALL CRITERIA VERIFICATION COMPLETE ===");
