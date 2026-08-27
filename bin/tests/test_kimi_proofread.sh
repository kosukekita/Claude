#!/usr/bin/env bash
set -u

SCRIPT_DIR=$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)
CLI=$(CDPATH= cd -- "$SCRIPT_DIR/.." && pwd)/kimi-proofread.sh
NODE=/usr/bin/node
KEY_FILE=${HOME}/.config/litellm/litellm.env

passed=0
failed=0
tmp_dir=$(mktemp -d)
trap 'rm -rf -- "$tmp_dir"' EXIT

pass() {
  passed=$((passed + 1))
  printf 'PASS #%s: %s\n' "$1" "$2"
}

fail() {
  failed=$((failed + 1))
  printf 'FAIL #%s: %s\n' "$1" "$2" >&2
}

run_expect_failure() {
  local stdout_file=$1
  local stderr_file=$2
  shift 2
  if "$@" >"$stdout_file" 2>"$stderr_file"; then
    return 1
  fi
}

if [[ ! -x "$CLI" ]]; then
  printf 'FAIL: executable not found: %s\n' "$CLI" >&2
  exit 1
fi

if [[ ! -x "$NODE" ]]; then
  printf 'FAIL: required runtime not found: %s\n' "$NODE" >&2
  exit 1
fi

fixture=$tmp_dir/input.md
printf '%s\n' '重要なのは、多角的かつ包括的に検討することだと言えるだろう。' >"$fixture"
printf '%s\n' '概念図に未発表の結果を示し、解析不能なら帰国後の課題とする。' >>"$fixture"

dry_default=$tmp_dir/dry-default.json
if "$CLI" --dry-run "$fixture" >"$dry_default" 2>"$tmp_dir/dry-default.err" &&
  "$NODE" - "$dry_default" <<'NODE'
const fs = require('fs');
const request = JSON.parse(fs.readFileSync(process.argv[2], 'utf8'));
if (request.model !== 'free-kimi-k3') process.exit(1);
if (!Number.isInteger(request.max_tokens) || request.max_tokens < 4000) process.exit(1);
NODE
then
  pass 1 'dry-run uses the default model and a safe max_tokens value'
else
  fail 1 'dry-run JSON is invalid or has unsafe defaults'
fi

dry_grant=$tmp_dir/dry-grant.json
if "$CLI" --dry-run --grant "$fixture" >"$dry_grant" 2>"$tmp_dir/dry-grant.err" &&
  "$NODE" - "$dry_grant" <<'NODE'
const fs = require('fs');
const request = JSON.parse(fs.readFileSync(process.argv[2], 'utf8'));
const system = request.messages?.find(message => message.role === 'system')?.content ?? '';
if (!system.includes('概念図')) process.exit(1);
if (!system.includes('未発表')) process.exit(1);
if (!system.includes('帰国後')) process.exit(1);
NODE
then
  pass 2 'grant mode includes the required forbidden-expression guidance'
else
  fail 2 'grant guidance is incomplete'
fi

if "$NODE" - "$dry_default" <<'NODE'
const fs = require('fs');
const request = JSON.parse(fs.readFileSync(process.argv[2], 'utf8'));
const system = request.messages?.find(message => message.role === 'system')?.content ?? '';
const boilerplate = ['重要なのは', '多角的', '包括的', 'と言えるだろう'];
if (!boilerplate.every(term => system.includes(term))) process.exit(1);
const grantOnly = ['概念図', '未発表', '帰国後の課題とする'];
if (grantOnly.some(term => system.includes(term))) process.exit(1);
NODE
then
  pass 3 'default mode includes boilerplate removal but excludes grant-only guidance'
else
  fail 3 'default proofreading guidance has the wrong scope'
fi

if run_expect_failure "$tmp_dir/missing.out" "$tmp_dir/missing.err" \
  "$CLI" "$tmp_dir/does-not-exist.md" && [[ -s "$tmp_dir/missing.err" ]]; then
  pass 4 'a missing input file fails with a stderr message'
else
  fail 4 'a missing input file was not rejected clearly'
fi

empty_file=$tmp_dir/empty.txt
: >"$empty_file"
if run_expect_failure "$tmp_dir/empty.out" "$tmp_dir/empty.err" "$CLI" "$empty_file"; then
  pass 5 'an empty input file is rejected'
else
  fail 5 'an empty input file was accepted'
fi

if run_expect_failure "$tmp_dir/tokens.out" "$tmp_dir/tokens.err" \
  "$CLI" --dry-run --max-tokens 100 "$fixture"; then
  pass 6 'max_tokens below 4000 is rejected'
else
  fail 6 'an unsafe max_tokens value was accepted'
fi

if [[ -r "$KEY_FILE" ]] && "$NODE" - "$KEY_FILE" "$dry_default" <<'NODE'
const fs = require('fs');
const envText = fs.readFileSync(process.argv[2], 'utf8');
const dryRun = fs.readFileSync(process.argv[3], 'utf8');
let key = '';
for (const rawLine of envText.split(/\r?\n/)) {
  const line = rawLine.trim();
  if (!line || line.startsWith('#')) continue;
  const match = line.match(/^(?:export\s+)?LITELLM_MASTER_KEY\s*=\s*(.*)$/);
  if (!match) continue;
  key = match[1].trim();
  if ((key.startsWith('"') && key.endsWith('"')) ||
      (key.startsWith("'") && key.endsWith("'"))) {
    key = key.slice(1, -1);
  }
  break;
}
if (!key) process.exit(2);
if (dryRun.includes(key)) process.exit(1);
NODE
then
  pass 7 'dry-run output does not expose the configured key value'
else
  fail 7 'key file is unavailable, unparsable, or its value leaked into dry-run output'
fi

live_output=$tmp_dir/live-output.txt
if "$CLI" --grant "$fixture" >"$live_output" 2>"$tmp_dir/live.err" && [[ -s "$live_output" ]]; then
  pass 8 'live grant-mode request succeeds and returns non-empty content'
else
  fail 8 'live request failed or returned empty content'
  if [[ -s "$tmp_dir/live.err" ]]; then
    sed -n '1,5p' "$tmp_dir/live.err" >&2
  fi
fi

if ((failed == 0 && passed == 8)); then
  pass 9 'standalone acceptance suite completed with all checks passing'
else
  fail 9 "standalone acceptance suite had ${failed} failure(s) before its final check"
fi

printf '%s passed, %s failed\n' "$passed" "$failed"
((failed == 0))
