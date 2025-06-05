from discord.ext import commands
from gotlockz_bot.odds_client import get_all_upcoming_odds
from gotlockz_bot.mlb_client import get_proj_win_pct
import discord


def implied_prob_from_ml(ml: int) -> float:
    if ml < 0:
        return abs(ml) / (abs(ml) + 100)
    return 100 / (ml + 100)

@commands.command(name='valuebets')
async def valuebets(ctx, threshold: float = 0.05):
    all_odds = get_all_upcoming_odds()
    edges = []
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
        if edgeA >= threshold:
            edges.append({'team': teamA, 'opp': teamB, 'implied': impliedA, 'proj': projA, 'edge': edgeA})
        if edgeB >= threshold:
            edges.append({'team': teamB, 'opp': teamA, 'implied': impliedB, 'proj': projB, 'edge': edgeB})
    if not edges:
        await ctx.reply('\u274c No strong value picks found tonight.')
        return
    embed = discord.Embed(title=f"\ud83d\udc8e Value Bets (Threshold \u2265 {threshold*100:.1f}%)", color=0x0099ff)
    for e in edges:
        embed.add_field(name=f"{e['team']} vs {e['opp']}", value=f"Implied: {e['implied']*100:.1f}%\nProjected: {e['proj']*100:.1f}%\nEdge: {e['edge']*100:.1f}%", inline=False)
    await ctx.send(embed=embed)
