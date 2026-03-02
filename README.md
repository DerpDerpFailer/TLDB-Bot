# TLDB Item Bot (Discord)

A simple Discord bot written in **Python** that allows you to search for **Throne and Liberty items** from **Questlog.gg** and display them in a clean Discord embed.

The bot performs a **light HTML search** on Questlog.gg each time a command is used.
No database, no cache, no mass scraping.

---

## ✨ Features

- Slash command: `/item <item_name>`
- Searches Questlog.gg by item name (approximate match)
- Retrieves:
  - Item name
  - Item icon
  - Item description (when available)
  - Direct link to the item
- Displays a clean Discord embed
- No database
- No local cache
- 100% Python
- Free hosting compatible (Render, Fly.io, etc.)

---

## 📦 Tech Stack

- **Python 3.10+**
- **discord.py** (Slash Commands)
- **requests**
- **BeautifulSoup4**
- **lxml**

---

## 📁 Project Structure

```
project/
├── bot.py
├── requirements.txt
└── README.md
```

---

## 🤖 Discord Command

```
/item <item_name>
```

### Example
```
/item wand
```

If no item is found, the bot replies with a clear error message.

---

## 🔧 Installation (Local Test)

### 1. Clone the repository
```bash
git clone https://github.com/your-username/questlog-item-bot.git
cd questlog-item-bot
```

### 2. Install dependencies
```bash
pip install -r requirements.txt
```

### 3. Set the Discord token
Linux / macOS:
```bash
export DISCORD_TOKEN=YOUR_DISCORD_BOT_TOKEN
```

Windows (PowerShell):
```powershell
setx DISCORD_TOKEN "YOUR_DISCORD_BOT_TOKEN"
```

### 4. Run the bot
```bash
python bot.py
```

---

## 🔑 Creating the Discord Bot

1. Go to: https://discord.com/developers/applications
2. Create a new application
3. Add a bot
4. Copy the **Bot Token**
5. Enable the following permissions:
   - Send Messages
   - Embed Links
   - Use Application Commands
6. Invite the bot to your server with:
   - `bot`
   - `applications.commands`

---

## ☁️ Free Hosting (Render)

This bot can be hosted for free on **Render.com**.

### Steps:
1. Create a Render account
2. Create a **New Web Service**
3. Connect your GitHub repository
4. Set:
   - **Build Command**
     ```bash
     pip install -r requirements.txt
     ```
   - **Start Command**
     ```bash
     python bot.py
     ```
5. Add environment variable:
   - `DISCORD_TOKEN = your bot token`
6. Deploy

⚠️ Note: On the free plan, the service may sleep when inactive.

---

## ⚠️ Limitations

- No official Questlog.gg API is used
- Scraping relies on Questlog.gg HTML structure
- If the website changes, the bot may need updates
- Free hosting may cause short wake-up delays

---

## 🛠 Common Issues

### Slash command does not appear
- Bot not invited with `applications.commands`

### Bot is online but not responding
- Invalid token
- Missing environment variable

### Item not found
- Item name too vague or incorrect

---

## 🔄 Updating the Bot

1. Modify `bot.py`
2. Commit and push to GitHub
3. Render redeploys automatically

---

## 📜 Disclaimer

This project is **not affiliated with Questlog.gg**.
Data is fetched respectfully and on-demand.

---

## 🧩 Possible Improvements

- Multiple result selection
- Pagination
- Cache system
- Language support (FR)
- Richer embeds (rarity, stats, etc.)

---

## ❤️ Credits

- Data source: https://questlog.gg
- Built for the Throne and Liberty community

Enjoy 🚀
