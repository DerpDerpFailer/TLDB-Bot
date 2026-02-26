import os
import requests
from bs4 import BeautifulSoup
import discord
from discord import app_commands
from flask import Flask
from threading import Thread

# ==============================
# CONFIG
# ==============================

TOKEN = os.getenv("DISCORD_TOKEN")

intents = discord.Intents.default()
bot = discord.Client(intents=intents)
tree = app_commands.CommandTree(bot)

# ==============================
# TLDB SCRAPER
# ==============================

def fetch_tldb_item(url: str):
    headers = {
        "User-Agent": "Mozilla/5.0"
    }

    try:
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()
    except requests.exceptions.RequestException as e:
        print(f"Request error: {e}")
        return None

    soup = BeautifulSoup(response.text, "lxml")

    # ======================
    # Item Name (REAL NAME)
    # ======================
    title_tag = soup.find("h1")
    if not title_tag:
        print("No <h1> found.")
        return None

    item_name = title_tag.text.strip()

    # ======================
    # Item Image
    # ======================
    image_tag = soup.find("meta", property="og:image")
    image_url = image_tag["content"] if image_tag else None

    # ======================
    # Description (optional)
    # ======================
    description = ""

    desc_block = soup.find("div", class_="description")
    if desc_block:
        description = desc_block.text.strip()

    # fallback if no description div
    if not description:
        meta_desc = soup.find("meta", property="og:description")
        if meta_desc:
            description = meta_desc["content"]

    return {
        "name": item_name,
        "image": image_url,
        "description": description,
        "url": url
    }

# ==============================
# DISCORD COMMAND
# ==============================

@tree.command(name="item", description="Get item info from a TLDB URL")
@app_commands.describe(url="Full TLDB item URL (https://tldb.info/db/item/...)")
async def item(interaction: discord.Interaction, url: str):

    await interaction.response.defer()

    if not url.startswith("https://tldb.info/db/item/"):
        await interaction.followup.send("❌ Please provide a valid TLDB item URL.")
        return

    data = fetch_tldb_item(url)

    if not data:
        await interaction.followup.send("❌ Could not fetch item data from TLDB.")
        return

    embed = discord.Embed(
        title=data["name"],
        url=data["url"],
        description=data["description"] or "No description available.",
        color=0x5865F2
    )

    if data["image"]:
        embed.set_thumbnail(url=data["image"])

    embed.set_footer(text="Data from TLDB.info")

    await interaction.followup.send(embed=embed)


@bot.event
async def on_ready():
    await tree.sync()
    print(f"Logged in as {bot.user}")

# ==============================
# FLASK (RENDER KEEP-ALIVE)
# ==============================

app = Flask(__name__)

@app.route("/")
def home():
    return "TLDB Item Bot is running!"

def run_discord():
    bot.run(TOKEN)

# ==============================
# MAIN
# ==============================

if __name__ == "__main__":
    Thread(target=run_discord).start()

    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)
