import { integer, pgTable, serial, text, timestamp } from "drizzle-orm/pg-core";

/**
 * ইউজারের তৈরি করা bot.py কনফিগারেশন সংরক্ষণ করে।
 */
export const botConfigs = pgTable("bot_configs", {
  id: serial("id").primaryKey(),
  label: text("label").notNull().default("আমার বট"),
  botToken: text("bot_token").notNull().default(""),
  adminIds: text("admin_ids").notNull().default("[]"),
  botUsername: text("bot_username").notNull().default(""),
  supportUsername: text("support_username").notNull().default(""),
  referBonus: text("refer_bonus").notNull().default("20"),
  minWithdraw: text("min_withdraw").notNull().default("100"),
  usdtRate: text("usdt_rate").notNull().default("122"),
  welcomeOffer: text("welcome_offer").notNull().default(""),
  paymentNumbers: text("payment_numbers").notNull().default("{}"),
  downloads: integer("downloads").notNull().default(0),
  createdAt: timestamp("created_at").notNull().defaultNow(),
  updatedAt: timestamp("updated_at").notNull().defaultNow(),
});

/** ডাউনলোড অ্যাক্টিভিটি লগ */
export const downloadLogs = pgTable("download_logs", {
  id: serial("id").primaryKey(),
  configId: integer("config_id"),
  source: text("source").notNull().default("default"),
  createdAt: timestamp("created_at").notNull().defaultNow(),
});

export type BotConfig = typeof botConfigs.$inferSelect;
export type NewBotConfig = typeof botConfigs.$inferInsert;
