# bot.py

import os
import logging
import discord
from discord import app_commands
from discord.ext import commands, tasks

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


@tasks.loop(minutes=30)
async def log_guild_count() -> None:
    """Log how many guilds the bot is connected to."""
    log.info("Currently connected to %d guild(s)", len(bot.guilds))

@bot.event
async def on_ready() -> None:
    log.info(f"GotLockz bot logged in as {bot.user} (ID: {bot.user.id})")
    log.info(f"Registering slash commands to guild {GUILD_ID}…")

    # Register/apply slash commands to the single GUILD_ID so they show up instantly
    guild = discord.Object(id=GUILD_ID)
    tree.copy_global_to(guild=guild)
    await tree.sync(guild=guild)

    log.info("Slash commands synced.")

    if not log_guild_count.is_running():
        log_guild_count.start()


# ———————————————————————————————————————————————
# Define the /postpick command on the tree
# —————————————————————————————————————————————

@tree.command(
    name="postpick",
    description="Register a pick and post it to your chosen channel",
    guild=discord.Object(id=GUILD_ID)
)
@app_commands.describe(
    units="How many units (e.g. 1.0) to wager on this pick",
    channel="Which channel to post the pick in"
)
async def postpick(interaction: discord.Interaction, units: float, channel: discord.TextChannel):
    """
    /postpick handler: confirm the pick and post it into the specified channel.
    """
    # Acknowledge immediately (defer) so the user does not see an “application did not respond” error.
    await interaction.response.defer(ephemeral=True)

    # Build a nice embed summarizing the pick.
    embed = discord.Embed(
        title="📣 New Pick Posted!",
        description=f"**Units:** {units}\n**Picked by:** {interaction.user.mention}"
    )
    embed.set_footer(text="Good luck! 🍀")

    # Send that embed to the target channel.
    await channel.send(embed=embed)

    # Finally, send a follow-up to the original user confirming it was posted.
    await interaction.followup.send(
        f"✅ Your pick of **{units} units** has been posted in {channel.mention}.",
        ephemeral=True
    )


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
