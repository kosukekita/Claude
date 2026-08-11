#!/usr/bin/node

import { existsSync, readFileSync } from "node:fs";
import { spawnSync } from "node:child_process";
import { join } from "node:path";

const EMAIL_TO = "u879269j@gmail.com";
const EMAIL_FROM = "u879269j@gmail.com";
const SMTP_PASS_FILE = join(process.env.HOME, ".config", "gmail-smtp.pass");
const CURL_CANDIDATES = ["/home/kita/anaconda3/bin/curl", "/usr/bin/curl"];

function fail(message) {
  process.stderr.write(`ERROR: ${message}\n`);
  process.exit(1);
}

if (process.argv.length !== 3) {
  fail("usage: send_mail.mjs REPORT_PATH");
}
const reportPath = process.argv[2];
if (!existsSync(reportPath)) {
  fail(`report not found: ${reportPath}`);
}
if (!existsSync(SMTP_PASS_FILE)) {
  fail(`SMTP password file not found: ${SMTP_PASS_FILE}`);
}
const curl = CURL_CANDIDATES.find((candidate) => existsSync(candidate));
if (!curl) {
  fail("curl executable not found");
}

const report = readFileSync(reportPath, "utf8");
const password = readFileSync(SMTP_PASS_FILE, "utf8").trim();
const encodedSubject = Buffer.from(
  "週次 Claude config-audit: 設定の変化を検出",
  "utf8",
).toString("base64");
const encodedBody = Buffer.from(report, "utf8")
  .toString("base64")
  .replace(/(.{76})/g, "$1\r\n");
const messageIdHeader = `Message-ID: <config-audit.${Date.now()}.${process.pid}@gmail.com>`;
const mime = [
  `From: ${EMAIL_FROM}`,
  `To: ${EMAIL_TO}`,
  `Subject: =?UTF-8?B?${encodedSubject}?=`,
  `Date: ${new Date().toUTCString()}`,
  messageIdHeader,
  "MIME-Version: 1.0",
  'Content-Type: text/plain; charset="UTF-8"',
  "Content-Transfer-Encoding: base64",
  "",
  encodedBody,
  "",
].join("\r\n");

const result = spawnSync(
  curl,
  [
    "--ssl-reqd",
    "--url",
    "smtps://smtp.gmail.com:465",
    "--user",
    `${EMAIL_FROM}:${password}`,
    "--mail-from",
    EMAIL_FROM,
    "--mail-rcpt",
    EMAIL_TO,
    "--upload-file",
    "-",
    "--silent",
    "--show-error",
  ],
  { input: mime, encoding: "utf8" },
);
if (result.error) {
  fail(result.error.message);
}
if (result.status !== 0) {
  fail(`curl exit ${result.status}: ${(result.stderr || "").trim()}`);
}
process.stdout.write(`SENT OK to ${EMAIL_TO}\n`);
