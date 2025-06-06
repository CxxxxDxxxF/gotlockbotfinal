"""Main entry point for the GotLockz bot."""

from __future__ import annotations

import logging
import sys
import datetime

import discord
from bot import run_bot


def current_timestamp() -> str:
    """Return the current UTC timestamp as a string."""
    return (
        datetime.datetime.now(datetime.timezone.utc)
        .strftime("%Y-%m-%d %H:%M:%S UTC")
    )


def ready_message(user: discord.ClientUser | None) -> str:
    """Format the ready log message with a timestamp."""
    return (
        "\u2714\ufe0f GotLockz bot logged in as "
        f"{user} at {current_timestamp()}"
    )


def main() -> None:
    """Configure logging, read the token, and run the bot."""
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s %(levelname)s: %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )
    logging.info("GotLockz bot starting...")

    try:
        run_bot()
    except Exception as exc:  # pragma: no cover - runtime failure
        logging.error("\u274c Login failed: %s", exc)
        sys.exit(1)


if __name__ == "__main__":
    main()
