#!/usr/bin/env bash
# grok_delegate.sh — SIGNPOST, not an implementation.
#
# This is the *terminal fallback* for the generate-edit-video skill's Grok path.
# It DOES NOT reimplement Grok. It (1) checks the Grok CLI is present + authed,
# (2) prints the grok-media delegation contract, and (3) echoes any --task/--prompt
# /--image/--out args back as a *suggested* grok-media invocation.
#
# >>> The agent MUST perform the actual generation by following the grok-media
# >>> SKILL (/home/kita/.claude/skills/grok-media/SKILL.md). Do NOT hardcode or
# >>> guess Grok CLI flags here beyond what grok-media documents.
#
# Usage: grok_delegate.sh [--task t2v|i2v|ref2v|t2i|edit] [--prompt P]
#                         [--image PATH] [--out PATH]
set -euo pipefail

# Scrub anaconda libtinfo LD pollution before spawning `grok` (consistency with
# the rest of the skill; harmless if env.sh is absent).
# shellcheck source=/dev/null
[ -f "$(dirname "$0")/env.sh" ] && . "$(dirname "$0")/env.sh" >/dev/null 2>&1 || true

# --- locate the Grok CLI (grok-media documents grok.exe on Windows; on this
# --- Linux box it is plain `grok`). Resolve without guessing flags. ---------
GROK=""
for cand in "${GROK_BIN:-}" "$HOME/.grok/bin/grok" "$HOME/.grok/bin/grok.exe" grok; do
  [ -n "$cand" ] || continue
  if command -v "$cand" >/dev/null 2>&1; then GROK="$cand"; break; fi
done

# --- args (echoed back only; never executed as Grok flags) ------------------
# Note: we deliberately avoid `shift 2`, which fails under `set -e` when a
# value-taking flag is the trailing arg with no value. Shift the flag, then
# shift the value only if one is present.
TASK="" ; PROMPT="" ; IMAGE="" ; OUT=""
while [ "$#" -gt 0 ]; do
  case "$1" in
    --task)   TASK="${2:-}"  ; shift; [ "$#" -gt 0 ] && shift ;;
    --prompt) PROMPT="${2:-}"; shift; [ "$#" -gt 0 ] && shift ;;
    --image)  IMAGE="${2:-}" ; shift; [ "$#" -gt 0 ] && shift ;;
    --out)    OUT="${2:-}"   ; shift; [ "$#" -gt 0 ] && shift ;;
    -h|--help) TASK="${TASK:-help}"; shift ;;
    *) printf 'warn: ignoring unknown arg: %s\n' "$1" >&2; shift ;;
  esac
done

bar() { printf '%s\n' "============================================================"; }

# --- (1) presence + auth gate ----------------------------------------------
bar
echo "grok_delegate.sh — Grok terminal fallback (SIGNPOST ONLY)"
bar
if [ -z "$GROK" ]; then
  cat <<'EOF'
Grok CLI: NOT FOUND.
  The xAI Grok Build CLI is not on PATH (looked for: $GROK_BIN, ~/.grok/bin/grok,
  ~/.grok/bin/grok.exe, grok).
  Install per the grok-media skill, then log in (OAuth — must be done in YOUR OWN
  terminal; `!`-prefixed / non-interactive runs do NOT complete the OAuth flow):
      grok login --device-auth
  Open the printed URL in an X Premium+ / SuperGrok logged-in browser, approve the code.
EOF
else
  echo "Grok CLI: found -> $GROK"
  echo "Auth check (grok models):"
  if "$GROK" models >/dev/null 2>&1; then
    echo "  OK — appears authenticated."
  else
    cat <<EOF
  NOT authenticated (or 'grok models' failed).
  Log in from YOUR OWN terminal (OAuth will not complete via '!'/non-interactive):
      $GROK login --device-auth
  Then open the URL in an X Premium+ / SuperGrok logged-in browser and approve.
EOF
  fi
fi

# --- (2) the delegation contract -------------------------------------------
bar
cat <<'EOF'
DELEGATION CONTRACT (follow the grok-media SKILL for the real work):
  skill: /home/kita/.claude/skills/grok-media/SKILL.md

  - Grok Build is an AGENT. There are NO dedicated subcommands; its media tools
    fire from NATURAL-LANGUAGE instructions. Tool names:
        image_gen           text -> image
        image_edit          edit an image
        image_to_video      input image -> video
        reference_to_video  reference image -> video
  - TEXT-TO-VIDEO is a 2-STAGE flow: image_gen  ->  image_to_video.
    (There is NO text-to-video tool.)
  - Run in a CLEAN, EMPTY working dir:   WORK="$(mktemp -d)"; cd "$WORK"
    (running under an existing project dir makes Grok explore and fail with
     Auth(AuthorizationRequired) before generating). Copy any input image INTO
     $WORK and reference it as ./input.jpg.
  - Output recovery (response text may be EMPTY even on success):
        ask Grok directly (same session):   grok -r -p 'absolute path of the media you just generated?'
        or scan the session dir:
            ~/.grok/sessions/<enc-cwd>/<session-id>/images/N.jpg
            ~/.grok/sessions/<enc-cwd>/<session-id>/videos/N.mp4
  - Video is async (~1 min): run in background, deliver via SendUserFile when done.

  >>> THIS SCRIPT IS THE TERMINAL FALLBACK. RUN VIA THE grok-media SKILL.
  >>> DO NOT HARDCODE GROK CLI FLAGS HERE.
EOF

# --- (3) echo args back as a *suggested* grok-media invocation --------------
if [ -n "$TASK$PROMPT$IMAGE$OUT" ]; then
  bar
  echo "SUGGESTED grok-media invocation (from your args — NOT executed here):"
  case "$TASK" in
    t2v)
      echo "  task=text-to-video -> 2 stages (image_gen, then image_to_video):"
      echo "    stage1: Use your image_gen tool to create an image: ${PROMPT:-<PROMPT>}."
      echo "    stage2: Use your image_to_video tool to animate ./input.jpg: ${PROMPT:-<MOTION>}."
      ;;
    i2v)
      echo "    Use your image_to_video tool to animate ./input.jpg: ${PROMPT:-<MOTION>}."
      ;;
    ref2v)
      echo "    Use your reference_to_video tool with ./ref.jpg: ${PROMPT:-<PROMPT>}."
      ;;
    edit)
      echo "    Use your image_edit tool on ./input.jpg: ${PROMPT:-<EDIT>}."
      ;;
    t2i|"")
      echo "    Use your image_gen tool to create an image: ${PROMPT:-<PROMPT>}."
      ;;
    *)
      echo "    (unknown --task '$TASK'; treat as image_gen) Use your image_gen tool: ${PROMPT:-<PROMPT>}."
      ;;
  esac
  [ -n "$IMAGE" ] && echo "  input image: copy '$IMAGE' into the mktemp WORK dir, reference as ./input.jpg"
  [ -n "$OUT" ]   && echo "  desired out: '$OUT' — copy the recovered session file there after Step 3"
  echo
  echo "  ^ This is the terminal fallback; run via the grok-media skill, do not"
  echo "    hardcode Grok CLI flags here."
fi
bar
