# bot.py

import os
import logging
import discord
from discord import app_commands
from discord.ext import commands

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

@bot.event
async def on_ready():
    log.info(f"GotLockz bot logged in as {bot.user} (ID: {bot.user.id})")
    log.info(f"Registering slash commands to guild {GUILD_ID}…")

    # Register/apply slash commands to the single GUILD_ID so they show up instantly
    guild = discord.Object(id=GUILD_ID)
    tree.copy_global_to(guild=guild)
    await tree.sync(guild=guild)

    log.info("Slash commands synced.")

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
    analysis="Write-up to accompany the pick",
    channel="Which channel to post the pick in"
)
async def postpick(
    interaction: discord.Interaction,
    units: float,
    analysis: str,
    channel: discord.TextChannel,
):
    """
    /postpick handler: confirm the pick and post it into the specified channel.
    Sends the analysis text and embed together so they appear in one message.
    """
    # Acknowledge immediately (defer) so the user does not see an “application did not respond” error.
    await interaction.response.defer(ephemeral=True)

    # Build a nice embed summarizing the pick.
    embed = discord.Embed(
        title="📣 New Pick Posted!",
        description=f"**Units:** {units}\n**Picked by:** {interaction.user.mention}"
    )
    embed.set_footer(text="Good luck! 🍀")

    # Send both the analysis text and the embed in a single message.
    await channel.send(content=analysis, embed=embed)

    # Finally, send a follow-up to the original user confirming it was posted.
    await interaction.followup.send(
        f"✅ Your pick of **{units} units** has been posted in {channel.mention}.",
        ephemeral=True
    )

# —————————————————————————————————————————————
# Run the bot
# —————————————————————————————————————————————

def run_bot() -> None:
    """Run the Discord bot after validating environment variables."""
    if DISCORD_TOKEN is None or GUILD_ID == 0:
        log.error("DISCORD_TOKEN or GUILD_ID not set in environment!")
        return

    bot.run(DISCORD_TOKEN)


if __name__ == "__main__":
    run_bot()
