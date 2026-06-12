#!/usr/bin/env bash
# setup-project-memory.sh
# One-shot, idempotent helper for SOLUTION A: move project memory from the
# OS-dependent harness store (~/.claude/projects/<slug>/memory) INTO the pCloud
# project folder (<project>/.claude-memory), and protect it from that project's
# own git repo by adding /.claude-memory/ to its .gitignore.
#
# Why a hand-maintained slug->path map: Claude Code's slug generation collapses
# both "_" and "-" to "-" (lossy, NOT reversible). The real folder is e.g.
# "Body_Segmentation" (underscore) but its slug is "...-Body-Segmentation". So we
# map slugs to real paths explicitly rather than string-substituting the slug.
#
# Safe to re-run: cp -n never overwrites; the .gitignore line is added once.

set -u
CLAUDE_DIR="$HOME/.claude"

# slug (under ~/.claude/projects) -> real pCloud project root (absolute path).
# Edit this map when you add projects. Keys MUST match the on-disk slug dir.
declare -A MAP=(
  ["-home-kita-pCloudDrive-Code-Research-RA"]="$HOME/pCloudDrive/Code/Research/RA"
  ["-home-kita-pCloudDrive-Code-Research-Body-Segmentation"]="$HOME/pCloudDrive/Code/Research/Body_Segmentation"
  ["-home-kita-pCloudDrive-Code-Research-Body-Segmentation-demo"]="$HOME/pCloudDrive/Code/Research/Body_Segmentation/demo"
  ["-home-kita-pCloudDrive-Code-Research-Osteoporosis"]="$HOME/pCloudDrive/Code/Research/Osteoporosis"
)

# Walk up from a path to find the enclosing git repo root (or empty).
git_root_of() {
    git -C "$1" rev-parse --show-toplevel 2>/dev/null
}

# Add /.claude-memory/ to the git repo's .gitignore (once), so project memory is
# never committed to that (often private) repo. Anchored to the repo root.
protect_in_repo() {
    local repo="$1"
    [ -n "$repo" ] || return 0
    local gi="$repo/.gitignore"
    if [ -f "$gi" ] && grep -qE '^/?\.claude-memory/?$' "$gi" 2>/dev/null; then
        echo "    .gitignore already protects .claude-memory (repo: $repo)"
        return 0
    fi
    {
        echo ""
        echo "# Claude Code project memory (synced via pCloud, NOT via this repo)"
        echo "/.claude-memory/"
    } >> "$gi"
    echo "    added /.claude-memory/ to $gi"
}

echo "== SOLUTION A migration: project memory -> pCloud folders =="
migrated=0
for slug in "${!MAP[@]}"; do
    src="$CLAUDE_DIR/projects/$slug/memory"
    proj="${MAP[$slug]}"
    dst="$proj/.claude-memory"

    [ -d "$proj" ] || { echo "  SKIP $slug : project folder missing ($proj)"; continue; }

    echo "  $slug"
    echo "    project: $proj"

    # Protect the project's own git repo first (if it is one).
    repo="$(git_root_of "$proj")"
    if [ -n "$repo" ]; then
        protect_in_repo "$repo"
    else
        echo "    (not a git repo - no .gitignore protection needed)"
    fi

    # Copy memory files (idempotent; never overwrite existing).
    if [ -d "$src" ]; then
        mkdir -p "$dst"
        copied=0
        for f in "$src"/*.md; do
            [ -e "$f" ] || continue
            if [ ! -e "$dst/$(basename "$f")" ]; then
                cp "$f" "$dst/" && copied=$((copied+1))
            fi
        done
        echo "    copied $copied new file(s) -> $dst"
        [ "$copied" -gt 0 ] && migrated=$((migrated+1))
    else
        echo "    (no existing harness memory to migrate)"
        # Still ensure the folder + a stub index exist so the project is ready.
        mkdir -p "$dst"
        [ -f "$dst/MEMORY.md" ] || printf '%s\n' "<!-- Project memory index. One line per fact: [Title](file.md) - hook -->" > "$dst/MEMORY.md"
    fi
done

echo "== done: $migrated project(s) received new memory files =="
echo "Note: old harness stores under ~/.claude/projects/-home-*-pCloudDrive-*/memory"
echo "      are left in place (git-ignored, harmless). New memory now lives in pCloud."
