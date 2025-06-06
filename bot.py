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
    description="Register a pick and post it (with analysis) into your chosen channel",
    guild=discord.Object(id=GUILD_ID)
)
@app_commands.describe(
    units="How many units (e.g. 1.0) to wager on this pick",
    channel="Which channel to post the pick in",
    image_url="Public URL of your bet-slip image (e.g. Fanatics embed link)",
    analysis="Your analysis text (can be multiple sentences)"
)
async def postpick(
    interaction: discord.Interaction,
    units: float,
    channel: discord.TextChannel,
    image_url: str,
    analysis: str
):
    """
    /postpick handler: confirm the pick, embed the bet-slip image and analysis in one post,
    and send it to the specified channel.
    """
    # Acknowledge immediately (defer) so the user does not see an “application did not respond” error.
    await interaction.response.defer(ephemeral=True)

    # Build a single embed that contains the bet-slip image and the analysis
    embed = discord.Embed(
        title="📣 New Pick Posted! 📣",
        description=f"**Units:** {units}  \u2003•  Picked by {interaction.user.mention}",
        color=discord.Color.green(),
    )

    # Attach the bet-slip image
    embed.set_image(url=image_url)

    # Include the analysis text
    embed.add_field(name="\ud83d\udcdd Analysis", value=analysis, inline=False)

    embed.set_footer(text="Good luck! \ud83c\udf40")

    # Send that embed to the target channel.
    await channel.send(embed=embed)

    # Finally, send a follow-up to the original user confirming it was posted.
    await interaction.followup.send(
        f"✅ Your pick of **{units} units** has been posted in {channel.mention}.",
        ephemeral=True
    )

# —————————————————————————————————————————————
# Run the bot
# —————————————————————————————————————————————

if __name__ == "__main__":
    # Ensure environment variables exist:
    if DISCORD_TOKEN is None or GUILD_ID == 0:
        log.error("DISCORD_TOKEN or GUILD_ID not set in environment!")
        exit(1)

    bot.run(DISCORD_TOKEN)
