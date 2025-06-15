
# bot.py

import os
import re
import asyncio
import discord
from discord import app_commands
from discord.ext import commands
from datetime import datetime
from image_processing import extract_text_from_image, parse_bet_details
from ai_analysis import generate_analysis

# Read environment variables
TOKEN = os.getenv("DISCORD_TOKEN", "dummy")
GUILD_ID = int(os.getenv("GUILD_ID", "8"))

# Intents
intents = discord.Intents.default()
intents.guilds = True
intents.messages = True
intents.message_content = True

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
    await interaction.response.defer(ephemeral=True)

    # STEP 1: Save image in Render-safe temp directory
    local_path = f"/tmp/{image.filename}"
    await image.save(local_path)

    # STEP 2: OCR the image
    text = extract_text_from_image(local_path)

    if os.path.exists(local_path):
        os.remove(local_path)

    print(f"🧾 Extracted OCR Text:\n{text}")

   # STEP 3:  OCR text into structured bet details
    details = parse_bet_details(text)

    if not details:
        await interaction.followup.send("❌ Couldn't parse the bet slip. Try /analyze_bet to debug.", ephemeral=True)
        return

    play_number = 7  # 🔜 We’ll automate this later
    date_str = datetime.utcnow().strftime("%-m/%-d/%y")
    analysis = await generate_analysis(details)

    game = details["game"]
    bet = details["bet"]
    odds = details["odds"]

    # Format message using VIP template
    message = format_vip_post(play_number, date_str, game, bet, odds, units, analysis)

    # STEP 4: Send formatted message to channel
    await channel.send(message)

    await interaction.followup.send("✅ VIP pick posted successfully.", ephemeral=True)

@bot.tree.command(
    name="analyze_bet",
    description="Analyze a bet slip image."
)
@app_commands.describe(
    image="Bet slip image to analyze",
)
async def analyze_bet(interaction: discord.Interaction, image: discord.Attachment):
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

# 💬 FORMATTER FUNCTION
def format_vip_post(play_number, date_str, game, bet, odds, units, analysis):
    return f"""🔒 I VIP PLAY #{play_number} 🏆 - {date_str}  
⚾ | Game: {game}  
🏆 | {bet} ({odds})  
💰 | Unit Size: {units}  

👇 | Analysis Below:  
{analysis}"""

def run_bot() -> None:
    bot.run(TOKEN)

if __name__ == "__main__":
    run_bot()
