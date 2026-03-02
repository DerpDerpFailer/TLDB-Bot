/**
 * fetch_items.mjs
 * Fetches the full item list from TLDB's internal API and saves it as items.json.
 * Uses the documented endpoint: https://tldb.info/internal-docs
 *
 * Run once at container startup (before bot.py).
 */

import * as devalue from "devalue";
import { decompress } from "compress-json";
import { writeFileSync, mkdirSync } from "fs";

const DATA_PATH = "/app/data/items.json";
const API_URL = "https://tldb.info/auction-house/__data.json";

console.log("Fetching TLDB item list...");

let resp;
try {
  resp = await fetch(API_URL, { headers: { "User-Agent": "Mozilla/5.0" } });
} catch (e) {
  console.error("Network error fetching item list:", e.message);
  process.exit(1);
}

if (!resp.ok) {
  console.error(`HTTP ${resp.status} from TLDB API`);
  process.exit(1);
}

const json = await resp.json();

// SvelteKit __data.json: find the "data" node
const dataNode = json.nodes?.find((e) => e?.type === "data");
if (!dataNode) {
  console.error("Could not find data node in TLDB response");
  process.exit(1);
}

// Decode devalue → plain JS object
const apiData = devalue.unflatten(dataNode.data);

if (!apiData?.items) {
  console.error("No 'items' key in decoded API data");
  process.exit(1);
}

// Decode compress-json
const items = decompress(apiData.items);

if (!Array.isArray(items) || items.length === 0) {
  console.error("Items list is empty after decompress");
  process.exit(1);
}

// Keep only what's needed for autocomplete: id + name
const simplified = items
  .filter((item) => item?.id && item?.name)
  .map((item) => ({ id: item.id, name: item.name }));

mkdirSync("/app/data", { recursive: true });
writeFileSync(DATA_PATH, JSON.stringify(simplified));

console.log(`Saved ${simplified.length} items to ${DATA_PATH}`);
