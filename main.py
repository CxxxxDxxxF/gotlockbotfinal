"""Main entry point for the GotLockz bot."""

from __future__ import annotations

import logging
import os
import sys
import datetime

import discord
from discord import app_commands


def current_timestamp() -> str:
    """Return the current UTC timestamp as a string."""
    return datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC")


def ready_message(user: discord.ClientUser | None) -> str:
    """Format the ready log message with a timestamp."""
    return f"\u2714\ufe0f GotLockz bot logged in as {user} at {current_timestamp()}"

intents = discord.Intents.default()
intents.guilds = True
intents.guild_messages = True
intents.message_content = True


class GotLockzBot(discord.Client):
    """Discord client handling slash commands."""

    def __init__(self, *, intents: discord.Intents) -> None:
        super().__init__(intents=intents)
        self.tree = app_commands.CommandTree(self)

    async def setup_hook(self) -> None:
        """Sync commands to the configured guild."""
        guild_id = int(os.getenv("GUILD_ID", "0"))
        if guild_id:
            guild_obj = discord.Object(id=guild_id)
            self.tree.copy_global_to(guild=guild_obj)
            await self.tree.sync(guild=guild_obj)
            logging.info("\u2705  Synchronized slash commands to guild %s.", guild_id)

    async def on_ready(self) -> None:  # pragma: no cover - simple log
        logging.info(ready_message(self.user))


bot = GotLockzBot(intents=intents)


@bot.tree.command(name="postpick", description="Register a pick and post it to your chosen channel.")
@app_commands.describe(
    units="How many units (e.g. 1.5, 2.0).",
    channel="The target channel name (e.g. free-plays or join-vip).",
)
async def postpick(interaction: discord.Interaction, units: float, channel: str) -> None:
    """Handle the /postpick slash command."""
    await interaction.response.defer()
    response_text = (
        f"Your pick has been received!\n"
        f"\u2022 Units: {units}\n"
        f"\u2022 Target Channel: #{channel}\n\n"
        "(Replace this block with your OCR + stats + formatting logic.)"
    )
    await interaction.followup.send(response_text)


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
        bot.run(token)
    except Exception as exc:  # pragma: no cover - runtime failure
        logging.error("\u274c Login failed: %s", exc)
        sys.exit(1)


if __name__ == "__main__":
    main()
