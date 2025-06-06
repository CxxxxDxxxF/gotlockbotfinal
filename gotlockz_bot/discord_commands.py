from discord.ext import commands
import asyncio
from .gpt_analyzer import analyze_text
from .mlb_client import get_today_games

class BasicCommands(commands.Cog):
    """Collection of simple bot commands."""

    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @commands.command()
    async def ping(self, ctx: commands.Context):
        """Respond with pong."""
        await ctx.send("Pong!")

    @commands.command()
    async def analyze(self, ctx: commands.Context, *, text: str):
        """Analyze text using GPT and return the result."""
        result = await asyncio.to_thread(analyze_text, text)
        await ctx.send(result)

    @commands.command()
    async def games(self, ctx: commands.Context):
        """Show today's MLB games."""
        games = await asyncio.to_thread(get_today_games)
        if games:
            await ctx.send("\n".join(games))
        else:
            await ctx.send("No games found today.")


def setup_bot(bot: commands.Bot):
    """Register the commands with the bot."""
    bot.add_cog(BasicCommands(bot))
