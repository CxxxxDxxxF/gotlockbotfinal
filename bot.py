# bot.py

import discord
from discord.ext import commands
import os
from dotenv import load_dotenv

load_dotenv()
TOKEN = os.getenv("DISCORD_TOKEN", "no-token-set")

intents = discord.Intents.default()
intents.message_content = True

bot = commands.Bot(command_prefix='/', intents=intents)

@bot.event
async def on_ready():
    print(f"Logged in as {bot.user} (ID: {bot.user.id})")

if __name__ == "__main__":
    if TOKEN == "no-token-set":
        print("⚠️ DISCORD_TOKEN is not set. Exiting.")
    else:
        bot.run(TOKEN)
