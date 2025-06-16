import os
import asyncio
import logging
from datetime import datetime

import discord
from discord import app_commands
from discord.ext import commands

from image_processing import extract_text_from_image, parse_bet_details
from ai_analysis import generate_analysis

# --- Logging Setup ---
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("gotlockz-bot")

# --- Environment Variables and Validation ---
DISCORD_TOKEN = os.getenv("DISCORD_TOKEN")
GUILD_ID = os.getenv("GUILD_ID")

if not DISCORD_TOKEN or not GUILD_ID:
    logger.error("Environment variables DISCORD_TOKEN and GUILD_ID must be set.")
    raise RuntimeError("DISCORD_TOKEN and GUILD_ID must be set in environment variables.")

try:
    GUILD_ID = int(GUILD_ID)
except ValueError:
    logger.error("GUILD_ID must be an integer.")
    raise

# --- Discord Intents & Bot Setup ---
intents = discord.Intents.default()
intents.guilds = True
intents.messages = True
intents.message_content = True

bot = commands.Bot(command_prefix="/", intents=intents)
tree = bot.tree

# --- Utility function for async file operations ---
async def async_save_attachment(attachment: discord.Attachment, local_path: str):
    try:
        await attachment.save(local_path)
    except Exception as e:
        logger.error(f"Failed to save attachment: {e}")
        raise

# --- Events ---
@bot.event
async def on_ready():
    logger.info(f"✅ Logged in as {bot.user} (ID: {bot.user.id})")
    try:
        guild = discord.Object(id=GUILD_ID)
        await tree.clear_commands(guild=guild)
        await tree.sync(guild=guild)
        logger.info(f"🔄 Synced slash commands to guild {GUILD_ID}")
    except Exception as e:
        logger.warning(f"⚠️ Guild sync failed: {e}")
        try:
            await tree.sync()
            logger.info("🔄 Synced slash commands globally.")
        except Exception as ge:
            logger.error(f"Global sync failed: {ge}")

# --- Slash Commands ---
@tree.command(
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

    if units <= 0:
        await interaction.followup.send(
            "❌ Units must be greater than zero.",
            ephemeral=True
        )
        return

    local_path = f"/tmp/{image.filename}"
    try:
        await async_save_attachment(image, local_path)

        # OCR
        try:
            text = extract_text_from_image(local_path)
            logger.info(f"🧾 Extracted OCR Text:\n{text}")
        except Exception as e:
            logger.error(f"OCR extraction failed: {e}")
            await interaction.followup.send(
                f"❌ Failed to process the image: {e}",
                ephemeral=True
            )
            return

        # Parse
        details = parse_bet_details(text)
        if not details:
            await interaction.followup.send(
                "❌ Couldn't parse the bet slip. Try /analyze_bet to debug.",
                ephemeral=True
            )
            return

        # AI analysis
        try:
            analysis = await generate_analysis(details)
        except Exception as e:
            logger.error(f"Analysis failed: {e}")
            analysis = "Analysis generation failed."

        # Build and send
        play_number = 1  # TODO: persist & increment
        date_str = datetime.utcnow().strftime("%-m/%-d/%y")
        message = generate_vip_message(
            play_number,
            date_str,
            details.get("game", "Unknown Game"),
            details.get("bet", "Unknown Bet"),
            details.get("odds", "N/A"),
            units,
            analysis
        )

        await channel.send(message)
        await interaction.followup.send(
            "✅ VIP pick posted successfully.",
            ephemeral=True
        )

    finally:
        # Clean up temp file
        if os.path.exists(local_path):
            os.remove(local_path)

@tree.command(
    name="analyze_bet",
    description="Analyze a bet slip image."
)
@app_commands.describe(
    image="Bet slip image to analyze"
)
async def analyze_bet(
    interaction: discord.Interaction,
    image: discord.Attachment
):
    await interaction.response.defer(ephemeral=True)
    local_path = f"/tmp/{image.filename}"
    try:
        await async_save_attachment(image, local_path)
        try:
            text = extract_text_from_image(local_path)
            details = parse_bet_details(text)
            if not details:
                result = "Could not extract details from the bet slip."
            else:
                result = await generate_analysis(details)
        except Exception as e:
            logger.error(f"Error analyzing bet slip: {e}")
            result = f"Error analyzing bet slip: {e}"
    finally:
        if os.path.exists(local_path):
            os.remove(local_path)

    await interaction.followup.send(result, ephemeral=True)

# --- Message Formatter ---
def generate_vip_message(
    play_number: int,
    date_str: str,
    game: str,
    bet: str,
    odds: str,
    units: float,
    analysis: str
) -> str:
    """
    Constructs the final VIP pick post in the required emoji-and-pipe format.
    """
    lines = [
        f"🔒 VIP PLAY #{play_number} 🏆 - {date_str}",
        f"⚾ | Game: {game}",
        f"🏆 | {bet} ({odds})",
        f"💵 | Unit Size: {units}",
        "",
        "👇 | Analysis Below:",
        analysis
    ]
    return "\n".join(lines)

# --- Entry Point for Local Dev ---
def run_bot():
    bot.run(DISCORD_TOKEN)
