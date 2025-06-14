import os

# Telegram Bot Token
BOT_TOKEN = os.environ.get("BOT_TOKEN", "7342216134:AAEb7ZadpG0TOoxblgkOCZHUU5tHZ5JJI40")

# SQLite3 DB file
DB_PATH = os.environ.get("DB_PATH", "yt_exchange.db")

# Admin user id(s) for reports (comma-separated or list)
ADMIN_IDS = [int(x) for x in os.environ.get("ADMIN_IDS", "5718213826").split(",") if x]