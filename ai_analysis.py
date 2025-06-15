
import os
from openai import OpenAI

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

async def generate_analysis(bet_details):
    if not bet_details:
        return "No bet details found."

    game = bet_details.get("game", "Unknown Game")
    bet = bet_details.get("bet", "Unknown Bet")
    odds = bet_details.get("odds", "N/A")

    prompt = f"""
You're an expert MLB betting analyst. Generate a hype-driven betting analysis for the following pick:

Game: {game}
Bet: {bet}
Odds: {odds}

The tone should be confident, stat-backed, and persuasive.
"""

    response = await client.chat.completions.create(
        model="gpt-4",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.7,
    )

    return response.choices[0].message.content.strip()
