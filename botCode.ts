import fs from "node:fs";
import path from "node:path";

export const BOT_FILE = path.join(process.cwd(), "public", "bot.py");

export interface GenerateInput {
  botToken?: string;
  adminIds?: string;
  botUsername?: string;
  supportUsername?: string;
  referBonus?: string;
  minWithdraw?: string;
  usdtRate?: string;
  welcomeOffer?: string;
  paymentNumbers?: Record<string, string>;
}

export interface ChangeLine {
  label: string;
  before: string;
  after: string;
}

export interface GenerateResult {
  code: string;
  changes: ChangeLine[];
}

const SAFE = (value: string) =>
  String(value ?? "")
    .replace(/[\r\n]+/g, " ")
    .replace(/["\\]/g, "")
    .trim();

export function readBotCode(): string {
  return fs.readFileSync(BOT_FILE, "utf-8");
}

function replaceOnce(source: string, pattern: RegExp, value: string): [string, boolean] {
  if (!pattern.test(source)) return [source, false];
  return [source.replace(pattern, () => value), true];
}

function settingLine(key: string, indent = "    "): RegExp {
  return new RegExp(`^${indent}"${key}":\\s*"[^"]*"`, "m");
}

/**
 * bot.py এর কনফিগ লাইনগুলো ইউজারের দেওয়া ভ্যালু দিয়ে রিপ্লেস করে।
 */
export function applyConfig(source: string, input: GenerateInput): GenerateResult {
  const changes: ChangeLine[] = [];
  let code = source;

  const push = (label: string, before: string, after: string) => {
    if (before !== after) changes.push({ label, before, after });
  };

  const token = SAFE(input.botToken ?? "");
  if (token) {
    const pattern = /^BOT_TOKEN = "[^"]*"/m;
    const before = code.match(pattern)?.[0] ?? "";
    const [next, ok] = replaceOnce(code, pattern, `BOT_TOKEN = "${token}"`);
    if (ok) {
      code = next;
      push("BOT_TOKEN", before, `BOT_TOKEN = "${token}"`);
    }
  }

  const admins = SAFE(input.adminIds ?? "");
  if (admins) {
    const numbers = admins
      .split(/[,\s]+/)
      .map((part) => part.replace(/[^\d-]/g, ""))
      .filter(Boolean);
    if (numbers.length > 0) {
      const pattern = /^ADMIN_IDS = \[[^\]]*\]/m;
      const before = code.match(pattern)?.[0] ?? "";
      const after = `ADMIN_IDS = [${numbers.join(", ")}]`;
      const [next, ok] = replaceOnce(code, pattern, after);
      if (ok) {
        code = next;
        push("ADMIN_IDS", before, after);
      }
    }
  }

  const simpleSettings: Array<[string, string | undefined, string]> = [
    ["bot_username", input.botUsername, "🤖 বট ইউজারনেম"],
    ["support_username", input.supportUsername, "📞 সাপোর্ট ইউজারনেম"],
    ["refer_bonus", input.referBonus, "👥 রেফার বোনাস"],
    ["min_withdraw", input.minWithdraw, "🔻 মিনিমাম উইথড্র"],
    ["usdt_rate", input.usdtRate, "💱 USDT রেট"],
  ];

  for (const [key, raw, label] of simpleSettings) {
    const value = SAFE(raw ?? "");
    if (!value) continue;
    const pattern = settingLine(key);
    const before = code.match(pattern)?.[0]?.trim() ?? "";
    const after = `"${key}": "${value}"`;
    const [next, ok] = replaceOnce(code, pattern, `    ${after}`);
    if (ok) {
      code = next;
      push(label, before, after);
    }
  }

  const offer = (input.welcomeOffer ?? "").replace(/["\\]/g, "").trim();
  if (offer) {
    const value = offer.replace(/\r?\n/g, "\\n");
    const pattern = settingLine("welcome_offer");
    const before = code.match(pattern)?.[0]?.trim() ?? "";
    const after = `"welcome_offer": "${value}"`;
    const [next, ok] = replaceOnce(code, pattern, `    ${after}`);
    if (ok) {
      code = next;
      push("🎉 ওয়েলকাম অফার", before, after);
    }
  }

  const payments = input.paymentNumbers ?? {};
  const paymentLabels: Record<string, string> = {
    bkash: "📱 বিকাশ নাম্বার",
    nagad: "💳 নগদ নাম্বার",
    rocket: "🚀 রকেট নাম্বার",
    usdt_binance: "🟨 Binance (USDT)",
    usdt_bitget: "🟦 Bitget (USDT)",
  };
  for (const key of Object.keys(paymentLabels)) {
    const value = SAFE(payments[key] ?? "");
    if (!value) continue;
    const pattern = new RegExp(`^(\\s*"${key}":\\s*\\{[^\\n]*?"num":\\s*")[^"]*(")`, "m");
    const match = code.match(pattern);
    if (!match) continue;
    const before = match[0].trim();
    code = code.replace(pattern, (_full: string, p1: string, p2: string) => `${p1}${value}${p2}`);
    push(paymentLabels[key], before.replace(/\s+/g, " ").slice(0, 70), value);
  }

  return { code, changes };
}

export function codeStats(code: string) {
  const lines = code.split("\n").length;
  const callbacks = (code.match(/@dp\.callback_query/g) ?? []).length;
  const messages = (code.match(/@dp\.message/g) ?? []).length;
  const tables = (code.match(/CREATE TABLE IF NOT EXISTS (\w+)/g) ?? []).map((item) =>
    item.replace("CREATE TABLE IF NOT EXISTS ", ""),
  );
  return { lines, callbacks, messages, tables, sizeKb: Math.round((Buffer.byteLength(code, "utf-8") / 1024) * 10) / 10 };
}
