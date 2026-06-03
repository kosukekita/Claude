"use strict";
// Self-contained, cross-OS launcher for the tooluniverse-osteo MCP server.
//
// Why this exists: `.mcp.json` cannot branch on OS, and a bare
// `"command": "bash"` resolves to the System32 WSL stub on Windows (which has
// no /bin/bash), killing the server. Node is guaranteed present for Claude
// Code and launches as a real .exe (no PATHEXT / WSL ambiguity), so we use it
// to resolve the per-OS venv binary ourselves and spawn it DIRECTLY. There is
// no bash and no .sh in the chain anymore -- the one OS branch `.mcp.json`
// cannot express lives here, in this committed launcher.
//
// The venv lives under $TOOLUNIVERSE_HOME (default: ~/tooluniverse-env). Its
// layout differs by OS: .venv/Scripts/*.exe on Windows, .venv/bin/* on POSIX.
// Override the root with TOOLUNIVERSE_HOME if your env lives elsewhere.
// Forward slashes are used in Windows paths because Node's fs/child_process
// accept them and they avoid JS backslash-escape pitfalls.
const { spawn } = require("node:child_process");
const fs = require("node:fs");
const path = require("node:path");
const os = require("node:os");

// Tools to expose. semantic_scholar_search is intentionally omitted: it is not
// in the installed build (v2.14.5) and including it aborts tool loading.
const INCLUDE_TOOLS = [
  "PubMed_search_articles",
  "EuropePMC_search_articles",
  "search_clinical_trials",
  "Tool_Finder_Keyword",
];

function homeDir() {
  return (
    process.env.HOME ||
    process.env.USERPROFILE ||
    (process.env.HOMEDRIVE && process.env.HOMEPATH
      ? process.env.HOMEDRIVE + process.env.HOMEPATH
      : "")
  );
}

function findBinary() {
  const envRoot =
    process.env.TOOLUNIVERSE_HOME || path.join(homeDir(), "tooluniverse-env");
  // Priority: Windows venv, POSIX venv. fs.existsSync picks the one that's real
  // on this machine, so the same committed config works on every PC.
  const candidates = [
    path.join(envRoot, ".venv", "Scripts", "tooluniverse-smcp-stdio.exe"),
    path.join(envRoot, ".venv", "bin", "tooluniverse-smcp-stdio"),
  ];
  for (const c of candidates) {
    if (fs.existsSync(c)) return c;
  }
  return null;
}

const bin = findBinary();

if (!bin) {
  const root =
    process.env.TOOLUNIVERSE_HOME || path.join(homeDir(), "tooluniverse-env");
  console.error(
    "tooluniverse-osteo: could not find tooluniverse-smcp-stdio.\n" +
      "  Looked under: " +
      path.join(root, ".venv", "{Scripts,bin}") +
      "\n  Set TOOLUNIVERSE_HOME or install tooluniverse on this machine."
  );
  process.exit(127);
}

// Forward any extra args supplied in .mcp.json after the launcher path.
const extraArgs = process.argv.slice(2);

const child = spawn(bin, ["--include-tools", ...INCLUDE_TOOLS, ...extraArgs], {
  stdio: "inherit",
  windowsHide: true,
});

child.on("error", (err) => {
  console.error(
    "tooluniverse-osteo: failed to launch (" + bin + "): " + err.message
  );
  process.exit(127);
});

child.on("exit", (code, signal) => {
  if (signal) {
    process.kill(process.pid, signal);
    return;
  }
  process.exit(code === null ? 1 : code);
});
