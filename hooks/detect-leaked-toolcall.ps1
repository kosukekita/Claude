# detect-leaked-toolcall.ps1
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
# finished assistant turn and, via exit code 2, tell the model to re-issue the
# dropped tool call.
#
# IMPORTANT constraints (per project memory):
#   * Output ONLY ASCII via STDERR ([Console]::Error). Writing non-ASCII to
#     stdout on this cp932 console produces mojibake (feedback_powershell_hook_utf8_stdout).
#   * Never echo raw transcript bytes back (avoids re-polluting context with any
#     stray surrogate). We emit a fixed ASCII advisory only.
#
# Exit codes:
#   0 = no leak detected (silent, normal)
#   2 = leak detected -> stderr advisory shown to the model so it retries

$ErrorActionPreference = 'Stop'

try {
    # The Stop hook receives a JSON payload on stdin containing transcript_path.
    $raw = [Console]::In.ReadToEnd()
    if ([string]::IsNullOrWhiteSpace($raw)) { exit 0 }

    $payload = $raw | ConvertFrom-Json
    $tp = $payload.transcript_path
    if ([string]::IsNullOrWhiteSpace($tp)) { exit 0 }
    if (-not (Test-Path -LiteralPath $tp)) { exit 0 }

    # Read the transcript and isolate the LAST assistant record. The transcript
    # is JSONL: one JSON object per line. We scan from the end for the most
    # recent assistant turn and concatenate its text blocks.
    $lines = Get-Content -LiteralPath $tp -Encoding UTF8
    if (-not $lines -or $lines.Count -eq 0) { exit 0 }

    $assistantText = $null
    for ($i = $lines.Count - 1; $i -ge 0; $i--) {
        $line = $lines[$i]
        if ([string]::IsNullOrWhiteSpace($line)) { continue }
        $obj = $null
        try { $obj = $line | ConvertFrom-Json } catch { continue }

        # Match the assistant message envelope. Schema can be either
        # {type:"assistant", message:{content:[...]}} or a flat shape; handle both.
        $role = $null
        if ($obj.type) { $role = $obj.type }
        elseif ($obj.message -and $obj.message.role) { $role = $obj.message.role }

        if ($role -ne 'assistant') { continue }

        $content = $null
        if ($obj.message -and $obj.message.content) { $content = $obj.message.content }
        elseif ($obj.content) { $content = $obj.content }
        if (-not $content) { continue }

        $sb = New-Object System.Text.StringBuilder
        foreach ($block in $content) {
            # Only TEXT blocks can hold leaked markup. Real tool_use blocks are
            # fine (they executed). A leak lives in a "text" block.
            if ($block.type -eq 'text' -and $block.text) {
                [void]$sb.AppendLine([string]$block.text)
            }
        }
        $assistantText = $sb.ToString()
        break
    }

    if ([string]::IsNullOrWhiteSpace($assistantText)) { exit 0 }

    # --- Detection -----------------------------------------------------------
    # Two independent signals; either one is sufficient.
    #
    # Signal A: literal tool-call markup present as text. The angle brackets are
    # real characters in the leaked text (live-verified, grep-able).
    $markupRegex = '<invoke\s+name=|</invoke>|<parameter\s+name=|<function_calls>'
    $hasMarkup = $assistantText -match $markupRegex

    # Signal B: a degraded open-marker token alone on its own line, immediately
    # followed by a markup line. This is the exact observed shape.
    $degradeRegex = '(?m)^\s*(court|count|call)\s*\r?\n\s*<(invoke|parameter|function_calls)'
    $hasDegrade = $assistantText -match $degradeRegex

    if ($hasMarkup -or $hasDegrade) {
        $msg = @(
            'LEAKED TOOL CALL DETECTED: the previous assistant turn emitted raw',
            'tool-call markup (e.g. <invoke name=...>) as plain TEXT instead of',
            'executing it, so that tool call DID NOT RUN. This is the known',
            'harness serialization-leak bug. Re-issue the dropped tool call now.',
            'If it leaks again on retry, the context is polluted: advise the user',
            'to run /clear (a same-context retry cannot reliably fix it).'
        ) -join ' '
        [Console]::Error.WriteLine($msg)
        exit 2
    }

    exit 0
}
catch {
    # Never let detector failure break the turn or block downstream Stop hooks.
    exit 0
}
