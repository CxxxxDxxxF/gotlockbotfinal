# main.py

#!/usr/bin/env python3
"""
main.py

Launches GotLockz bot and logs a ready message.
"""
import os
import logging
from datetime import datetime
from dotenv import load_dotenv

# ensure .env is loaded
load_dotenv()

# configure logging
logging.basicConfig(
    format="[%(asctime)s] %(levelname)s:%(name)s: %(message)s",
    level=logging.INFO
)
logger = logging.getLogger()

from bot import bot, GUILD_ID  # our configured Bot instance

def current_timestamp() -> str:
    return datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S UTC")

@bot.event
async def on_ready_status():
    msg = f"✔️ GotLockz bot is live in guild {GUILD_ID} at {current_timestamp()}"
    logger.info(msg)

if __name__ == "__main__":
    token = os.getenv("DISCORD_TOKEN")
    if not token:
        logger.error("DISCORD_TOKEN not set.")
        raise RuntimeError("Missing DISCORD_TOKEN")
    bot.run(token)

