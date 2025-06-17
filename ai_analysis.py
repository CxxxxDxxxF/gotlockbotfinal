# ai_analysis.py

#!/usr/bin/env python3
"""
ai_analysis.py

Synchronous GPT-based analysis generator for bets.
"""
import os
import logging
from openai import OpenAI

# ---- Logging Setup ----
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# ---- OpenAI Client ----
API_KEY = os.getenv("OPENAI_API_KEY")
if not API_KEY:
    raise RuntimeError("OPENAI_API_KEY environment variable not set.")
client = OpenAI(api_key=API_KEY)


def generate_analysis(
    bet_details: dict,
    model: str = "gpt-4",
    temperature: float = 0.7
) -> str:
    """
    Generates a concise, data-driven betting analysis.
    Expects bet_details with keys: away, home or player, bet, odds, units (optional).
    """
    if not isinstance(bet_details, dict):
        logger.warning("bet_details is not a dictionary.")
        return "Invalid bet details provided."

    # build a human‐readable game identifier
    if "away" in bet_details and "home" in bet_details:
        game = f"{bet_details['away']} @ {bet_details['home']}"
    else:
        game = bet_details.get("player", "Unknown Bet")

    pick  = bet_details.get("bet", "Unknown Bet")
    units = bet_details.get("units", "N/A")

    # system + user prompt
    system = "You are an expert MLB betting analyst."
    user   = (
        f"Here are the bet details:\n"
        f"- Game/Player: {game}\n"
        f"- Pick: {pick}\n"
        f"- Odds: {bet_details.get('odds','N/A')}\n"
        f"- Units: {units}\n\n"
        "Write a 1–2 paragraph, punchy, persuasive analysis of why this is a strong wager."
    )

    try:
        resp = client.chat.completions.create(
            model=model,
            messages=[
                {"role": "system",  "content": system},
                {"role": "user",    "content": user}
            ],
            temperature=temperature,
            max_tokens=300,
        )
        return resp.choices[0].message.content.strip()
    except Exception:
        logger.exception("Error generating analysis.")
        return "⚠️ Error generating analysis."
