import discord
import os
from discord.ext import tasks
from gotlockz_bot.valuebets_module import valuebets, implied_prob_from_ml
from gotlockz_bot.sheets_client import get_recent_linewatch_logs
from config import DISCORD_TOKEN, DAILY_SUMMARY_CHANNEL_ID, VALUE_THRESHOLD

client = discord.Client(intents=discord.Intents.default())

@client.event
async def on_ready():
    print('Daily Summary Bot Logged In')
    send_daily_summary.start()

@tasks.loop(hours=24)
async def send_daily_summary():
    await client.wait_until_ready()
    channel = client.get_channel(int(DAILY_SUMMARY_CHANNEL_ID))
    edges = []
    # For simplicity call valuebets helper
    # But we just call get_all_upcoming_odds etc not to run openai
    from gotlockz_bot.odds_client import get_all_upcoming_odds
    from gotlockz_bot.mlb_client import get_proj_win_pct
    all_odds = get_all_upcoming_odds()
    for matchup, data in all_odds.items():
        teamA, teamB = matchup.split(' vs ')
        mlA = data['moneyline'].get(teamA)
        mlB = data['moneyline'].get(teamB)
        impliedA = implied_prob_from_ml(mlA)
        impliedB = implied_prob_from_ml(mlB)
        projA = get_proj_win_pct(teamA)
        projB = get_proj_win_pct(teamB)
        edgeA = projA - impliedA
        edgeB = projB - impliedB
        if edgeA >= VALUE_THRESHOLD:
            edges.append({'team': teamA, 'opp': teamB, 'implied': impliedA, 'proj': projA, 'edge': edgeA})
        if edgeB >= VALUE_THRESHOLD:
            edges.append({'team': teamB, 'opp': teamA, 'implied': impliedB, 'proj': projB, 'edge': edgeB})
    if edges:
        embed1 = discord.Embed(title='\ud83d\udc8e Top Value Bets', color=0x00ff00)
        for e in edges[:5]:
            embed1.add_field(name=f"{e['team']} vs {e['opp']}", value=f"Edge: {e['edge']*100:.1f}%", inline=False)
    else:
        embed1 = discord.Embed(title='\ud83d\udc8e Top Value Bets', description='None found', color=0x00ff00)
    logs = get_recent_linewatch_logs(hours=24)
    if logs:
        embed2 = discord.Embed(title='\ud83d\udea8 Biggest Line Moves (24h)', color=0xff0000)
        for log in logs:
            embed2.add_field(name=f"{log['Team']} (Game: {log['GameDate']})", value=f"{log['OldLine']} -> {log['NewLine']} (\u0394 {log['Difference']})", inline=False)
    else:
        embed2 = discord.Embed(title='\ud83d\udea8 Biggest Line Moves (24h)', description='No moves', color=0xff0000)
    await channel.send(embed=embed1)
    await channel.send(embed=embed2)

if __name__ == '__main__':
    client.run(DISCORD_TOKEN)
