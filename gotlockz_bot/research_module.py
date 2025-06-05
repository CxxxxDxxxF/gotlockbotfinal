import discord
from discord.ext import commands
from gotlockz_bot.odds_client import get_line_for_matchup
from gotlockz_bot.mlb_client import get_last_five_stats, get_team_metrics
from gotlockz_bot.gpt_analyzer import build_research_prompt, call_openai

@commands.command(name='research')
async def research(ctx, *, matchup: str):
    try:
        teamA, _, teamB = matchup.partition(' vs ')
        lines = get_line_for_matchup(teamA, teamB)
        if not lines:
            await ctx.reply('\u26a0\ufe0f No upcoming game found for those teams.')
            return
        ml = lines['moneyline']
        spread = lines['spread']
        total = lines['total']
        pitcherA = get_team_metrics(teamA).get('probable_starter')
        pitcherB = get_team_metrics(teamB).get('probable_starter')
        statsA = get_last_five_stats(pitcherA) if pitcherA else {}
        statsB = get_last_five_stats(pitcherB) if pitcherB else {}
        teamMetricsA = get_team_metrics(teamA)
        teamMetricsB = get_team_metrics(teamB)
        prompt = build_research_prompt(
            teamA, teamB, ml, spread, total,
            statsA, statsB, teamMetricsA, teamMetricsB
        )
        verdict = call_openai(prompt)
        embed = discord.Embed(title=f"\ud83d\udd0d Research: {teamA} vs {teamB}", color=0x1f8b4c)
        embed.add_field(name="Current Lines", value=f"Moneyline: {ml.get(teamA)} / {ml.get(teamB)}\nSpread: {spread}\nTotal: {total}", inline=False)
        embed.add_field(name=f"{pitcherA} (Last 5 Starts)", value=f"ERA: {statsA.get('ERA', 'N/A')}, WHIP: {statsA.get('WHIP', 'N/A')}, K/9: {statsA.get('K9', 'N/A')}", inline=True)
        embed.add_field(name=f"{pitcherB} (Last 5 Starts)", value=f"ERA: {statsB.get('ERA', 'N/A')}, WHIP: {statsB.get('WHIP', 'N/A')}, K/9: {statsB.get('K9', 'N/A')}", inline=True)
        embed.add_field(name=f"{teamA} Metrics", value=f"R/G: {teamMetricsA['RPG']:.2f}, BA vs RHP: {teamMetricsA['BA_vs_RHP']:.3f},\nBullpen ERA (14d): {teamMetricsA['BP_ERA_14']:.2f}", inline=False)
        embed.add_field(name=f"{teamB} Metrics", value=f"R/G: {teamMetricsB['RPG']:.2f}, BA vs LHP: {teamMetricsB['BA_vs_LHP']:.3f},\nBullpen ERA (14d): {teamMetricsB['BP_ERA_14']:.2f}", inline=False)
        embed.add_field(name="\ud83c\udfd1 GPT Verdict", value=verdict, inline=False)
        await ctx.send(embed=embed)
    except Exception as e:
        await ctx.reply('\u274c Something went wrong in /research. Try again later.')
        print('Research Error:', e)
