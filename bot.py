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
import statsapi                 # ← changed here
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
    """
    Fetches today's schedule and returns the UTC→EST datetime
    for the game matching away/home. Returns None if not found.
    """
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


def generate_vip_message(
    number: int,
    details: dict,
    units: float,
    analysis: str
) -> str:
    """
    Builds the VIP pick post exactly as spec:
    🔒 VIP PLAY #X 🏆 – M/D/YY  
    ⚾  **Game:** Away @ Home (M/D/YY h:mm PM TZ)  

    🏆  **Pick:** Away – Moneyline (±ODDS)  
    💰  **Units:** X  

    👇  **Analysis:**  
    <analysis>
    """
    away = details["away"]
    home = details["home"]
    odds = details["odds"]

    dt = lookup_game_time(away, home)
    if dt:
        date_str = dt.strftime("%-m/%-d/%y")
        full_time = dt.strftime("%-m/%-d/%y %-I:%M %p %Z")
    else:
        # fallback to today
        date_str = datetime.now().strftime("%-m/%-d/%y")
        full_time = ""

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


def generate_generic_message(
    number: int,
    details: dict,
    units: float,
    analysis: str,
    kind: str
) -> str:
    """
    For lotto/free channels—adjust emojis & headings as desired.
    """
    header = {
        "lotto": ("🎲", "LOTTO PLAY"),
        "free":  ("🆓", "FREE PLAY"),
    }[kind]
    away = details.get("away", details.get("player",""))
    home = details.get("home", "")
    odds = details["odds"]

    lines = [
        f"{header[0]} {header[1]} #{number} – {datetime.now().strftime('%-m/%-d/%y')}",
        f"Bet: {details['bet']} ({odds})",
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

    # clear + sync commands to guild first
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
    await interaction.response.defer(ephemeral=True)

    cfg = CHANNEL_CONFIG.get(channel.id)
    if not cfg:
        await interaction.followup.send(
            "❌ I can only post to VIP, Lotto, or Free channels.",
            ephemeral=True
        )
        return

    # save & OCR
    raw = await image.read()
    try:
        text = extract_text_from_image(raw)
    except Exception as e:
        logger.error(f"OCR failure: {e}")
        return await interaction.followup.send(
            "❌ Failed to OCR the image.",
            ephemeral=True
        )

    details = parse_bet_details(text)
    if not details:
        return await interaction.followup.send(
            "❌ Couldn't parse bet details. Make sure the slip is clear.",
            ephemeral=True
        )

    # AI analysis (sync)
    details["units"] = units
    analysis = generate_analysis(details)

    # bump counter & format
    key, kind = cfg
    COUNTERS[key] += 1
    with open(COUNTER_FILE, "w") as f:
        json.dump(COUNTERS, f)

    if key == "vip":
        msg = generate_vip_message(COUNTERS[key], details, units, analysis)
    else:
        msg = generate_generic_message(COUNTERS[key], details, units, analysis, key)

    # post and confirm
    await channel.send(msg)
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
        "away": None if "@" not in teams else teams.split("@")[0].strip(),
        "home": None if "@" not in teams else teams.split("@")[1].strip(),
        "bet": bet,
        "odds": "",
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
