#!/usr/bin/env node
// detect-leaked-toolcall.mjs
// Stop hook (cross-OS): detect raw tool-call markup that LEAKED into the
// assistant's finished message as plain text instead of being executed as a
// real tool call.
//
// Background (verified against live transcripts, 2026-06-15 / re-confirmed on
// Linux 2026-06-23): a harness-level serialization defect occasionally drops
// the tool-call open marker's namespace prefix, degrading it to a bare token
// ("court"/"count"/"call") followed by literal <invoke name=...> markup. The
// harness then fails to parse it as a tool call and renders it as visible text,
// so the operation NEVER RUNS and fails silently.
//
// WHY node (not bash/jq/python): on this rig `jq` and `python3` resolve to the
// anaconda copies, whose libtinfo.so.6 pollutes LD_LIBRARY_PATH (known issue,
// breaks soffice). Only `/usr/bin/node` is clean. node also parses the JSONL
// transcript robustly and runs identically on Windows and Linux, so one file
// replaces the PowerShell-only .ps1 that silently no-op'd on Linux.
//
// This hook cannot prevent or repair the leak (it happens inside the model-
// output boundary that no hook can observe). It only DETECTS the leak in the
// just-finished assistant turn and, via exit code 2, tells the model to re-issue
// the dropped tool call. (Stop hooks: exit 2 => stderr is shown to the model and
// it is asked to continue, which is exactly the retry we want.)
//
// Exit codes:
//   0 = no leak detected (silent, normal) — also used for any internal error so
//       a detector fault never breaks the turn or blocks downstream Stop hooks.
//   2 = leak detected -> stderr advisory shown to the model so it retries.

import { readFileSync } from 'node:fs';

function readStdin() {
  try {
    return readFileSync(0, 'utf8');
  } catch {
    return '';
  }
}

function stripCodeSpans(paragraph) {
  let result = '';
  let i = 0;
  while (i < paragraph.length) {
    if (paragraph[i] === '`') {
      let start = i;
      while (i < paragraph.length && paragraph[i] === '`') {
        i++;
      }
      const tickCount = i - start;
      let foundClose = false;
      let j = i;
      while (j < paragraph.length) {
        if (paragraph[j] === '`') {
          let closeStart = j;
          while (j < paragraph.length && paragraph[j] === '`') {
            j++;
          }
          const closeCount = j - closeStart;
          if (closeCount === tickCount) {
            const codeSpan = paragraph.slice(start, j);
            result += codeSpan.replace(/[^\r\n]/g, ' ');
            i = j;
            foundClose = true;
            break;
          }
        } else {
          j++;
        }
      }
      if (!foundClose) {
        result += paragraph.slice(start, i);
      }
    } else {
      result += paragraph[i];
      i++;
    }
  }
  return result;
}

function stripMarkdownExclusions(text) {
  if (typeof text !== 'string') return '';
  try {
    if (process.env.__TEST_FORCE_STRIP_ERROR === '1') {
      throw new Error('Forced exception for testing');
    }
    const lines = text.split(/\r?\n/);
    const resultLines = new Array(lines.length);
    let i = 0;

    while (i < lines.length) {
      const line = lines[i];

      const fenceMatch = line.match(/^ {0,3}(`{3,}|~{3,})(.*)$/);
      if (fenceMatch) {
        const fenceChars = fenceMatch[1];
        const infoString = fenceMatch[2];
        const fenceChar = fenceChars[0];
        const fenceLength = fenceChars.length;

        if (!(fenceChar === '`' && infoString.includes('`'))) {
          let closeIndex = -1;
          for (let j = i + 1; j < lines.length; j++) {
            const closeMatch = lines[j].match(/^ {0,3}(`{3,}|~{3,})\s*$/);
            if (
              closeMatch &&
              closeMatch[1][0] === fenceChar &&
              closeMatch[1].length >= fenceLength
            ) {
              closeIndex = j;
              break;
            }
          }

          if (closeIndex !== -1) {
            for (let k = i; k <= closeIndex; k++) {
              resultLines[k] = '';
            }
            i = closeIndex + 1;
            continue;
          }
        }
      }

      if (/^\s*>/.test(line)) {
        resultLines[i] = '';
        i++;
        continue;
      }

      resultLines[i] = line;
      i++;
    }

    const processedLines = [];
    let currentParagraphLines = [];

    function flushParagraph() {
      if (currentParagraphLines.length === 0) return;
      const paragraphText = currentParagraphLines.join('\n');
      const strippedParagraph = stripCodeSpans(paragraphText);
      const splitBack = strippedParagraph.split('\n');
      for (const pl of splitBack) {
        processedLines.push(pl);
      }
      currentParagraphLines = [];
    }

    for (let idx = 0; idx < resultLines.length; idx++) {
      const l = resultLines[idx];
      if (/^\s*$/.test(l)) {
        flushParagraph();
        processedLines.push(l);
      } else {
        currentParagraphLines.push(l);
      }
    }
    flushParagraph();

    return processedLines.join('\n');
  } catch {
    return '';
  }
}

function main() {
  const raw = readStdin();
  if (!raw || !raw.trim()) return 0;

  let payload;
  try {
    payload = JSON.parse(raw);
  } catch {
    return 0;
  }

  const tp = payload && payload.transcript_path;
  if (!tp || typeof tp !== 'string') return 0;

  // Stop hooks can fire in a loop; honor stop_hook_active to avoid re-nagging.
  if (payload.stop_hook_active === true) return 0;

  let lines;
  try {
    lines = readFileSync(tp, 'utf8').split(/\r?\n/);
  } catch {
    return 0;
  }
  if (!lines.length) return 0;

  // Scan from the end for the most recent assistant turn; concatenate its TEXT
  // blocks only. Real tool_use blocks executed fine — a leak lives in a "text"
  // block.
  let assistantText = null;
  for (let i = lines.length - 1; i >= 0; i--) {
    const line = lines[i];
    if (!line || !line.trim()) continue;
    let obj;
    try {
      obj = JSON.parse(line);
    } catch {
      continue;
    }

    const role = obj.type || (obj.message && obj.message.role);
    if (role !== 'assistant') continue;

    const content =
      (obj.message && obj.message.content) || obj.content || null;
    if (!content) continue;

    const parts = [];
    if (Array.isArray(content)) {
      for (const block of content) {
        if (block && block.type === 'text' && typeof block.text === 'string') {
          parts.push(block.text);
        }
      }
    } else if (typeof content === 'string') {
      parts.push(content);
    }
    assistantText = parts.join('\n');
    break;
  }

  if (!assistantText || !assistantText.trim()) return 0;

  // --- Detection -----------------------------------------------------------
  const textToEvaluate = stripMarkdownExclusions(assistantText);
  if (!textToEvaluate || !textToEvaluate.trim()) return 0;

  // Signal A: literal tool-call markup present as text.
  const markupRegex = /<invoke\s+name=|<\/invoke>|<parameter\s+name=|<function_calls>|<\/antml:invoke>|<invoke\s+name=/;
  // Signal B: a degraded open-marker token alone on its own line, immediately
  // followed by a markup line. The exact observed shape.
  const degradeRegex = /(^|\n)\s*(court|count|call)\s*\r?\n\s*<(antml:)?(invoke|parameter|function_calls)/;

  if (markupRegex.test(textToEvaluate) || degradeRegex.test(textToEvaluate)) {
    const msg = [
      'LEAKED TOOL CALL DETECTED: the previous assistant turn emitted raw',
      'tool-call markup (e.g. <invoke name=...>) as plain TEXT instead of',
      'executing it, so that tool call DID NOT RUN. This is the known harness',
      'serialization-leak bug. Re-issue the dropped tool call now. If it leaks',
      'again on retry, the context is polluted: advise the user to run /clear',
      '(a same-context retry cannot reliably fix it).',
    ].join(' ');
    process.stderr.write(msg + '\n');
    return 2;
  }

  return 0;
}

try {
  process.exit(main());
} catch {
  process.exit(0);
}
