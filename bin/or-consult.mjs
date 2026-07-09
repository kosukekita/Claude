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
 *
 * フォールバック: OpenRouter が 402(残高切れ)を返したら、同じ messages を AtlasCloud
 *   (OpenAI 互換 /v1/chat/completions)へ投げ直す。どのプロバイダで応答したかは必ず stderr に
 *   出す(黙って別アカウントへ課金が移らないように)。429 はフォールバックせず OpenRouter の
 *   エラーとして扱う(残高切れではないため)。--no-fallback で無効化できる。
 *   AtlasCloud キー: ~/.config/atlascloud.key(1行,chmod 600) → 環境変数 $ATLASCLOUD_API_KEY。
 */
import fs from "node:fs";
import os from "node:os";
import path from "node:path";

const KEY_PATH = path.join(os.homedir(), ".config", "openrouter.key");
const API = "https://openrouter.ai/api/v1";
const ATLAS_KEY_PATH = path.join(os.homedir(), ".config", "atlascloud.key");
// AtlasCloud の LLM は /v1(OpenAI 互換)。画像/動画は /api/v1 で base が違うが、ここでは無関係。
const ATLAS_API = "https://api.atlascloud.ai/v1";
// 🔑 既定は openai/gpt-5.5(Codex=OpenAI系の代替、= "Claude 以外の独立視点")。
//   ※Claude 系の知見でよいなら OpenRouter を使わず Claude Code 自身(このセッション)が答える
//     こと。OpenRouter で anthropic/claude-* を呼ぶのは Claude 契約と OpenRouter の二重課金で無駄。
//     OpenRouter フォールバックは「Codex/Grok がレート制限 かつ Claude 以外の視点が要る」ときだけ。
//   gpt-5.5(proでない)は少トークンで content を返し空応答が起きにくい。pro/o3-pro 等の重い
//   reasoning モデルは max-tokens を大きく(12000+)しないと content が空になる。
const DEFAULT_MODEL = "openai/gpt-5.5";

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

// AtlasCloud キー: ~/.config/atlascloud.key を優先し、無ければ $ATLASCLOUD_API_KEY。
// どちらも無ければ null(呼び出し側でフォールバック不可を案内)。改行混入で落ちないよう trim 必須。
function readAtlasKey() {
  try {
    const k = fs.readFileSync(ATLAS_KEY_PATH, "utf8").trim();
    if (k) return k;
  } catch {}
  const env = (process.env.ATLASCLOUD_API_KEY || "").trim();
  return env || null;
}

// OpenRouter の model id を AtlasCloud のカタログ表記に変換。x-ai/* → xai/*(ハイフン無し)。
// それ以外は概ね同じ id なのでそのまま渡す(未知の id も無変換で通す)。
function toAtlasModel(model) {
  const PREFIX = { "x-ai/": "xai/" };
  for (const [from, to] of Object.entries(PREFIX)) {
    if (model.startsWith(from)) return to + model.slice(from.length);
  }
  return model;
}

function parseArgs(argv) {
  const a = { model: DEFAULT_MODEL, maxTokens: 4000, system: null, stdin: false, list: false, noFallback: false, prompt: null };
  const rest = [];
  for (let i = 0; i < argv.length; i++) {
    const t = argv[i];
    if (t === "--model") a.model = argv[++i];
    else if (t === "--max-tokens") a.maxTokens = parseInt(argv[++i], 10);
    else if (t === "--system") a.system = argv[++i];
    else if (t === "--stdin") a.stdin = true;
    else if (t === "--list") a.list = true;
    else if (t === "--no-fallback") a.noFallback = true;
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

// 成功時 {ok:true, json}、失敗時 {ok:false, status, body}。402 フォールバック判定を
// 呼び出し側に委ねるため、ここでは process.exit しない。
async function orChat(key, model, messages, maxTokens) {
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
  if (r.ok) return { ok: true, json: await r.json() };
  return { ok: false, status: r.status, body: await r.text() };
}

// AtlasCloud LLM は OpenAI 互換なのでボディ/レスポンス形は OpenRouter と同じ。
// エラー封筒は {code,msg}(OpenAI 形ではない)ので、失敗時は body を生で呼び出し側に返す。
async function atlasChat(key, model, messages, maxTokens) {
  const r = await fetch(`${ATLAS_API}/chat/completions`, {
    method: "POST",
    headers: {
      Authorization: `Bearer ${key}`,
      "Content-Type": "application/json",
    },
    body: JSON.stringify({ model, messages, max_tokens: maxTokens }),
  });
  if (r.ok) return { ok: true, json: await r.json() };
  return { ok: false, status: r.status, body: await r.text() };
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

  let res = await orChat(key, args.model, messages, args.maxTokens);
  let provider = "openrouter";
  let sentModel = args.model;

  // 402 = OpenRouter 残高切れ。429(レート制限)ではフォールバックしない。
  if (!res.ok && res.status === 402 && !args.noFallback) {
    const atlasKey = readAtlasKey();
    if (!atlasKey) {
      console.error("OpenRouter が 402(残高切れ)。AtlasCloud キーが無いためフォールバックできません。");
      console.error(`AtlasCloud キーを ~/.config/atlascloud.key に置く(chmod 600)か $ATLASCLOUD_API_KEY を設定すればフォールバックできます。`);
      process.exit(1);
    }
    sentModel = toAtlasModel(args.model);
    console.error(`[or-consult] openrouter 402 -> falling back to atlascloud (model: ${sentModel})`);
    res = await atlasChat(atlasKey, sentModel, messages, args.maxTokens);
    provider = "atlascloud";
  }

  if (!res.ok) {
    if (provider === "openrouter") {
      console.error(`OpenRouter HTTP ${res.status}: ${res.body.slice(0, 400)}`);
      if (res.status === 402) console.error("→ 残高不足。--max-tokens を下げるか https://openrouter.ai/settings/credits で追加(または AtlasCloud キーを置いてフォールバック)。");
      if (res.status === 429) console.error("→ レート制限。少し待って再試行(429 はフォールバックしません)。");
    } else {
      // AtlasCloud の非2xx。封筒は {code,msg}。404/400 はキー不正(認証失敗)やモデル名不正でも起きる。
      console.error(`AtlasCloud HTTP ${res.status}: ${res.body.slice(0, 400)}`);
      console.error("→ AtlasCloud が非2xx。404/400 は AtlasCloud キー不正(認証失敗)やモデル名不正の可能性。~/.config/atlascloud.key を確認してください。");
    }
    process.exit(1);
  }

  const d = res.json;
  const msg = d.choices?.[0]?.message?.content ?? "(空の応答)";
  process.stdout.write(msg + "\n");
  const u = d.usage || {};
  console.error(`\n[or-consult provider=${provider} model=${d.model ?? sentModel} tokens=${u.total_tokens ?? "?"}]`);
}

main().catch((e) => {
  console.error("or-consult error:", e.message);
  process.exit(1);
});
