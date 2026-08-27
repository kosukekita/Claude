#!/usr/bin/env bash
set -u

NODE=/usr/bin/node
DEFAULT_MODEL=free-kimi-k3
DEFAULT_MAX_TOKENS=8000

usage() {
  printf 'Usage: %s [--grant] [--dry-run] [--model NAME] [--max-tokens N] FILE.md|FILE.txt\n' \
    "$(basename -- "$0")" >&2
}

die() {
  printf 'kimi-proofread: %s\n' "$1" >&2
  exit 1
}

grant=0
dry_run=0
model=$DEFAULT_MODEL
max_tokens=$DEFAULT_MAX_TOKENS
input_file=

while (($# > 0)); do
  case $1 in
    --grant)
      grant=1
      shift
      ;;
    --dry-run)
      dry_run=1
      shift
      ;;
    --model)
      (($# >= 2)) || die '--model requires a model name'
      [[ -n $2 ]] || die '--model requires a non-empty model name'
      model=$2
      shift 2
      ;;
    --max-tokens)
      (($# >= 2)) || die '--max-tokens requires an integer'
      max_tokens=$2
      shift 2
      ;;
    --help|-h)
      usage
      exit 0
      ;;
    --)
      shift
      (($# > 0)) || die 'input file is required'
      [[ -z $input_file ]] || die 'only one input file may be specified'
      input_file=$1
      shift
      (($# == 0)) || die 'only one input file may be specified'
      ;;
    -*)
      die "unknown option: $1"
      ;;
    *)
      [[ -z $input_file ]] || die 'only one input file may be specified'
      input_file=$1
      shift
      ;;
  esac
done

if [[ -z $input_file ]]; then
  usage
  die 'input file is required'
fi

[[ -f $input_file ]] || die "input file does not exist or is not a regular file: $input_file"
[[ -r $input_file ]] || die "input file is not readable: $input_file"
[[ -s $input_file ]] || die "input file is empty: $input_file"

case ${input_file,,} in
  *.md|*.txt) ;;
  *) die 'input file must have a .md or .txt extension' ;;
esac

[[ $max_tokens =~ ^[0-9]+$ ]] || die '--max-tokens must be an integer'
max_tokens_value=$((10#$max_tokens))
((max_tokens_value >= 4000)) || die '--max-tokens must be at least 4000'

[[ -x $NODE ]] || die 'required runtime /usr/bin/node is not available'

mode=live
((dry_run == 1)) && mode=dry-run

exec "$NODE" - "$mode" "$grant" "$model" "$max_tokens_value" "$input_file" <<'NODE'
'use strict';

const fs = require('fs');
const http = require('http');
const path = require('path');

const [, , mode, grantFlag, model, maxTokensText, inputPath] = process.argv;
const maxTokens = Number(maxTokensText);

const generalInstructions = `あなたは日本語文書の校正者です。入力された本文を、次の規則に従って校正してください。
- 冗長表現、二重敬語、ら抜き言葉を修正する。
- 主語と述語の不一致を修正する。
- 一文が長すぎる場合は、意味を変えずに読みやすく分割する。
- AI生成文に見られる紋切り型を除去する。特に「重要なのは」「多角的」「包括的」「と言えるだろう」など、内容を足さない定型表現を避ける。
- 事実、固有名詞、数値は変更しない。新しい事実を追加しない。
- 出力は校正後の本文だけとし、前置き、説明、変更点、注釈を一切書かない。`;

const grantInstructions = `

これは助成金・研究費の申請書です。次の追加規則も必ず守ってください。
- 自明なメタ表記「概念図」「イメージ図」「模式図」「※イメージです」は削除する。実測図との区別が必要な場合は、概念側に注記せず、実測側を「実解析結果」とする。
- 自分を弱く見せる語「未発表」「予備的」「試験的」は、内容を損なわない形で削除または修正する。
- 計画の弱みや不確実性を強調する表現「現時点では確定していない」「〜が立たない場合も」「帰国後の課題とする」は削除または前向きで具体的な計画表現に修正する。
- 口語的な「仕事」は「研究」に修正する。
- ただし、解いた課題の説明（例: 網羅できないため新たな手法を作ったこと）、国内では得がたい留学の必要性、助成が必要な理由、受入条件や年収要件など要件充足を裏づける事実は消さず、意味を保持する。これらを計画の弱み表現と混同しない。`;

function fatal(message) {
  process.stderr.write(`kimi-proofread: ${message}\n`);
  process.exit(1);
}

function readMasterKey(envPath) {
  let envText;
  try {
    envText = fs.readFileSync(envPath, 'utf8');
  } catch (error) {
    fatal(`cannot read LiteLLM credential file: ${envPath}`);
  }

  for (const rawLine of envText.split(/\r?\n/)) {
    const line = rawLine.trim();
    if (!line || line.startsWith('#')) continue;
    const match = line.match(/^(?:export\s+)?LITELLM_MASTER_KEY\s*=\s*(.*)$/);
    if (!match) continue;
    let value = match[1].trim();
    if ((value.startsWith('"') && value.endsWith('"')) ||
        (value.startsWith("'") && value.endsWith("'"))) {
      value = value.slice(1, -1);
    }
    if (value) return value;
  }

  fatal(`LITELLM_MASTER_KEY is missing from ${envPath}`);
}

let inputText;
try {
  inputText = fs.readFileSync(inputPath, 'utf8');
} catch (error) {
  fatal(`cannot read input file: ${inputPath}`);
}

const requestBody = {
  model,
  max_tokens: maxTokens,
  messages: [
    {
      role: 'system',
      content: generalInstructions + (grantFlag === '1' ? grantInstructions : ''),
    },
    {role: 'user', content: inputText},
  ],
};

if (mode === 'dry-run') {
  process.stdout.write(`${JSON.stringify(requestBody, null, 2)}\n`);
  process.exit(0);
}

const home = process.env.HOME;
if (!home) fatal('HOME is not set; cannot locate LiteLLM credentials');
const masterKey = readMasterKey(path.join(home, '.config', 'litellm', 'litellm.env'));
const body = JSON.stringify(requestBody);

const request = http.request(
  {
    hostname: '127.0.0.1',
    port: 4000,
    path: '/v1/chat/completions',
    method: 'POST',
    headers: {
      Authorization: `Bearer ${masterKey}`,
      'Content-Type': 'application/json',
      'Content-Length': Buffer.byteLength(body),
    },
  },
  response => {
    const chunks = [];
    response.setEncoding('utf8');
    response.on('data', chunk => chunks.push(chunk));
    response.on('end', () => {
      if (response.statusCode < 200 || response.statusCode >= 300) {
        fatal(`LiteLLM gateway returned HTTP ${response.statusCode}`);
      }

      let payload;
      try {
        payload = JSON.parse(chunks.join(''));
      } catch (error) {
        fatal('LiteLLM gateway returned invalid JSON');
      }

      const content = payload?.choices?.[0]?.message?.content;
      if (typeof content !== 'string' || content.trim().length === 0) {
        fatal('model returned empty content (reasoning may have exhausted max_tokens)');
      }

      process.stdout.write(content);
      if (!content.endsWith('\n')) process.stdout.write('\n');
    });
  },
);

request.setTimeout(600000, () => {
  request.destroy(new Error('request timed out after 600 seconds'));
});
request.on('error', error => {
  fatal(`cannot reach LiteLLM gateway: ${error.message}`);
});
request.end(body);
NODE
