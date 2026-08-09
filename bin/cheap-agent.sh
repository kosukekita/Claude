#!/usr/bin/env bash
set -eo pipefail

if [ $# -eq 0 ]; then
  echo "Error: Task string required." >&2
  exit 1
fi

TASK="$1"

# Check gateway
if ! curl -s "http://127.0.0.1:4000/health" > /dev/null; then
  echo "Error: LiteLLM gateway is down." >&2
  exit 1
fi

export ANTHROPIC_BASE_URL="http://127.0.0.1:4000"
TOKEN="$(grep '^LITELLM_MASTER_KEY=' "$HOME/.config/litellm/litellm.env" | cut -d= -f2-)"
if [ -z "$TOKEN" ]; then
  echo "Error: LITELLM_MASTER_KEY not found." >&2
  exit 1
fi
export ANTHROPIC_AUTH_TOKEN="$TOKEN"

MODEL="${CHEAP_AGENT_MODEL:-claude-atlas-deepseek-v4}"
export ANTHROPIC_MODEL="$MODEL"

# Check model validity
MODELS_JSON=$(curl -s -H "Authorization: Bearer $ANTHROPIC_AUTH_TOKEN" "http://127.0.0.1:4000/v1/models")
if [[ "$MODELS_JSON" != *\"$MODEL\"* ]]; then
  echo "Error: Invalid model name: $MODEL" >&2
  exit 1
fi

export CLAUDE_CODE_DISABLE_EXPERIMENTAL_BETAS=1
export CLAUDE_CODE_AUTO_COMPACT_WINDOW=128000
export CLAUDE_CODE_MAX_OUTPUT_TOKENS=16384

SETTINGS='{"permissions":{"allow":["Read","WebFetch","Bash(cat*)","Bash(ls*)","Bash(grep*)","Bash(find*)","Bash(head*)","Bash(tail*)","Bash(wc*)"],"defaultMode":"reject"},"remoteControlAtStartup":false,"disableRemoteControl":true,"fallbackModel":["'$MODEL'"]}'

set +e
OUTPUT=$(timeout 600 claude -p "$TASK" --model "$MODEL" --settings "$SETTINGS" 2>/dev/null)
RET=$?
set -e

if [ $RET -eq 124 ]; then
  echo "Error: Execution timed out." >&2
  exit $RET
elif [ $RET -ne 0 ]; then
  echo "Error: Agent failed or returned non-zero exit code." >&2
  exit $RET
fi

echo "$OUTPUT"
