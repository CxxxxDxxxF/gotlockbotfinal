import discord
from discord.ext import commands
from dotenv import load_dotenv
import os
import logging

load_dotenv()
DISCORD_TOKEN = os.getenv("DISCORD_TOKEN")

intents = discord.Intents.default()
intents.message_content = True

bot = commands.Bot(command_prefix='/', intents=intents)
logging.basicConfig(level=logging.INFO)

# Import commands/modules
from gotlockz_bot.discord_commands import postpick, help_cmd
from gotlockz_bot.research_module import research
from gotlockz_bot.linewatch_module import watchline, linewatch_loop
from gotlockz_bot.valuebets_module import valuebets
from gotlockz_bot.portfolio_module import myportfolio

bot.add_command(postpick)
bot.add_command(research)
bot.add_command(watchline)
bot.add_command(valuebets)
bot.add_command(myportfolio)
bot.add_command(help_cmd)

@bot.event
async def on_ready():
    print(f"Logged in as {bot.user}")
    bot.loop.create_task(linewatch_loop(bot))

if __name__ == '__main__':
    bot.run(DISCORD_TOKEN)
