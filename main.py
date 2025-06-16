#!/usr/bin/env python3
"""
main.py

Orchestrates GotLockz bot startup and logs a ready message with timestamp.
"""
import logging
from datetime import datetime
from bot import run_bot, bot

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
    # Log to console
    logger.info(msg)
    # Optionally send this message into a designated Discord channel:
    # status_channel = bot.get_channel(YOUR_STATUS_CHANNEL_ID)
    # if status_channel:
    #     await status_channel.send(msg)


if __name__ == "__main__":
    run_bot()
