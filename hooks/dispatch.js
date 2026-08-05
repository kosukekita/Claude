const fs = require('fs');
const path = require('path');
const { spawnSync } = require('child_process');

function main() {
  const target = process.argv[2];
  if (!target) {
    process.exit(0);
  }

  const extraArgs = process.argv.slice(3);
  const hooksDir = __dirname;
  const isWin = process.platform === 'win32';

  let baseName = target;
  if (target.endsWith('.ps1') || target.endsWith('.sh') || target.endsWith('.py') || target.endsWith('.mjs') || target.endsWith('.js') || target.endsWith('.cjs')) {
    baseName = path.basename(target, path.extname(target));
  }

  const findFile = (ext) => {
    const filePath = path.join(hooksDir, baseName + ext);
    return fs.existsSync(filePath) ? filePath : null;
  };

  const commandExists = (cmd) => {
    try {
      const whereCmd = isWin ? 'where' : 'which';
      const res = spawnSync(whereCmd, [cmd], { stdio: 'ignore' });
      return res.status === 0;
    } catch (e) {
      return false;
    }
  };

  let runner = null;
  let runnerArgs = [];

  if (isWin) {
    // Windows priority: .mjs/.cjs/.js -> .ps1 -> .py -> .sh (if bash exists)
    const jsFile = findFile('.mjs') || findFile('.cjs') || findFile('.js');
    const psFile = findFile('.ps1');
    const pyFile = findFile('.py');
    const shFile = findFile('.sh');

    if (jsFile) {
      runner = 'node';
      runnerArgs = [jsFile, ...extraArgs];
    } else if (psFile) {
      runner = 'powershell';
      runnerArgs = ['-NoProfile', '-ExecutionPolicy', 'Bypass', '-File', psFile, ...extraArgs];
    } else if (pyFile) {
      runner = commandExists('python') ? 'python' : (commandExists('python3') ? 'python3' : 'py');
      runnerArgs = [pyFile, ...extraArgs];
    } else if (shFile && commandExists('bash')) {
      runner = 'bash';
      runnerArgs = [shFile, ...extraArgs];
    }
  } else {
    // Non-Windows (Linux/macOS) priority: .mjs/.cjs/.js -> .sh -> .py -> .ps1 (if pwsh/powershell exists)
    const jsFile = findFile('.mjs') || findFile('.cjs') || findFile('.js');
    const shFile = findFile('.sh');
    const pyFile = findFile('.py');
    const psFile = findFile('.ps1');

    if (jsFile) {
      runner = 'node';
      runnerArgs = [jsFile, ...extraArgs];
    } else if (shFile) {
      runner = 'bash';
      runnerArgs = [shFile, ...extraArgs];
    } else if (pyFile) {
      runner = commandExists('python3') ? 'python3' : 'python';
      runnerArgs = [pyFile, ...extraArgs];
    } else if (psFile && (commandExists('pwsh') || commandExists('powershell'))) {
      runner = commandExists('pwsh') ? 'pwsh' : 'powershell';
      runnerArgs = ['-NoProfile', '-ExecutionPolicy', 'Bypass', '-File', psFile, ...extraArgs];
    }
  }

  if (!runner) {
    process.exit(0);
  }

  const res = spawnSync(runner, runnerArgs, {
    stdio: [0, 'pipe', 'pipe'],
    maxBuffer: 1024 * 1024 * 64,
    windowsHide: true
  });

  if (res.error) {
    process.exit(0);
  }

  if (res.stdout && res.stdout.length > 0) {
    process.stdout.write(res.stdout);
  }

  if (res.stderr && res.stderr.length > 0) {
    process.stderr.write(res.stderr);
  }

  process.exit(res.status !== null ? res.status : 0);
}

main();
