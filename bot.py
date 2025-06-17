#!/usr/bin/env python3
"""
bot.py

Defines the GotLockz Discord bot with:
- /postpick → multi-channel VIP, lotto, free
- /analyze  → custom analysis in #analysis
- auto command sync + ready log
"""
import os
import json
import logging
import discord
import statsapi                 # ← your MLB stats API
from discord import TextChannel
from discord.ext import commands
from discord import app_commands
from datetime import datetime
from zoneinfo import ZoneInfo

from dotenv import load_dotenv
from image_processing import extract_text_from_image, parse_bet_details
from ai_analysis      import generate_analysis

# ---- Load .env ----
load_dotenv()

# ---- Logging ----
logging.basicConfig(
    format="[%(asctime)s] %(levelname)s:%(name)s: %(message)s",
    level=logging.INFO
)
logger = logging.getLogger("gotlockz-bot")

# ---- Bot Setup ----
DISCORD_TOKEN       = os.getenv("DISCORD_TOKEN")
GUILD_ID            = int(os.getenv("GUILD_ID", 0))
ANALYSIS_CHANNEL_ID = int(os.getenv("ANALYSIS_CHANNEL_ID", 0))

if not DISCORD_TOKEN or not GUILD_ID:
    logger.error("DISCORD_TOKEN and GUILD_ID must be set.")
    raise RuntimeError("Missing required environment variables.")

intents = discord.Intents.default()
intents.guilds = True
intents.messages = True
intents.message_content = True

bot = commands.Bot(command_prefix="/", intents=intents)
tree = bot.tree

# ---- Persistent Counters ----
COUNTER_FILE = "counters.json"
try:
    with open(COUNTER_FILE) as f:
        COUNTERS = json.load(f)
except FileNotFoundError:
    COUNTERS = {"vip": 0, "lotto": 0, "free": 0}

# ---- Channel Configuration (by ID) ----
CHANNEL_CONFIG = {
    int(os.getenv("VIP_CHANNEL_ID", 0)):   "vip",
    int(os.getenv("LOTTO_CHANNEL_ID", 0)): "lotto",
    int(os.getenv("FREE_CHANNEL_ID", 0)):  "free",
}

# ---- Helpers ----
def lookup_game_time(away: str, home: str) -> datetime | None:
    today = datetime.now().date().isoformat()
    sched = statsapi.schedule(start_date=today, end_date=today)
    for day in sched.get("dates", []):
        for g in day.get("games", []):
            a = g["teams"]["away"]["team"]["name"]
            h = g["teams"]["home"]["team"]["name"]
            if a.lower() == away.lower() and h.lower() == home.lower():
                dt_utc = datetime.fromisoformat(
                    g["gameDate"].replace("Z", "+00:00")
                )
                return dt_utc.astimezone(ZoneInfo("America/New_York"))
    return None

def generate_vip_message(number: int, details: dict, units: float, analysis: str) -> str:
    away, home, odds = details["away"], details["home"], details["odds"]
    dt = lookup_game_time(away, home)
    if dt:
        date_str = dt.strftime("%-m/%-d/%y")
        full_time = dt.strftime("%-m/%-d/%y %-I:%M %p %Z")
    else:
        date_str, full_time = datetime.now().strftime("%-m/%-d/%y"), ""
    parts = [
        f"🔒 VIP PLAY #{number} 🏆 – {date_str}",
        f"⚾  **Game:** {away} @ {home}" + (f" ({full_time})" if full_time else ""),
        "",
        f"🏆  **Pick:** {details['bet']} ({odds})",
        f"💰  **Units:** {units}",
        "",
        "👇  **Analysis:**",
        analysis
    ]
    return "\n".join(parts)

def generate_generic_message(number: int, details: dict, units: float, analysis: str, kind: str) -> str:
    header_emoji, header_title = {
        "lotto": ("🎲", "LOTTO PLAY"),
        "free":  ("🆓", "FREE PLAY"),
    }[kind]
    lines = [
        f"{header_emoji} {header_title} #{number} – {datetime.now().strftime('%-m/%-d/%y')}",
        f"Bet: {details['bet']} ({details['odds']})",
        f"Units: {units}",
        "",
        "Analysis:",
        analysis
    ]
    return "\n".join(lines)

# ---- Bot Events ----
@bot.event
async def on_ready():
    logger.info(f"✅ Logged in as {bot.user} (ID: {bot.user.id})")
    guild = discord.Object(id=GUILD_ID)
    tree.clear_commands(guild=guild)
    await tree.sync(guild=guild)
    logger.info(f"🔄 Synced slash commands to guild {GUILD_ID}")

# ---- /postpick Command ----
@tree.command(
    name="postpick",
    description="Upload a bet slip & post to VIP, Lotto, or Free channels"
)
@app_commands.describe(
    units="How many units?",
    channel="Where to post the pick",
    image="Attach your bet slip image"
)
async def postpick(
    interaction: discord.Interaction,
    units: float,
    channel: TextChannel,
    image: discord.Attachment
):
    # 1) ACK immediately
    await interaction.response.defer(ephemeral=True)

    # 2) Validate
    kind = CHANNEL_CONFIG.get(channel.id)
    if not kind:
        return await interaction.followup.send(
            "❌ I can only post to VIP, Lotto, or Free channels.",
            ephemeral=True
        )
    if units <= 0:
        return await interaction.followup.send(
            "❌ Units must be greater than zero.",
            ephemeral=True
        )

    # 3) OCR & parse
    try:
        raw = await image.read()
        text = extract_text_from_image(raw)
        details = parse_bet_details(text)
        if not details:
            return await interaction.followup.send(
                "❌ Couldn't parse the bet slip. Try /analyze to debug.",
                ephemeral=True
            )
    except Exception as e:
        logger.exception("OCR/parsing failed")
        return await interaction.followup.send(
            f"❌ Failed processing image: {e}",
            ephemeral=True
        )

    # 4) AI analysis
    details["units"] = units
    try:
        analysis = generate_analysis(details)
    except Exception:
        logger.exception("AI analysis failed")
        analysis = "⚠️ Analysis failed."

    # 5) Persist counter
    COUNTERS[kind] += 1
    with open(COUNTER_FILE, "w") as f:
        json.dump(COUNTERS, f)

    # 6) Build & post
    if kind == "vip":
        msg = generate_vip_message(COUNTERS[kind], details, units, analysis)
    else:
        msg = generate_generic_message(
            COUNTERS[kind], details, units, analysis, kind
        )
    await channel.send(msg)

    # 7) Ephemeral confirmation
    await interaction.followup.send(
        f"✅ Your pick has been posted to {channel.mention}.",
        ephemeral=True
    )


# ---- /analyze Command ----
@tree.command(
    name="analyze",
    description="Run a custom AI analysis in the analysis channel"
)
@app_commands.describe(
    teams="Matchup (e.g. NY Yankees @ BOS Red Sox)",
    bet="Type of bet (Moneyline, O/U 6.5, etc.)",
    model="Model approach (value, power, contrarian…)",
    tone="Tone (hype, dry-stats, etc.)"
)
async def analyze(
    interaction: discord.Interaction,
    teams: str,
    bet: str,
    model: str = "default",
    tone: str = "hype"
):
    if interaction.channel_id != ANALYSIS_CHANNEL_ID:
        return await interaction.response.send_message(
            "❌ Use this only in the designated analysis channel.",
            ephemeral=True
        )

    await interaction.response.defer(ephemeral=True)
    details = {
        "player": teams if "@" not in teams else None,
        "away":  None if "@" not in teams else teams.split("@")[0].strip(),
        "home":  None if "@" not in teams else teams.split("@")[1].strip(),
        "bet":   bet,
        "odds":  "",
        "units": ""
    }
    analysis = generate_analysis(details, model=model, temperature=0.8)
    embed = discord.Embed(
        title=f"Analysis [{model.title()} | {tone.title()}]",
        description=analysis,
        color=discord.Color.blurple()
    )
    embed.add_field(name="Matchup", value=teams, inline=True)
    embed.add_field(name="Bet", value=bet, inline=True)
    await interaction.followup.send(embed=embed)

# (no __main__ here—startup handled in main.py)
