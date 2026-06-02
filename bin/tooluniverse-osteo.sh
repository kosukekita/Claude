#!/usr/bin/env bash
# Cross-PC launcher for the tooluniverse-osteo MCP server.
#
# The MCP `command` field can't branch on OS, and the venv layout differs
# between machines (Unix: .venv/bin, Windows: .venv/Scripts; home paths differ).
# This wrapper resolves the right tooluniverse-smcp-stdio binary at runtime so
# the same .mcp.json works on every PC that shares this repo.
#
# Override the env root by exporting TOOLUNIVERSE_HOME if your venv lives
# somewhere other than "$HOME/tooluniverse-env".
set -euo pipefail

ENV_ROOT="${TOOLUNIVERSE_HOME:-$HOME/tooluniverse-env}"

# Candidate binary locations, in priority order: Unix venv, Windows venv,
# then anything already on PATH.
candidates=(
  "$ENV_ROOT/.venv/bin/tooluniverse-smcp-stdio"
  "$ENV_ROOT/.venv/Scripts/tooluniverse-smcp-stdio.exe"
)

BIN=""
for c in "${candidates[@]}"; do
  if [ -x "$c" ]; then
    BIN="$c"
    break
  fi
done

if [ -z "$BIN" ]; then
  if command -v tooluniverse-smcp-stdio >/dev/null 2>&1; then
    BIN="$(command -v tooluniverse-smcp-stdio)"
  fi
fi

if [ -z "$BIN" ]; then
  echo "tooluniverse-osteo: could not find tooluniverse-smcp-stdio." >&2
  echo "  Looked under: $ENV_ROOT/.venv/{bin,Scripts} and PATH." >&2
  echo "  Set TOOLUNIVERSE_HOME or install tooluniverse on this machine." >&2
  exit 127
fi

exec "$BIN" \
  --include-tools \
    PubMed_search_articles \
    semantic_scholar_search \
    EuropePMC_search_articles \
    search_clinical_trials \
    Tool_Finder_Keyword \
  "$@"
