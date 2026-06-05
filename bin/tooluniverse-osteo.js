"use strict";
// Cross-OS launcher for the tooluniverse-osteo MCP server.
//
// Why this exists: `.mcp.json` cannot branch on OS, and the venv layout
// differs per machine (Unix: .venv/bin, Windows: .venv/Scripts; home paths
// differ). A bare `"command": "bash"` also resolves to the System32 WSL stub
// on Windows (which has no /bin/bash), so we avoid bash entirely. Node is
// guaranteed present for Claude Code and launches as a real .exe, so this
// launcher resolves the per-OS `tooluniverse-smcp-stdio` binary at runtime
// and spawns it directly with raw stdio (the MCP JSON-RPC channel).
//
// Override the env root by exporting TOOLUNIVERSE_HOME if your venv lives
// somewhere other than "$HOME/tooluniverse-env". Forward slashes are fine on
// Windows (Node accepts them) and avoid JS backslash-escape pitfalls.
//
// If the venv is not installed on this machine, exit cleanly with a clear
// message. The server should additionally be left out of this PC's
// enabledMcpjsonServers (settings.local.json) so /doctor does not flag it.
const { spawn } = require("node:child_process");
const fs = require("node:fs");
const path = require("node:path");
const os = require("node:os");

const envRoot =
  process.env.TOOLUNIVERSE_HOME || path.join(os.homedir(), "tooluniverse-env");

// Candidate binary locations, in priority order: Windows venv, Unix venv.
const candidates = [
  path.join(envRoot, ".venv", "Scripts", "tooluniverse-smcp-stdio.exe"),
  path.join(envRoot, ".venv", "bin", "tooluniverse-smcp-stdio"),
];

const bin = candidates.find((c) => fs.existsSync(c)) || null;

if (!bin) {
  console.error(
    "tooluniverse-osteo: could not find tooluniverse-smcp-stdio.\n" +
      "  Looked under: " +
      path.join(envRoot, ".venv", "{Scripts,bin}") +
      "\n" +
      "  Set TOOLUNIVERSE_HOME or install tooluniverse on this machine,\n" +
      "  and add 'tooluniverse-osteo' to this PC's enabledMcpjsonServers."
  );
  process.exit(127);
}

// The tools this server exposes. semantic_scholar_search was dropped (not in
// the installed build); 4 tools load cleanly.
const includeTools = [
  "PubMed_search_articles",
  "EuropePMC_search_articles",
  "search_clinical_trials",
  "Tool_Finder_Keyword",
];

const extraArgs = process.argv.slice(2);

const child = spawn(bin, ["--include-tools", ...includeTools, ...extraArgs], {
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
  if (signal) process.exit(1);
  process.exit(code === null ? 1 : code);
});
