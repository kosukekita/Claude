const fs = require('fs');
const os = require('os');
const path = require('path');
const childProcess = require('child_process');

const EXTENSIONS = ['.ps1', '.sh', '.py', '.mjs', '.js', '.cjs'];

function platformName(nodePlatform = process.platform) {
  if (nodePlatform === 'win32') return 'windows';
  if (nodePlatform === 'linux') return 'linux';
  return nodePlatform;
}

function loadManifest(env = process.env) {
  const manifestPath = env.CLAUDE_HOOK_MANIFEST || path.join(__dirname, 'manifest.json');
  return JSON.parse(fs.readFileSync(manifestPath, 'utf8'));
}

function baseNameFor(target) {
  if (EXTENSIONS.some((extension) => target.endsWith(extension))) {
    return path.basename(target, path.extname(target));
  }
  return target;
}

function commandExists(command, spawn = childProcess.spawnSync, nodePlatform = process.platform) {
  try {
    const probe = nodePlatform === 'win32' ? 'where' : 'which';
    return spawn(probe, [command], { stdio: 'ignore' }).status === 0;
  } catch (_error) {
    return false;
  }
}

function findHookFile(baseName, extension, hooksDir = __dirname) {
  const filePath = path.join(hooksDir, baseName + extension);
  return fs.existsSync(filePath) ? filePath : null;
}

function resolveRunner(target, options = {}) {
  const hooksDir = options.hooksDir || __dirname;
  const spawn = options.spawnSync || childProcess.spawnSync;
  const nodePlatform = options.platform || process.platform;
  const isWindows = nodePlatform === 'win32';
  const baseName = baseNameFor(target);
  const find = (extension) => findHookFile(baseName, extension, hooksDir);
  const jsFile = find('.mjs') || find('.cjs') || find('.js');
  const psFile = find('.ps1');
  const pyFile = find('.py');
  const shFile = find('.sh');

  if (isWindows) {
    if (jsFile) return { runner: process.execPath, args: [jsFile] };
    if (psFile) {
      return {
        runner: 'powershell',
        args: ['-NoProfile', '-ExecutionPolicy', 'Bypass', '-File', psFile]
      };
    }
    if (pyFile) {
      const python = commandExists('python', spawn, nodePlatform)
        ? 'python'
        : (commandExists('python3', spawn, nodePlatform) ? 'python3' : 'py');
      return { runner: python, args: [pyFile] };
    }
    if (shFile && commandExists('bash', spawn, nodePlatform)) {
      return { runner: 'bash', args: [shFile] };
    }
    return null;
  }

  if (jsFile) return { runner: process.execPath, args: [jsFile] };
  if (shFile) return { runner: 'bash', args: [shFile] };
  if (pyFile) {
    const python = commandExists('python3', spawn, nodePlatform) ? 'python3' : 'python';
    return { runner: python, args: [pyFile] };
  }
  if (psFile && (commandExists('pwsh', spawn, nodePlatform) || commandExists('powershell', spawn, nodePlatform))) {
    const powershell = commandExists('pwsh', spawn, nodePlatform) ? 'pwsh' : 'powershell';
    return {
      runner: powershell,
      args: ['-NoProfile', '-ExecutionPolicy', 'Bypass', '-File', psFile]
    };
  }
  return null;
}

function stateRoot(env = process.env, nodePlatform = process.platform) {
  if (env.XDG_STATE_HOME) return env.XDG_STATE_HOME;
  if (nodePlatform === 'win32' && env.LOCALAPPDATA) return env.LOCALAPPDATA;
  return path.join(os.homedir(), '.local', 'state');
}

function warningEvent(target, metadata, kind, detail) {
  return {
    timestamp: new Date().toISOString(),
    target,
    platform: platformName(),
    criticality: metadata ? metadata.criticality : 'unknown',
    kind,
    detail
  };
}

function recordWarning(event, env = process.env) {
  try {
    const directory = path.join(stateRoot(env), 'claude-hooks');
    fs.mkdirSync(directory, { recursive: true });
    fs.appendFileSync(
      path.join(directory, 'dispatch-events.jsonl'),
      JSON.stringify(event) + '\n',
      'utf8'
    );
  } catch (_error) {
    // Reporting must remain fail-open even when the state directory is unavailable.
  }
}

function visibleFailure(target, metadata, kind, detail, env = process.env) {
  const event = warningEvent(target, metadata, kind, detail);
  recordWarning(event, env);
  return `[HOOK DISPATCH WARNING] ${target} (${event.criticality}): ${detail}\n`;
}

function platformMatches(declared, nodePlatform = process.platform) {
  return declared === 'any' || declared === platformName(nodePlatform);
}

function inspectTarget(target, options = {}) {
  const env = options.env || process.env;
  let manifest;
  try {
    manifest = loadManifest(env);
  } catch (error) {
    return { applicable: true, metadata: null, resolution: null, error: `manifest unreadable: ${error.message}` };
  }
  const metadata = manifest.targets && manifest.targets[baseNameFor(target)];
  if (!metadata) {
    return { applicable: true, metadata: null, resolution: null, error: 'target is not declared in manifest' };
  }
  if (!platformMatches(metadata.platform, options.platform || process.platform)) {
    return { applicable: false, metadata, resolution: null, error: null };
  }
  const resolution = resolveRunner(target, options);
  return {
    applicable: true,
    metadata,
    resolution,
    error: resolution ? null : 'no runnable implementation was found'
  };
}

function dispatchTarget(target, extraArgs = [], options = {}) {
  const env = options.env || process.env;
  const spawn = options.spawnSync || childProcess.spawnSync;
  const inspected = inspectTarget(target, options);
  if (!inspected.applicable) return { status: 0, stdout: '', stderr: '' };
  if (inspected.error) {
    const stderr = visibleFailure(target, inspected.metadata, 'unresolved', inspected.error, env);
    return { status: 0, stdout: '', stderr };
  }

  const result = spawn(
    inspected.resolution.runner,
    [...inspected.resolution.args, ...extraArgs],
    {
      stdio: options.input === undefined ? [0, 'pipe', 'pipe'] : ['pipe', 'pipe', 'pipe'],
      input: options.input,
      env,
      maxBuffer: 1024 * 1024 * 64,
      windowsHide: true
    }
  );
  if (result.error) {
    const detail = `spawn failure: ${result.error.message}`;
    const stderr = visibleFailure(target, inspected.metadata, 'spawn-error', detail, env);
    return { status: 0, stdout: '', stderr };
  }
  return {
    status: result.status !== null ? result.status : 0,
    stdout: result.stdout || Buffer.alloc(0),
    stderr: result.stderr || Buffer.alloc(0)
  };
}

function main() {
  const target = process.argv[2];
  if (!target) process.exit(0);
  const result = dispatchTarget(target, process.argv.slice(3));
  if (result.stdout && result.stdout.length > 0) process.stdout.write(result.stdout);
  if (result.stderr && result.stderr.length > 0) process.stderr.write(result.stderr);
  process.exit(result.status);
}

module.exports = {
  baseNameFor,
  dispatchTarget,
  inspectTarget,
  loadManifest,
  platformMatches,
  platformName,
  resolveRunner
};

if (require.main === module) main();
