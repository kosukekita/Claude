#!/usr/bin/env bash
set -u

tests_dir="$(cd "$(dirname "$0")" && pwd)"

node "$tests_dir/test_phase1.js" || exit 1
node "$tests_dir/test_detect_leaked_toolcall.js" || exit 1
bash "$tests_dir/test_health_check.sh" || exit 1
bash "$tests_dir/test_phase2.sh" || exit 1
python3 "$tests_dir/test_guard_policy.py" || exit 1
python3 "$tests_dir/test_hook_observability.py" || exit 1
python3 "$tests_dir/test_guard_override.py" || exit 1
bash "$tests_dir/test_guard.sh" || exit 1
python3 "$tests_dir/test_phase3.py" || exit 1
bash "$tests_dir/verify_all.sh" || exit 1

printf 'ALL HOOK TESTS PASS\n'
