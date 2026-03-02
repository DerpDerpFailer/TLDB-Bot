import os
import re
import json
import time
import asyncio
import threading
import requests
from bs4 import BeautifulSoup
import discord
from discord import app_commands

TOKEN = os.getenv("DISCORD_TOKEN")
ITEMS_PATH = "/app/data/items.json"
ITEMS_REFRESH_HOURS = 24

intents = discord.Intents.default()
client = discord.Client(intents=intents)
tree = app_commands.CommandTree(client)

# ==========================
# ITEMS LIST (chargée en RAM)
# ==========================
_items: list[dict] = []         # [{id, name}]
_items_loaded_at: float = 0.0


def load_items_from_disk() -> None:
    """Charge items.json en mémoire."""
    global _items, _items_loaded_at
    try:
        with open(ITEMS_PATH, "r", encoding="utf-8") as f:
            _items = json.load(f)
        _items_loaded_at = time.time()
        print(f"Loaded {len(_items)} items from {ITEMS_PATH}")
    except Exception as e:
        print(f"Warning: could not load items list: {e}")
        _items = []


def refresh_items_if_needed() -> None:
    """Re-lance fetch_items.mjs si le cache est trop vieux (>24h)."""
    age_hours = (time.time() - _items_loaded_at) / 3600
    if age_hours < ITEMS_REFRESH_HOURS:
        return

    print(f"Item list is {age_hours:.1f}h old, refreshing...")
    try:
        import subprocess
        result = subprocess.run(
            ["node", "/app/fetch_items.mjs"],
            capture_output=True, text=True, timeout=60
        )
        if result.returncode == 0:
            load_items_from_disk()
            print("Item list refreshed successfully.")
        else:
            print(f"fetch_items.mjs failed: {result.stderr}")
    except Exception as e:
        print(f"Could not refresh items: {e}")


def search_items_local(query: str) -> list[dict]:
    """Filtre la liste en RAM — insensible à la casse, recherche partielle."""
    refresh_items_if_needed()
    q = query.lower()
    return [item for item in _items if q in item["name"].lower()][:25]


# ==========================
# FETCH ITEM DETAILS
# ==========================
def clean_text(text):
    return re.sub(r'\s+', ' ', text).strip()


def fetch_tldb_item(item_id: str) -> dict | None:
    url = f"https://tldb.info/db/item/{item_id}"
    headers = {"User-Agent": "Mozilla/5.0"}

    try:
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()
    except requests.exceptions.RequestException:
        return None

    soup = BeautifulSoup(response.text, "lxml")

    name_tag = soup.find("h1")
    if not name_tag:
        return None
    item_name = clean_text(name_tag.text)

    image_url = None
    header = soup.find("div", class_=re.compile("item-header"))
    if header:
        img = header.find("img")
        if img and img.get("src"):
            image_url = img["src"]

    rarity = "Unknown"
    rarity_tag = soup.find("span", class_=re.compile("item-header-rarity-name"))
    if rarity_tag:
        rarity = clean_text(rarity_tag.text)

    description = ""
    desc_tag = soup.find("h2", class_="item-description")
    if desc_tag:
        description = clean_text(desc_tag.text)

    stats = []
    base_stats_text = soup.find(string=re.compile("Base Stats", re.I))
    if base_stats_text:
        base_section = base_stats_text.find_parent()
        current = base_section.find_next()
        while current:
            if current.name in ["h2", "h3"] and "Base Stats" not in current.text:
                break
            if current.name == "span" and current.get("class"):
                if any("stat-name" in c for c in current.get("class")):
                    stat_name = clean_text(current.text.replace(":", ""))
                    value_tag = current.find_next("span", class_=re.compile("stat-value"))
                    if value_tag:
                        stats.append(f"• {stat_name}: {clean_text(value_tag.text)}")
            current = current.find_next()

    skill_name = ""
    skill_desc = ""
    skill_title = soup.find("span", class_=re.compile("text-accent"))
    if skill_title:
        skill_name = clean_text(skill_title.text)
        skill_description = soup.find("span", class_=re.compile("unique-skill-description"))
        if skill_description:
            skill_desc = clean_text(skill_description.text)

    return {
        "name": item_name,
        "rarity": rarity,
        "description": description,
        "stats": stats,
        "skill_name": skill_name,
        "skill_desc": skill_desc,
        "url": url,
        "image": image_url,
    }


# ==========================
# SLASH COMMAND /item
# ==========================
@tree.command(name="item", description="Rechercher un item TLDB par nom")
@app_commands.describe(item_name="Commence à taper le nom de l'item...")
async def item_command(interaction: discord.Interaction, item_name: str):
    await interaction.response.defer()

    # item_name = l'ID de l'item quand sélectionné via autocomplete
    data = fetch_tldb_item(item_name)

    if not data:
        await interaction.followup.send(
            f"❌ Item introuvable : `{item_name}`\n"
            "💡 Utilise l'autocomplétion pour sélectionner un item dans la liste."
        )
        return

    embed = discord.Embed(
        title=data["name"],
        url=data["url"],
        color=discord.Color.blurple()
    )

    if data["image"]:
        embed.set_thumbnail(url=data["image"])

    embed.add_field(name="Rarity", value=data["rarity"], inline=True)

    if data["description"]:
        embed.add_field(name="Description", value=data["description"], inline=False)

    if data["stats"]:
        embed.add_field(name="⚔ Base Stats", value="\n".join(data["stats"]), inline=False)

    if data["skill_name"]:
        embed.add_field(
            name=f"✨ Unique Skill — {data['skill_name']}",
            value=data["skill_desc"] or "Pas de description",
            inline=False
        )

    embed.set_footer(text="Data from TLDB.info")
    await interaction.followup.send(embed=embed)


# ==========================
# AUTOCOMPLETE
# ==========================
@item_command.autocomplete("item_name")
async def item_autocomplete(
    interaction: discord.Interaction,
    current: str,
) -> list[app_commands.Choice[str]]:
    if len(current) < 2:
        return []

    loop = asyncio.get_event_loop()
    results = await loop.run_in_executor(None, search_items_local, current)

    return [
        app_commands.Choice(
            name=r["name"][:100],
            value=r["id"]
        )
        for r in results
    ]


# ==========================
# EVENTS
# ==========================
@client.event
async def on_ready():
    load_items_from_disk()

    try:
        synced = await tree.sync()
        print(f"Synced {len(synced)} command(s)")
    except Exception as e:
        print(e)

    print(f"Logged in as {client.user}")


if __name__ == "__main__":
    client.run(TOKEN)
