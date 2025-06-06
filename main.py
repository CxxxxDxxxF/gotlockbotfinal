"""Main entry point for the GotLockz bot."""

from __future__ import annotations

import logging
import os
import sys

import discord


intents = discord.Intents.default()
intents.guilds = True
intents.messages = True
intents.message_content = True

client = discord.Client(intents=intents)


@client.event
async def on_ready() -> None:  # pragma: no cover - simple log
    """Log when the bot is ready."""
    logging.info("\u2714\ufe0f GotLockz bot logged in as %s", client.user)


def main() -> None:
    """Configure logging, read the token, and run the bot."""
    logging.basicConfig(level=logging.INFO)
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
