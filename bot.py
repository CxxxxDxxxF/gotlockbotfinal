#!/usr/bin/env python3
"""
Main entrypoint for GotLockz Discord Bot.
Provides slash commands for posting VIP/FREE picks based on bet slips.
"""

import os
import logging
import asyncio
from datetime import datetime
import discord
from discord import app_commands
from discord.ext import commands

from image_processing import extract_text_from_image, parse_bet_details
from ai_analysis import generate_analysis
# from sheets_integration import get_next_play_id, log_pick  # Uncomment when sheets_integration is ready

# ---- Logging Setup ----
logging.basicConfig(
    format="[%(asctime)s] %(levelname)s:%(name)s: %(message)s",
    level=logging.INFO
)
logger = logging.getLogger("gotlockz-bot")

# ---- Environment Variables ----
TOKEN = os.getenv("DISCORD_TOKEN")
GUILD_ID = os.getenv("GUILD_ID")

if not TOKEN or not GUILD_ID:
    logger.critical("DISCORD_TOKEN and GUILD_ID must be set in env variables.")
    raise SystemExit("Missing environment variables.")

try:
    GUILD_ID = int(GUILD_ID)
except ValueError:
    logger.critical("GUILD_ID must be an integer.")
    raise

# ---- Discord Bot Initialization ----
intents = discord.Intents.default()
intents.guilds = True
intents.messages = True
intents.message_content = True

bot = commands.Bot(command_prefix=commands.when_mentioned_or("/"), intents=intents)

# ---- Error Handlers ----
@bot.event
async def on_app_command_error(interaction: discord.Interaction, error: app_commands.AppCommandError):
    """Handle errors for slash commands."""
    logger.error(f"Error in command '{interaction.command.name}': {error}", exc_info=True)
    # Respond to user
    if interaction.response.is_done():
        await interaction.followup.send("❌ An unexpected error occurred. Please try again later.", ephemeral=True)
    else:
        await interaction.response.send_message("❌ An unexpected error occurred. Please try again later.", ephemeral=True)

# ---- Bot Events ----
@bot.event
async def on_ready():
    logger.info(f"✅ Logged in as {bot.user} (ID: {bot.user.id})")
    # Sync commands to guild first for faster updates during dev
    try:
        guild = discord.Object(id=GUILD_ID)
        await bot.tree.sync(guild=guild)
        logger.info(f"🔄 Synced slash commands to guild {GUILD_ID}")
    except Exception as e:
        logger.warning(f"Failed to sync to guild {GUILD_ID}: {e}")
        await bot.tree.sync()
        logger.info("🔄 Synced slash commands globally")

# ---- Utility Functions ----
async def async_save_attachment(attachment: discord.Attachment, local_path: str):
    try:
        await attachment.save(local_path)
        logger.debug(f"Saved attachment to {local_path}")
    except Exception:
        logger.exception("Failed to save attachment")
        raise


def cleanup_file(path: str):
    try:
        if os.path.exists(path):
            os.remove(path)
            logger.debug(f"Deleted temp file: {path}")
    except Exception:
        logger.warning(f"Failed to delete temp file: {path}")


def generate_vip_message(play_number: int, date_str: str, game: str, bet: str, odds: str, units: float, analysis: str) -> str:
    return (
        f"🔒 **VIP PLAY #{play_number}** 🏆 - {date_str}\n"
        f"⚾ **Game:** {game}\n"
        f"🏆 **Bet:** {bet} (Odds: {odds})\n"
        f"💰 **Units:** {units}\n\n"
        f"👇 **Analysis:**\n{analysis}"
    )

# ---- Slash Commands ----
@bot.tree.command(name="postpick", description="Post a VIP pick to the specified channel.")
@app_commands.describe(
    units="How many units are you staking?",
    channel="Channel where the pick should be posted",
    image="Bet slip image file"
)
async def postpick(interaction: discord.Interaction, units: float, channel: discord.TextChannel, image: discord.Attachment):
    await interaction.response.defer(ephemeral=True)
    # Validate units
    if units <= 0:
        await interaction.followup.send("❌ Units must be greater than zero.", ephemeral=True)
        return

    temp_path = f"tmp/{image.filename}"
    try:
        # Save attachment
        await async_save_attachment(image, temp_path)

        # OCR extraction
        try:
            ocr_text = extract_text_from_image(temp_path)
            logger.info(f"OCR text: {ocr_text}")
        except Exception as e:
            logger.exception("OCR extraction failed")
            await interaction.followup.send(f"❌ Failed to process image: {e}", ephemeral=True)
            return

        # Parse bet details
        bet_details = parse_bet_details(ocr_text)
        if not bet_details:
            await interaction.followup.send("❌ Could not parse bet slip. Use `/analyze_bet` to debug.", ephemeral=True)
            return

        # Generate analysis
        try:
            analysis = await generate_analysis(bet_details)
        except Exception as e:
            logger.exception("Analysis generation failed")
            analysis = "Failed to generate analysis."

        # Determine play number
        # play_number = get_next_play_id()  # From sheets_integration
        play_number = 1  # TODO: replace with dynamic counter

        # Format message
        date_str = datetime.utcnow().strftime("%m/%d/%y")
        message_content = generate_vip_message(
            play_number,
            date_str,
            bet_details.get("game", "Unknown"),
            bet_details.get("bet", "Unknown"),
            bet_details.get("odds", "N/A"),
            units,
            analysis
        )
        # Send to target channel
        await channel.send(message_content)

        # Log pick to sheet (optional)
        # log_pick(play_number, date_str, bet_details, units)

        await interaction.followup.send("✅ VIP pick posted successfully.", ephemeral=True)
    finally:
        cleanup_file(temp_path)


@bot.tree.command(name="analyze_bet", description="Analyze a bet slip image and return analysis.")
@app_commands.describe(image="Bet slip image file")
async def analyze_bet(interaction: discord.Interaction, image: discord.Attachment):
    await interaction.response.defer(ephemeral=True)
    temp_path = f"tmp/{image.filename}"
    result = ""
    try:
        await async_save_attachment(image, temp_path)
        try:
            ocr_text = extract_text_from_image(temp_path)
            bet_details = parse_bet_details(ocr_text)
            if not bet_details:
                result = "❌ Could not extract details."
            else:
                result = await generate_analysis(bet_details)
        except Exception as e:
            logger.exception("Bet analysis failed")
            result = f"❌ Error: {e}"
    finally:
        cleanup_file(temp_path)

    await interaction.followup.send(result, ephemeral=True)

# ---- Bot Execution ----
def main():
    # Ensure tmp directory exists
    os.makedirs("tmp", exist_ok=True)
    bot.run(TOKEN)

if __name__ == "__main__":
    main()
