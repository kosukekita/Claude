"use strict";
// Cross-OS bootstrap for the tooluniverse-osteo MCP server.
//
// Why this exists: `.mcp.json` cannot branch on OS, and a bare
// `"command": "bash"` resolves to the System32 WSL stub on Windows
// (which has no /bin/bash), breaking the server. Node is guaranteed to
// be present for Claude Code and is launched as a real .exe (no PATHEXT
// or WSL ambiguity), so we use it to launch the CORRECT bash by absolute
// path: Git Bash on Windows, /bin/bash on Linux/macOS. Locating the venv
// binary stays in tooluniverse-osteo.sh.
//
// Override the bash path by exporting TU_OSTEO_BASH if your bash lives
// elsewhere. Forward slashes are used in all Windows paths because Node's
// fs/child_process accept them and they avoid JS backslash-escape pitfalls.
const { spawnSync } = require("node:child_process");
const fs = require("node:fs");
const path = require("node:path");

const launcher = path.join(__dirname, "tooluniverse-osteo.sh");

function findBash() {
  if (process.env.TU_OSTEO_BASH) return process.env.TU_OSTEO_BASH;
  if (process.platform === "win32") {
    const candidates = [
      "C:/Program Files/Git/bin/bash.exe",
      "C:/Program Files/Git/usr/bin/bash.exe",
      "C:/Program Files (x86)/Git/bin/bash.exe",
    ];
    if (process.env.ProgramW6432) {
      candidates.push(
        path.join(process.env.ProgramW6432, "Git", "bin", "bash.exe")
      );
    }
    if (process.env.LOCALAPPDATA) {
      candidates.push(
        path.join(
          process.env.LOCALAPPDATA,
          "Programs",
          "Git",
          "bin",
          "bash.exe"
        )
      );
    }
    for (const c of candidates) {
      if (fs.existsSync(c)) return c;
    }
    // Last resort: rely on PATH (may hit the WSL stub; documented failure mode).
    return "bash";
  }
  return "/bin/bash";
}

const bash = findBash();

// Forward any extra args supplied in .mcp.json after the launcher path.
const extraArgs = process.argv.slice(2);

const result = spawnSync(bash, [launcher, ...extraArgs], {
  stdio: "inherit",
  windowsHide: true,
});

if (result.error) {
  console.error(
    "tooluniverse-osteo: failed to launch bash (" +
      bash +
      "): " +
      result.error.message
  );
  process.exit(127);
}

process.exit(result.status === null ? 1 : result.status);
