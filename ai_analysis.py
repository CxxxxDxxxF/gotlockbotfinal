# ai_analysis.py

"""
Handles generating analysis for bets using OpenAI's GPT.
"""
import os
import logging
from datetime import datetime
from openai import OpenAI

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Validate API key
API_KEY = os.getenv("OPENAI_API_KEY")
if not API_KEY:
    raise RuntimeError("OPENAI_API_KEY environment variable not set.")

# Initialize OpenAI client
client = OpenAI(api_key=API_KEY)

def generate_analysis(
    bet_details: dict,
    model: str = "gpt-4",
    temperature: float = 0.7
) -> str:
    """
    Generates a concise, 2-paragraph, data-driven MLB betting analysis.

    Args:
        bet_details (dict): Should include keys: "game" OR ("away","home"), "bet", "odds", optionally "units", "date", "time", "vip".
        model (str): OpenAI model to use.
        temperature (float): Sampling randomness.

    Returns:
        str: Analysis text or error message.
    """
    if not isinstance(bet_details, dict):
        logger.warning("bet_details is not a dict.")
        return "Invalid bet details provided."

    # Extract values with defaults
    game  = bet_details.get("game")
    if not game and bet_details.get("away") and bet_details.get("home"):
        game = f"{bet_details['away']} @ {bet_details['home']}"
    game = game or "Unknown Game"

    pick  = bet_details.get("bet") or bet_details.get("pick") or "Unknown Bet"
    odds  = bet_details.get("odds", "N/A")
    units = bet_details.get("units", "N/A")
    date  = bet_details.get("date", datetime.now().strftime("%-m/%-d/%y"))
    time  = bet_details.get("time", "")
    vip   = bet_details.get("vip", False)

    # System and user prompts
    system_prompt = (
        "You are a veteran MLB handicapper. "
        "Write a concise, 2-paragraph analysis that convinces a smart bettor to pull the trigger. "
        "Use crisp stats (recent form, pitcher matchup, park/weather factors), highlight any edge or value, "
        "and end with a clear recommendation."
    )

    user_prompt = (
        f"Here are the bet details:\n"
        f"- Game: {game}\n"
        f"- Pick: {pick}\n"
        f"- Odds: {odds}\n"
        f"- Units: {units}\n"
        f"- Date: {date} {time}\n\n"
        "In your analysis, cover:\n"
        "1. Last 5 games performance\n"
        "2. Starting pitcher matchup\n"
        "3. Venue/park or weather factors\n"
        "4. Why these odds represent value\n\n"
        "Write exactly two paragraphs, each 2–4 sentences. "
        "Start with a hook and close with a recommendation."
    )

    try:
        response = client.chat.completions.create(
            model=model,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user",   "content": user_prompt}
            ],
            temperature=temperature,
            max_tokens=350,
        )
        return response.choices[0].message.content.strip()

    except Exception as e:
        logger.exception("Error generating analysis.")
        return f"⚠️ Error generating analysis: {e}"
