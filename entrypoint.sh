#!/bin/bash
set -e

echo "=== [1/2] Refreshing TLDB item list ==="
node /app/fetch_items.mjs

echo "=== [2/2] Starting Discord bot ==="
exec python /app/bot.py
