import asyncio
from datetime import datetime
import discord
from discord.ext import commands
from gotlockz_bot.sheets_client import get_watchlist, append_linewatch_log, update_watchlist_last_line, append_watchlist_row
from gotlockz_bot.odds_client import get_line_for_matchup
from gotlockz_bot.mlb_client import get_today_schedule
from config import SHEETS_SPREADSHEET_ID

async def linewatch_loop(bot: discord.Client):
    await bot.wait_until_ready()
    while True:
        watchlist = get_watchlist()
        for entry in watchlist:
            team = entry['Team']
            threshold = float(entry['Threshold'])
            channel = bot.get_channel(int(entry['ChannelID']))
            old_line = int(entry['LastLine'])
            opponent = entry['Opponent']
            data = get_line_for_matchup(team, opponent)
            if not data:
                continue
            new_line = int(data['moneyline'].get(team, old_line))
            if abs(new_line - old_line) >= threshold:
                diff = new_line - old_line
                timestamp = datetime.utcnow().isoformat()
                await channel.send(f"\ud83d\udea8 **Line Alert for {team}**: Moneyline moved from {old_line:+d} to {new_line:+d} (\u0394 {diff:+d}).")
                append_linewatch_log([timestamp, team, old_line, new_line, diff, entry['GameDate']])
                update_watchlist_last_line(entry['RowID'], new_line)
        await asyncio.sleep(300)

@commands.command(name='watchline')
async def watchline(ctx, team: str, threshold: float, channel: discord.TextChannel = None):
    chan = channel or ctx.channel
    schedule = get_today_schedule()
    opponent = None
    game_date = None
    for matchup, info in schedule.items():
        away, home = matchup.split(' vs ')
        if team in (away, home):
            opponent = home if away == team else away
            game_date = info['gameDate']
            break
    if not opponent:
        await ctx.reply(f"\u26a0\ufe0f Could not find any upcoming game for '{team}'.")
        return
    current_data = get_line_for_matchup(team, opponent)
    if not current_data:
        await ctx.reply(f"\u26a0\ufe0f No line data found for '{team} vs {opponent}'.")
        return
    initial_line = int(current_data['moneyline'].get(team))
    row_id = append_watchlist_row([ctx.author.id, team, opponent, threshold, chan.id, initial_line, game_date])
    await ctx.reply(f"\u2705 Now watching line for **{team}** vs **{opponent}**. Alert at \u00b1{int(threshold)} change.")
