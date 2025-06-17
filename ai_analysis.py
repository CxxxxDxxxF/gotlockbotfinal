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
    # … your existing validation and “game”/“pick” extraction …

    # 1) Stronger system prompt
    system = (
        "You are a veteran MLB handicapper. "
        "Your goal: write a concise, 2-paragraph analysis that convinces a smart bettor to pull the trigger. "
        "Use crisp stats (recent form, pitcher matchup, park factors), highlight any edge or value, "
        "and end with a clear recommendation."
    )

    # 2) Structured user prompt
    user = (
        f"Here are the bet details:\n"
        f"- Game: {game}\n"
        f"- Pick: {pick}\n"
        f"- Odds: {bet_details.get('odds','N/A')}\n"
        f"- Units: {bet_details.get('units','N/A')}\n\n"

        "In your analysis, be sure to cover:\n"
        "1. Recent performance trends (last 5 games)\n"
        "2. Starting pitcher matchup\n"
        "3. Venue or weather factors if relevant\n"
        "4. Why these odds represent value\n\n"

        "Write exactly two paragraphs, each 2–4 sentences. "
        "Begin with a one-sentence hook and close with a one-sentence recommendation."
    )

    try:
        resp = client.chat.completions.create(
            model=model,
            messages=[
                {"role": "system", "content": system},
                {"role": "user",   "content": user}
            ],
            temperature=temperature,
            max_tokens=350,
        )
        return resp.choices[0].message.content.strip()
    except Exception:
        logger.exception("Error generating analysis.")
        return "⚠️ Error generating analysis."
