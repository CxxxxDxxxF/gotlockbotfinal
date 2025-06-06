import logging
from discord.ext import tasks

log = logging.getLogger("gotlockz")


def create_log_guild_count_task(bot):
    """Return a task that logs how many guilds the bot is connected to."""

    @tasks.loop(minutes=30)
    async def log_guild_count():
        log.info("Currently connected to %d guild(s)", len(bot.guilds))

    return log_guild_count
