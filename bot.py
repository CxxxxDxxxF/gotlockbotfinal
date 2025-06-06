# bot.py

import os
import re
import discord
from discord import app_commands
from discord.ext import commands
from datetime import datetime

# Import your helper functions (make sure these files exist in your repo)
from ocr_utils import run_ocr_on_image
from mlb_utils import get_game_start_time
from ai_utils import generate_analysis

# Read environment variables
TOKEN    = os.getenv("DISCORD_TOKEN")
GUILD_ID = os.getenv("GUILD_ID")

if not TOKEN or not GUILD_ID:
    raise RuntimeError("DISCORD_TOKEN or GUILD_ID not set in environment")

# Intents and bot setup
intents = discord.Intents.default()
bot = commands.Bot(command_prefix="/", intents=intents)


@bot.event
async def on_ready():
    print(f"✅ Logged in as {bot.user} (ID: {bot.user.id})")
    # Sync slash commands to the specified guild so that /postpick appears quickly.
    guild = discord.Object(id=int(GUILD_ID))
    await bot.tree.sync(guild=guild)
    print("✅ Synchronized slash commands.")


@bot.tree.command(
    name="postpick",
    description="Upload a bet slip image and post the VIP pick with AI analysis."
)
@app_commands.describe(
    image="Attach the bet‐slip image file here",
    units="How many units are you staking?"
)
async def postpick(interaction: discord.Interaction, image: discord.Attachment, units: float):
    """
    /postpick handler:
    1) Download the attached image to /tmp
    2) Run OCR on it to extract 'Team A at Team B', odds, etc.
    3) Look up the game start time via MLB-StatsAPI
    4) Generate an AI analysis paragraph
    5) Build & send a single Embed + attach the original image
    6) Send a follow-up ephemeral message confirming success
    """

    # 1) Acknowledge immediately to avoid "The application did not respond"
    await interaction.response.defer(ephemeral=True)

    # 2) Download the image locally
    local_filename = f"/tmp/{image.filename}"
    try:
        await image.save(local_filename)
    except Exception as e:
        await interaction.followup.send(
            f"⚠️ Failed to download the attached image: {e}",
            ephemeral=True
        )
        return

    # 3) Run OCR on the downloaded image
    try:
        ocr_text = await run_ocr_on_image(local_filename)
    except Exception as e:
        await interaction.followup.send(
            f"⚠️ OCR processing failed: {e}",
            ephemeral=True
        )
        return

    # 4) Parse the OCR text for matchup, odds, etc.
    #    We’ll join all lines into one string to simplify regex searching.
    lines = ocr_text.splitlines()
    full_text = " ".join(lines)

    # 4a) Find "Team A at Team B"
    match = re.search(r"([A-Za-z\s]+)\s+at\s+([A-Za-z\s]+)", full_text, re.IGNORECASE)
    if not match:
        await interaction.followup.send(
            "⚠️ Could not detect a valid ‘Team A at Team B’ pattern in the uploaded image. "
            "Make sure your bet slip clearly shows something like ‘New York Mets at New York Yankees’.",
            ephemeral=True
        )
        return

    away_team = match.group(1).strip()
    home_team = match.group(2).strip()
    matchup_text = f"{away_team} @ {home_team}"

    # 4b) Extract odds (first occurrence of + or - followed by 2–3 digits)
    odds_match = re.search(r"([+-]\d{2,3})", full_text)
    odds_text = odds_match.group(1) if odds_match else "N/A"

    # 4c) Assume the game date is "today" (UTC). Format as YYYY-MM-DD.
    today_str = datetime.utcnow().strftime("%Y-%m-%d")

    # 5) Fetch the start time of today's matchup (e.g. "7:05 PM EST")
    try:
        start_time = await get_game_start_time(away_team, home_team, today_str)
        if not start_time:
            start_time = "N/A"
    except Exception as e:
        # If the MLB API fails, we’ll default to "N/A" but continue.
        print(f"⚠️ MLB API error: {e}")
        start_time = "N/A"

    # 6) Generate AI analysis via OpenAI
    analysis_prompt = (
        f"Write a concise, insightful baseball betting analysis for the matchup "
        f"{away_team} at {home_team} on {today_str} with odds {odds_text}. "
        f"Use recent team and player statistics to support the pick."
    )
    try:
        ai_paragraph = await generate_analysis(analysis_prompt)
        # If OpenAI returns an empty string or errors, fallback message:
        if not ai_paragraph:
            ai_paragraph = "N/A ― AI analysis unavailable."
    except Exception as e:
        print(f"⚠️ OpenAI error: {e}")
        ai_paragraph = "N/A ― AI analysis failed."


    # 7) Build a Discord Embed containing all extracted and generated data
    embed = discord.Embed(
        title=f"📣 VIP Pick – {today_str}",
        description=f"Matchup: **{matchup_text}**\nOdds: **{odds_text}**\n"
    )
    embed.add_field(name="Start Time (EST)", value=start_time, inline=True)
    embed.add_field(name="Units", value=str(units), inline=True)
    embed.add_field(name="Analysis", value=ai_paragraph, inline=False)
    embed.set_footer(text=f"Picked by {interaction.user.display_name} • Good luck! 🍀")

    # 8) Send the embed AND attach the original image in one message
    target_channel: discord.TextChannel = interaction.channel  # same channel where /postpick was invoked
    try:
        await target_channel.send(
            embed=embed,
            file=discord.File(local_filename)
        )
    except Exception as e:
        await interaction.followup.send(
            f"⚠️ Failed to post the pick to {target_channel.mention}: {e}",
            ephemeral=True
        )
        return

    # 9) Finally, confirm back to the user that their pick has been posted
    await interaction.followup.send(
        f"✅ Your VIP pick has been posted in {target_channel.mention}.",
        ephemeral=True
    )


if __name__ == "__main__":
    bot.run(TOKEN)
