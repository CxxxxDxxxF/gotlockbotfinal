"""Main entry point for the GotLockz bot."""

from __future__ import annotations

import logging
import os
import sys
import datetime

import discord


def current_timestamp() -> str:
    """Return the current UTC timestamp as a string."""
    return datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC")


def ready_message(user: discord.ClientUser | None) -> str:
    """Format the ready log message with a timestamp."""
    return f"\u2714\ufe0f GotLockz bot logged in as {user} at {current_timestamp()}"

intents = discord.Intents.default()
intents.guilds = True
intents.messages = True
intents.message_content = True

client = discord.Client(intents=intents)


@client.event
async def on_ready() -> None:  # pragma: no cover - simple log
    """Log when the bot is ready."""
    logging.info(ready_message(client.user))


def main() -> None:
    """Configure logging, read the token, and run the bot."""
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s %(levelname)s: %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )
    logging.info("GotLockz bot starting...")

    token = os.getenv("DISCORD_TOKEN")
    if not token:
        logging.error("\u274c ERROR: DISCORD_TOKEN not found")
        sys.exit(1)

    try:
        client.run(token)
    except Exception as exc:  # pragma: no cover - runtime failure
        logging.error("\u274c Login failed: %s", exc)
        sys.exit(1)


if __name__ == "__main__":
    main()
