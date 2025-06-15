# bot.py

import os
import re
import asyncio
import discord
from discord import app_commands
from discord.ext import commands
from datetime import datetime

# Import helper functions from the local modules
from image_processing import extract_text_from_image, parse_bet_details
from ai_analysis import generate_analysis

# Read environment variables
TOKEN = os.getenv("DISCORD_TOKEN", "dummy")
GUILD_ID = int(os.getenv("GUILD_ID", "8"))

# Intents and bot setup
intents = discord.Intents.default()
intents.guilds = True
intents.messages = True
intents.message_content = True  # This is important if you analyze content in the future
bot = commands.Bot(command_prefix="/", intents=intents)
tree = bot.tree


@bot.event
async def on_ready():
    print(f"✅ Logged in as {bot.user} (ID: {bot.user.id})")
    try:
        guild = discord.Object(id=int(GUILD_ID))
        await bot.tree.sync(guild=guild)
        print(f"✅ Synced slash commands to guild {GUILD_ID}")
    except Exception as e:
        print(f"⚠️ Guild sync failed: {e}")
        await bot.tree.sync()
        print("✅ Synced slash commands globally.")

@bot.tree.command(
    name="postpick",
    description="Post a VIP pick to the specified channel."
)
@app_commands.describe(
    units="How many units are you staking?",
    channel="Channel where the pick should be posted",
    image="Upload a bet slip image"
)
async def postpick(
    interaction: discord.Interaction,
    units: float,
    channel: discord.TextChannel,
    image: discord.Attachment
):
    """Send a simple embed with the unit amount to the given channel."""

    await interaction.response.defer(ephemeral=True)

    embed = discord.Embed(
        title="\U0001F4E3 VIP Pick",
        description=f"Units: **{units}**",
        timestamp=datetime.utcnow(),
    )

    await channel.send(embed=embed)

    await interaction.followup.send(
        f"\u2705 Your VIP pick has been posted in {channel.mention}.",
        ephemeral=True,
    )

@bot.tree.command(
    name="analyze_bet",
    description="Analyze a bet slip image."
)
@app_commands.describe(
    image="Bet slip image to analyze",
)
async def analyze_bet(interaction: discord.Interaction, image: discord.Attachment):
    """Run OCR on the uploaded image and respond with analysis."""

    await interaction.response.defer(ephemeral=True)

    local_path = f"/tmp/{image.filename}"
    try:
        await image.save(local_path)
        text = extract_text_from_image(local_path)
        details = parse_bet_details(text)
        analysis = generate_analysis(details)
        if asyncio.iscoroutine(analysis):
            analysis = await analysis
    finally:
        if os.path.exists(local_path):
            os.remove(local_path)

    await interaction.followup.send(analysis, ephemeral=True)


def run_bot() -> None:
    """Entry point used by main.py to start the bot."""
    bot.run(TOKEN)


if __name__ == "__main__":
    run_bot()
