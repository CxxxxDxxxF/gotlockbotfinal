from discord.ext import commands
import discord
from gotlockz_bot.sheets_client import get_all_picks_for_user

@commands.command(name='myportfolio')
async def myportfolio(ctx):
    user_id = ctx.author.id
    picks = get_all_picks_for_user(user_id)
    if not picks:
        await ctx.reply('\u26a0\ufe0f You have no recorded picks yet.')
        return
    total_units = sum(p['Units'] for p in picks)
    total_payout = sum(p['Payout'] for p in picks if p['Result'] == 'W')
    wins = sum(1 for p in picks if p['Result'] == 'W')
    losses = sum(1 for p in picks if p['Result'] == 'L')
    pushes = sum(1 for p in picks if p['Result'] == 'P')
    record_text = f"{wins}-{losses}-{pushes}"
    roi = ((total_payout - total_units) / total_units) * 100 if total_units else 0

    def current_streak(picks_list):
        streak = 0
        last_result = picks_list[-1]['Result']
        for p in reversed(picks_list):
            if p['Result'] == last_result and last_result in ['W', 'L', 'P']:
                streak += 1
            else:
                break
        return last_result, streak

    last_result, streak_count = current_streak(picks)
    streak_text = f"{last_result} x{streak_count}" if last_result in ['W', 'L', 'P'] else 'No streak'

    embed = discord.Embed(title=f"\ud83d\udcc8 {ctx.author.display_name}'s Portfolio", color=0xFFD700)
    embed.add_field(name="Total Picks", value=str(len(picks)), inline=True)
    embed.add_field(name="Record (W–L–P)", value=record_text, inline=True)
    embed.add_field(name="ROI", value=f"{roi:.2f}%", inline=True)
    embed.add_field(name="Avg Units/Pick", value=f"{total_units/len(picks):.2f}", inline=True)
    embed.add_field(name="Streak", value=streak_text, inline=True)
    await ctx.send(embed=embed)
