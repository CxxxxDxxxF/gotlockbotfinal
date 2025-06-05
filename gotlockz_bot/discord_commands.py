import discord
from discord.ext import commands
import tempfile
import aiohttp
import os

from gotlockz_bot.ocr_parser import image_to_text, parse_bets_from_text
from gotlockz_bot.mlb_client import get_today_schedule, get_last_five_stats, get_team_metrics
from gotlockz_bot.gpt_analyzer import build_vip_prompt, call_openai
from gotlockz_bot.sheets_client import get_count_of_type, append_pick_to_sheet
from config import SHEETS_SPREADSHEET_ID

async def download_attachment(url: str) -> str:
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as resp:
            if resp.status != 200:
                return None
            data = await resp.read()
            tmp_file = tempfile.NamedTemporaryFile(delete=False, suffix='.png')
            tmp_file.write(data)
            tmp_file.close()
            return tmp_file.name

@commands.command(name='postpick')
async def postpick(ctx, units: float, target_channel: str = None):
    if not ctx.message.attachments:
        await ctx.reply("\ud83d\udcf8 Please attach a clear bet-slip image.")
        return
    attachment = ctx.message.attachments[0]
    image_path = await download_attachment(attachment.url)
    if not image_path:
        await ctx.reply("\u274c Error downloading the image. Try again.")
        return
    raw_text = image_to_text(image_path)
    bets = parse_bets_from_text(raw_text)
    if not bets:
        await ctx.reply("\u274c Could not parse any bets. Make sure the image is legible.")
        os.remove(image_path)
        return
    dest = ctx.channel
    for bet in bets:
        pick_type = 'VIP' if units >= 2 else 'FREE'
        count = get_count_of_type(SHEETS_SPREADSHEET_ID, pick_type)
        play_number = count + 1
        bet['date'] = ctx.message.created_at.strftime('%Y-%m-%d')
        bet['units'] = units
        bet['type'] = pick_type
        bet['play_number'] = play_number
        schedule = get_today_schedule()
        for matchup in schedule.keys():
            away, home = matchup.split(' vs ')
            if bet['teamA'] in (away, home):
                bet['teamB'] = home if away == bet['teamA'] else away
                break
        pitcherA = get_team_metrics(bet['teamA']).get('probable_starter')
        pitcherB = get_team_metrics(bet['teamB']).get('probable_starter')
        statsA = get_last_five_stats(pitcherA) if pitcherA else {}
        statsB = get_last_five_stats(pitcherB) if pitcherB else {}
        mlb_context = {'pitcherA_stats': statsA, 'pitcherB_stats': statsB}
        prompt = build_vip_prompt(bet, mlb_context)
        analysis_text = call_openai(prompt)
        embed = discord.Embed(title=f"{pick_type} PLAY #{play_number}", color=0xff0000)
        embed.add_field(name="Game", value=f"{bet['teamA']} vs {bet['teamB']} ({bet['line']} @ {bet['odds']})", inline=False)
        embed.add_field(name="Units", value=str(units), inline=True)
        embed.add_field(name="Date", value=bet['date'], inline=True)
        embed.add_field(name="Analysis", value=analysis_text, inline=False)
        await dest.send(embed=embed)
        row = [bet['date'], pick_type, play_number, bet['teamA'], bet['teamB'], bet['line'], bet['odds'], units]
        append_pick_to_sheet(SHEETS_SPREADSHEET_ID, row)
    os.remove(image_path)

@commands.command(name='help')
async def help_cmd(ctx):
    msg = (
        "__**How to use /postpick**__\n"
        "1\u20e3 Attach a clear bet-slip image (JPEG/PNG).\n"
        "2\u20e3 Type `/postpick <units> [#channel]`\n"
        "Example: `/postpick 3 #vip-picks`\n"
        "The bot will OCR, fetch MLB stats, call GPT, and post the analysis.\n"
    )
    await ctx.reply(msg)
