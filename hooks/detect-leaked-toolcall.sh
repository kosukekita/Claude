#!/usr/bin/env bash
# detect-leaked-toolcall.sh
# Stop hook: detect raw tool-call markup that LEAKED into the assistant's
# finished message as plain text instead of being executed as a real tool call.
#
# Background (verified against live transcripts, 2026-06-15):
#   A harness-level serialization defect occasionally drops the tool-call open
#   marker's namespace prefix, degrading it to a bare token ("court"/"count"/
#   "call") followed by literal <invoke name=...> markup. The harness then fails
#   to parse it as a tool call and renders it as visible text, so the operation
#   (Bash/Edit/Write/Grep/Workflow) NEVER RUNS and fails silently.
#
# This hook cannot prevent or repair the leak (it happens inside the model-output
# boundary that no hook can observe). It can only DETECT the leak in the just-
# finished assistant turn and, via exit code 2, tell the harness to re-issue the
# dropped tool call.
#
# NOTE on exit code 2 (Stop hook):
#   Claude Codeのhooksドキュメントによると、Stopフックでexit 2を返すと
#   ハーネスはモデルに処理の続行を促す（「ツールが未完了なので再試行せよ」
#   というシグナル）。exit 0は正常終了、exit 2は「まだ続行が必要」を意味する。
#   ただしこれはモデルに再送を「促す」だけで保証ではない。
#   同じコンテキストで再試行しても同じ状態に陥る可能性があるため、
#   advisory messageに /clear を推奨する文言を含めている。
#
# Exit codes:
#   0 = no leak detected (silent, normal)
#   2 = leak detected -> stderr advisory shown to the model so it retries

set -euo pipefail

# stdin からペイロードを読む（Stop フックはJSONをstdinに渡す）
raw=$(cat)

if [[ -z "$raw" ]]; then
    exit 0
fi

# transcript_path を抽出
# jqが使えるならjqを、なければpython3を使う
if command -v jq >/dev/null 2>&1; then
    transcript_path=$(printf '%s' "$raw" | jq -r '.transcript_path // empty' 2>/dev/null)
else
    transcript_path=$(printf '%s' "$raw" | python3 -c "
import sys, json
data = json.load(sys.stdin)
tp = data.get('transcript_path', '')
if tp:
    print(tp)
" 2>/dev/null || true)
fi

if [[ -z "$transcript_path" ]] || [[ ! -f "$transcript_path" ]]; then
    exit 0
fi

# トランスクリプト(JSONL)を読んで最後のassistantターンのテキストを抽出
# jqまたはpython3でパース
if command -v jq >/dev/null 2>&1; then
    assistant_text=$(jq -rs '
        # 全行を配列に展開（JSONL: 各行が独立したJSONオブジェクト）
        [.[] | select(
            # type == "assistant" もしくは message.role == "assistant" の行
            (.type == "assistant") or (.message.role == "assistant")
        )]
        | last
        | if . == null then ""
          else
            # content配列のtypeがtextのブロックのテキストを連結
            ([
                (if .message.content then .message.content
                 elif .content then .content
                 else []
                 end)[]
                | select(.type == "text")
                | .text
            ] | join("\n"))
          end
    ' "$transcript_path" 2>/dev/null || true)
else
    assistant_text=$(python3 << PYEOF
import json, sys

transcript_path = """$transcript_path"""
try:
    lines = open(transcript_path, encoding='utf-8').readlines()
except Exception:
    sys.exit(0)

last_assistant = None
for line in lines:
    line = line.strip()
    if not line:
        continue
    try:
        obj = json.loads(line)
    except Exception:
        continue
    role = None
    if obj.get('type') == 'assistant':
        role = 'assistant'
    elif obj.get('message', {}).get('role') == 'assistant':
        role = 'assistant'
    if role != 'assistant':
        continue
    last_assistant = obj

if last_assistant is None:
    sys.exit(0)

content = last_assistant.get('message', {}).get('content') or last_assistant.get('content', [])
texts = []
for block in content:
    if isinstance(block, dict) and block.get('type') == 'text' and block.get('text'):
        texts.append(block['text'])
print('\n'.join(texts))
PYEOF
2>/dev/null || true)
fi

if [[ -z "$assistant_text" ]]; then
    exit 0
fi

# --- 検知 -------------------------------------------------------------------
# Signal A: ツールコールのマークアップがテキストとして存在する
has_markup=0
if printf '%s' "$assistant_text" | grep -qE '<invoke[[:space:]]+name=|</invoke>|<parameter[[:space:]]+name=|<function_calls>'; then
    has_markup=1
fi

# Signal B: 退化した開始トークン単独行 + 直後マークアップ行
# (court|count|call) だけの行の直後に <invoke|<parameter|<function_calls> が来るパターン
has_degrade=0
if printf '%s' "$assistant_text" | grep -qzP '(?m)^\s*(court|count|call)\s*\n\s*<(invoke|parameter|function_calls)' 2>/dev/null; then
    has_degrade=1
elif printf '%s' "$assistant_text" | python3 -c "
import sys, re
text = sys.stdin.read()
pattern = r'(?m)^\s*(court|count|call)\s*\n\s*<(invoke|parameter|function_calls)'
sys.exit(0 if re.search(pattern, text) else 1)
" 2>/dev/null; then
    has_degrade=1
fi

if [[ "$has_markup" -eq 1 ]] || [[ "$has_degrade" -eq 1 ]]; then
    echo 'LEAKED TOOL CALL DETECTED: the previous assistant turn emitted raw tool-call markup (e.g. <invoke name=...>) as plain TEXT instead of executing it, so that tool call DID NOT RUN. This is the known harness serialization-leak bug. Re-issue the dropped tool call now. If it leaks again on retry, the context is polluted: advise the user to run /clear (a same-context retry cannot reliably fix it).' >&2
    exit 2
fi

exit 0
