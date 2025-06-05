from datetime import datetime
import discord


def format_moneyline(ml: int) -> str:
    return f"{ml:+d}"


def implied_prob_from_ml(ml: int) -> float:
    if ml < 0:
        return abs(ml) / (abs(ml) + 100)
    return 100 / (ml + 100)


def format_date(dt: datetime) -> str:
    return dt.strftime("%Y-%m-%d")


def make_styled_embed(title: str, color: int = 0x3498db) -> discord.Embed:
    embed = discord.Embed(title=title, color=color, timestamp=datetime.utcnow())
    embed.set_footer(text="GotLockBot Final • Powered by OpenAI & API-Sports")
    return embed
