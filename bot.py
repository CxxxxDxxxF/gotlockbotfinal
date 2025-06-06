# bot.py

import os

import discord
from discord.ext import commands
from dotenv import load_dotenv

from gotlockz_bot import setup_bot
from gotlockz_bot.utils import setup_logging

load_dotenv()
TOKEN = os.getenv("DISCORD_TOKEN", "no-token-set")

setup_logging()

intents = discord.Intents.default()
intents.message_content = True

bot = commands.Bot(command_prefix='/', intents=intents)
setup_bot(bot)


@bot.event
async def on_ready():
    print(f"Logged in as {bot.user} (ID: {bot.user.id})")


if __name__ == "__main__":
    if TOKEN == "no-token-set":
        print("⚠️ DISCORD_TOKEN is not set. Exiting.")
    else:
        bot.run(TOKEN)
