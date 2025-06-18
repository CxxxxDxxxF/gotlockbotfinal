# ai_analysis.py

"""
Handles generating analysis for bets using OpenAI's GPT.
"""
import os
import logging
from datetime import datetime
import openai

# ——— Logging ———
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# ——— OpenAI Configuration ———
OPENAI_KEY = os.getenv("OPENAI_API_KEY")
if not OPENAI_KEY:
    raise RuntimeError("OPENAI_API_KEY environment variable not set.")
openai.api_key = OPENAI_KEY

# allow overriding via env for easy tuning
DEFAULT_MODEL       = os.getenv("OPENAI_MODEL", "gpt-4")
DEFAULT_TEMPERATURE = float(os.getenv("ANALYSIS_TEMPERATURE", 0.7))

def generate_analysis(
    bet_details: dict,
    model: str = DEFAULT_MODEL,
    temperature: float = DEFAULT_TEMPERATURE
) -> str:
    """
    Generates a concise, 2-paragraph, data-driven MLB betting analysis.

    Expects bet_details to include either:
      • a full "game" string (e.g. "NYY @ BOS"), or both "away"/"home"
      • "bet" (e.g. "Yankees – Moneyline")
      • "odds" (e.g. "-190")
    Optionally:
      • "units", "date", "time"

    Returns:
      A 2-paragraph analysis, or an error message on failure.
    """
    if not isinstance(bet_details, dict):
        logger.warning("generate_analysis: bet_details is not a dict")
        return "⚠️ Invalid bet details provided."

    # build a fallback game string
    game = bet_details.get("game")
    if not game and bet_details.get("away") and bet_details.get("home"):
        game = f"{bet_details['away']} @ {bet_details['home']}"
    game = game or "Unknown Game"

    pick  = bet_details.get("bet") or bet_details.get("pick") or "Unknown Pick"
    odds  = bet_details.get("odds", "N/A")
    units = bet_details.get("units", "N/A")
    date  = bet_details.get("date", datetime.now().strftime("%-m/%-d/%y"))
    time  = bet_details.get("time", "")
    dt_str = f"{date} {time}".strip()

    system_prompt = (
        "You are a veteran MLB handicapper. "
        "Write exactly two paragraphs (2–4 sentences each) that convince a smart bettor to pull the trigger. "
        "Use crisp stats (recent form, pitcher matchup, park/weather factors), highlight any edge or value, "
        "and end each analysis with a clear recommendation."
    )

    user_prompt = (
        f"Bet details:\n"
        f"- Game: {game}\n"
        f"- Pick: {pick}\n"
        f"- Odds: {odds}\n"
        f"- Units: {units}\n"
        f"- Date/Time: {dt_str}\n\n"
        "In your analysis cover:\n"
        "1. Last five games performance\n"
        "2. Starting pitcher matchup\n"
        "3. Venue, park or weather factors\n"
        "4. Why these odds represent value\n\n"
        "Begin with a hook and close with a recommendation."
    )

    try:
        resp = openai.ChatCompletion.create(
            model=  model,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role":    "user", "content": user_prompt}
            ],
            temperature=temperature,
            max_tokens=350,
        )
        return resp.choices[0].message.content.strip()

    except Exception as e:
        logger.exception("Error generating analysis")
        return f"⚠️ Error generating analysis: {e}"
