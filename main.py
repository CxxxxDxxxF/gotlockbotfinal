#!/usr/bin/env python3
"""
main.py

Orchestrates GotLockz bot startup and logs a ready message with timestamp.
"""
import os
import logging
from datetime import datetime
from bot import bot  # only import the bot instance

# Configure root logger (ensure format and level)
logging.basicConfig(
    format="[%(asctime)s] %(levelname)s:%(name)s: %(message)s",
    level=logging.INFO
)
logger = logging.getLogger()


def current_timestamp() -> str:
    """Return current UTC timestamp as a formatted string."""
    return datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S UTC")


def ready_message(user) -> str:
    """Return a ready message including the user's identifier and timestamp."""
    return f"\u2714 GotLockz bot logged in as {user} at {current_timestamp()}"

# Attach to the bot’s on_ready event to log/send ready message
@bot.event
async def on_ready_status():
    msg = ready_message(bot.user)
    logger.info(msg)
    # Optionally send this to a Discord status channel:
    # status_channel = bot.get_channel(YOUR_STATUS_CHANNEL_ID)
    # if status_channel:
    #     await status_channel.send(msg)


if __name__ == "__main__":
    token = os.getenv("DISCORD_TOKEN")
    if not token:
        logger.error("DISCORD_TOKEN environment variable not set.")
        raise RuntimeError("DISCORD_TOKEN must be set to run the bot.")
    bot.run(token)
