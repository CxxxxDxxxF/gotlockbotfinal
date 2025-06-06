# bot.py

import os
import logging
import discord
from discord.ext import commands

from commands import register_commands
from tasks import create_log_guild_count_task

# Basic logging
logging.basicConfig(level=logging.INFO)
log = logging.getLogger("gotlockz")

# Read token and guild from environment
DISCORD_TOKEN = os.getenv("DISCORD_TOKEN")
# Make sure GUILD_ID is set in Render’s Environment Variables page as an integer (e.g. “123456789012345678”)
GUILD_ID = int(os.getenv("GUILD_ID", "0"))

# Create intents – we only need default intents for slash commands
intents = discord.Intents.default()
bot = commands.Bot(command_prefix="!", intents=intents)

# Set up a Tree for application commands
tree = bot.tree

# Create background tasks
log_guild_count = create_log_guild_count_task(bot)

# Register commands immediately so tests can inspect them
postpick_command = register_commands(tree, GUILD_ID)

@bot.event
async def on_ready():
    log.info(f"GotLockz bot logged in as {bot.user} (ID: {bot.user.id})")
    log.info(f"Registering slash commands to guild {GUILD_ID}…")

    # Register/apply slash commands to the single GUILD_ID so they show up instantly
    guild = discord.Object(id=GUILD_ID)
    tree.copy_global_to(guild=guild)
    await tree.sync(guild=guild)

    log.info("Slash commands synced.")

    if not log_guild_count.is_running():
        log_guild_count.start()

def run_bot() -> None:
    """Run the Discord bot after validating configuration."""
    if DISCORD_TOKEN is None or GUILD_ID == 0:
        raise RuntimeError("DISCORD_TOKEN or GUILD_ID not set in environment")
    bot.run(DISCORD_TOKEN)

# —————————————————————————————————————————————
# Run the bot
# —————————————————————————————————————————————

if __name__ == "__main__":
    try:
        run_bot()
    except Exception as exc:  # pragma: no cover - runtime failure
        log.error("Bot failed to start: %s", exc)
        raise
