---
name: pcloud-project-memory-solution-a
description: Project memory lives in <pCloud-project>/.claude-memory/ (not ~/.claude store) so it cross-PC syncs despite OS slug differences
metadata: 
  node_type: memory
  type: project
  originSessionId: 5abc3f9a-6807-4887-a828-d7f17f8a2012
---

Cross-PC project-memory carry-over (Solution A, implemented 2026-06-12). Harness auto-memory is keyed by an OS-dependent cwd slug (Linux `/home/kita/pCloudDrive/Code/Research/RA` -> `-home-kita-pCloudDrive-Code-Research-RA`; Windows `P:\...\RA` -> `p--...-RA`), so the SAME project's memory was never cross-read between PCs. Fix: store project memory INSIDE the pCloud project folder at `<project>/.claude-memory/`, which pCloud syncs as real files identical on every machine.

**Moving parts (all in ~/.claude, committed):**
- `hooks/memory-inject-project.sh` — SessionStart hook. Reads the stdin JSON `cwd` (fallback: jq -> python3 -> `$CLAUDE_PROJECT_DIR`), then injects `<cwd>/.claude-memory/MEMORY.md` + linked bodies (YAML frontmatter stripped) as `additionalContext` JSON `{"hookSpecificOutput":{"hookEventName":"SessionStart","additionalContext":...}}`. A HOOK, not a CLAUDE.md rule, because injection must be mechanical — global `~/.claude/CLAUDE.md` is NOT loaded when cwd is a project (only that project's own CLAUDE.md is). Registered in settings.json SessionStart, bash-guarded, alongside the global memory-inject.
- `bin/setup-project-memory.sh` — idempotent migration. Copies harness project memory into `<project>/.claude-memory/` via an EXPLICIT slug->realpath map (slug is lossy: both `_` and `-` collapse to `-`, e.g. real `Body_Segmentation` vs slug `...-Body-Segmentation`, so you cannot reverse the slug). Also appends `/.claude-memory/` to the project's OWN `.gitignore` if it is a git repo — RA (`RA_Research`) and Osteoporosis are private repos that track CLAUDE.md, so `.claude-memory/` would otherwise be committed there.
- `CLAUDE.md` rule: cwd-deterministic routing — cwd under `~/.claude` -> global store; cwd under pCloud project -> `./.claude-memory/`.

**Bug found & fixed (4034d17):** the inject loop checked `char_limit` BEFORE appending the snippet, so a first memory file larger than the cap (RA's 6.7KB deploy-log memory > old 6000) broke the loop with empty output — the hook injected nothing. Fix: append first, then check cap (>=1 body always lands); raised cap to 12000. NOTE: global `hooks/memory-inject.ps1` has the SAME pre-append-check structure — latent there too, just not yet triggered because global memories are small. Watch for it if a global memory ever exceeds ~6KB.

**Verification done:** all 10 migrated files present; `.claude-memory/` is git-ignored in RA/Osteoporosis/demo repos (no leak, `git status` clean); hook E2E injects RA 8KB/2 memories, Body_Segmentation 5KB/4. Old harness stores under `~/.claude/projects/-home-*-pCloudDrive-*/memory` left in place (git-ignored, harmless). See [[mcp-cross-pc-and-claude-json-race]] and [[alphaxiv-mcp-streamable-http]] for the broader cross-PC ~/.claude setup; cross-OS auto-sync hooks (auto-pull.sh/auto-push.sh, .gitignore -*--claude rule) landed same day.
