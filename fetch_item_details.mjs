/**
 * fetch_item_details.mjs <item_id>
 * Fetches item details from TLDB's internal __data.json endpoint.
 * Decodes devalue format and computes stats at enchant level 12.
 * Outputs clean JSON to stdout.
 */

import * as devalue from "devalue";

const item_id = process.argv[2];
if (!item_id) {
  console.error("Usage: node fetch_item_details.mjs <item_id>");
  process.exit(1);
}

const API_URL = `https://tldb.info/db/item/${item_id}/__data.json`;

let resp;
try {
  resp = await fetch(API_URL, { headers: { "User-Agent": "Mozilla/5.0" } });
} catch (e) {
  console.error("NETWORK_ERROR:" + e.message);
  process.exit(1);
}

if (!resp.ok) {
  console.error("HTTP_ERROR:" + resp.status);
  process.exit(1);
}

const json = await resp.json();
const dataNode = json.nodes?.find((e) => e?.type === "data");
if (!dataNode) {
  console.error("NO_DATA_NODE");
  process.exit(1);
}

const apiData = devalue.unflatten(dataNode.data);
const item = apiData?.data;

if (!item) {
  console.error("NO_ITEM");
  process.exit(1);
}

// ── Helpers ───────────────────────────────────────────────────────────────────

function formatValue(value, format, multiply) {
  const computed = value * (multiply ?? 1);
  if (!format || format === "{0}") return String(Math.round(computed * 100) / 100);
  return format.replace("{0}", Math.round(computed * 100) / 100);
}

function computeStatAtLevel(stat, level) {
  const bonuses = (stat.enchant_values ?? [])
    .slice(0, level)
    .reduce((a, b) => a + b, 0);
  return stat.value + bonuses;
}

// ── Parse stats at enchant level 12 ──────────────────────────────────────────

const ENCHANT_LEVEL = 12;

function parseStatGroup(statList) {
  if (!Array.isArray(statList)) return [];
  return statList.map((stat) => {
    const raw = computeStatAtLevel(stat, ENCHANT_LEVEL);
    return {
      key: stat.key,
      name: stat.name,
      value: formatValue(raw, stat.format, stat.multiply),
    };
  });
}

const stats = item.stats ?? {};

// Main stats (Damage, Attack Speed, Range…)
const mainStats = parseStatGroup(stats.main_stats);

// Extra fixed stats (Fortitude, Perception…)
const extraStats = parseStatGroup(stats.extra_fixed_stats);

// ── Unique skill ──────────────────────────────────────────────────────────────
const skill = item.skill_unique ?? null;

// ── Output ────────────────────────────────────────────────────────────────────
const output = {
  id: item.id,
  name: item.name,
  rarity: item.rarity,
  icon: item.icon,
  description: item.description,
  type: item.typeName,
  skill: skill
    ? {
        name: skill.name,
        description: Array.isArray(skill.description)
          ? skill.description.join("")
          : skill.description ?? "",
      }
    : null,
  main_stats: mainStats,
  extra_stats: extraStats,
  enchant_level: ENCHANT_LEVEL,
};

process.stdout.write(JSON.stringify(output));
