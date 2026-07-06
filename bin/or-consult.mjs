#!/usr/bin/env node
/**
 * or-consult.mjs — OpenRouter フォールバック相談ツール
 *
 * Codex CLI / Grok CLI がレート制限・障害で使えないとき、Claude Code から
 * OpenRouter API 経由で代替モデル(gpt-5.5-pro / claude-sonnet-5 / grok-4.3 等)に
 * 相談を続けるための最小ラッパー。CLI に依存せず OpenRouter を直接叩く。
 *
 * APIキー: ~/.config/openrouter.key (chmod 600 推奨)。中身は "sk-or-..." の1行。
 *
 * 使い方:
 *   node ~/.claude/bin/or-consult.mjs "<プロンプト>" [--model <id>] [--max-tokens N] [--system <text>]
 *   echo "<長いプロンプト>" | node ~/.claude/bin/or-consult.mjs --stdin [--model <id>]
 *   node ~/.claude/bin/or-consult.mjs --list        # 主要な利用可能モデルを表示
 *
 * 既定モデル: openai/gpt-5.5-pro (Codex=OpenAI系の代替に最も近い)。
 * 代替候補: anthropic/claude-sonnet-5, x-ai/grok-4.3, google/gemini-2.5-pro, openai/o3-pro
 *
 * 注意: OpenRouter は従量課金。残高不足時は HTTP 402 が返る。max_tokens を明示しないと
 *   モデル上限を要求して 402 になりやすいので、既定で 4000 を付ける。
 */
import fs from "node:fs";
import os from "node:os";
import path from "node:path";

const KEY_PATH = path.join(os.homedir(), ".config", "openrouter.key");
const API = "https://openrouter.ai/api/v1";
// 既定は非reasoningの claude-sonnet-5(max-tokens 内で必ず content を返す)。
// gpt-5.5-pro / o3-pro 等の reasoning モデルは max-tokens が小さいと推論トークンで消費され
// content が空になるため、それらを使うときは --max-tokens を大きく(8000+)する。
const DEFAULT_MODEL = "anthropic/claude-sonnet-5";

function readKey() {
  try {
    const k = fs.readFileSync(KEY_PATH, "utf8").trim();
    if (!k) throw new Error("empty");
    return k;
  } catch {
    console.error(`OpenRouter APIキーが読めません: ${KEY_PATH}\n` +
      `~/.config/openrouter.key に "sk-or-..." を1行で置いてください(chmod 600)。`);
    process.exit(2);
  }
}

function parseArgs(argv) {
  const a = { model: DEFAULT_MODEL, maxTokens: 4000, system: null, stdin: false, list: false, prompt: null };
  const rest = [];
  for (let i = 0; i < argv.length; i++) {
    const t = argv[i];
    if (t === "--model") a.model = argv[++i];
    else if (t === "--max-tokens") a.maxTokens = parseInt(argv[++i], 10);
    else if (t === "--system") a.system = argv[++i];
    else if (t === "--stdin") a.stdin = true;
    else if (t === "--list") a.list = true;
    else rest.push(t);
  }
  if (rest.length) a.prompt = rest.join(" ");
  return a;
}

async function readStdin() {
  const chunks = [];
  for await (const c of process.stdin) chunks.push(c);
  return Buffer.concat(chunks).toString("utf8").trim();
}

async function listModels(key) {
  const r = await fetch(`${API}/models`, { headers: { Authorization: `Bearer ${key}` } });
  const d = await r.json();
  const ids = (d.data || []).map((m) => m.id);
  const groups = ["openai/gpt-5", "openai/o3", "anthropic/claude", "x-ai/grok-4", "google/gemini-2.5"];
  for (const g of groups) {
    const hit = ids.filter((m) => m.startsWith(g)).slice(0, 4);
    if (hit.length) console.log(`${g}*: ${hit.join(", ")}`);
  }
  console.log(`\n総モデル数: ${ids.length}  (既定: ${DEFAULT_MODEL})`);
}

async function chat(key, model, messages, maxTokens) {
  const r = await fetch(`${API}/chat/completions`, {
    method: "POST",
    headers: {
      Authorization: `Bearer ${key}`,
      "Content-Type": "application/json",
      "HTTP-Referer": "https://claude.ai/code",
      "X-Title": "claude-code-or-fallback",
    },
    body: JSON.stringify({ model, messages, max_tokens: maxTokens }),
  });
  if (!r.ok) {
    const body = await r.text();
    console.error(`OpenRouter HTTP ${r.status}: ${body.slice(0, 400)}`);
    if (r.status === 402) console.error("→ 残高不足。--max-tokens を下げるか https://openrouter.ai/settings/credits で追加。");
    process.exit(1);
  }
  return r.json();
}

async function main() {
  const args = parseArgs(process.argv.slice(2));
  const key = readKey();
  if (args.list) return listModels(key);

  let prompt = args.prompt;
  if (args.stdin || (!prompt && !process.stdin.isTTY)) prompt = await readStdin();
  if (!prompt) {
    console.error('プロンプトがありません。使い方: or-consult.mjs "<質問>" [--model <id>] [--max-tokens N]');
    process.exit(2);
  }

  const messages = [];
  if (args.system) messages.push({ role: "system", content: args.system });
  messages.push({ role: "user", content: prompt });

  const d = await chat(key, args.model, messages, args.maxTokens);
  const msg = d.choices?.[0]?.message?.content ?? "(空の応答)";
  process.stdout.write(msg + "\n");
  const u = d.usage || {};
  console.error(`\n[or-consult model=${d.model} tokens=${u.total_tokens ?? "?"}]`);
}

main().catch((e) => {
  console.error("or-consult error:", e.message);
  process.exit(1);
});
