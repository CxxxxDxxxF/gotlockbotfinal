#!/usr/bin/env python3
"""
ai_analysis.py

Handles generation of hype-driven, stat-backed betting analyses using OpenAI's API.
"""
import os
import logging
from typing import Dict
from openai import OpenAI, error as openai_error

# ---- Logging Setup ----
logging.basicConfig(
    format="[%(asctime)s] %(levelname)s:%(name)s: %(message)s",
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# ---- OpenAI Client Initialization ----
API_KEY = os.getenv("OPENAI_API_KEY")
if not API_KEY:
    logger.critical("OPENAI_API_KEY environment variable not set.")
    raise RuntimeError("Missing OPENAI_API_KEY environment variable.")

client = OpenAI(api_key=API_KEY)

async def generate_analysis(
    bet_details: Dict[str, str],
    model: str = "gpt-4",
    temperature: float = 0.7,
    max_tokens: int = 512
) -> str:
    """
    Generates a hype-driven, stat-backed betting analysis for MLB games.

    Args:
        bet_details (Dict[str, str]): Contains keys 'game', 'bet', and 'odds'.
        model (str): OpenAI model to use.
        temperature (float): Sampling temperature for creativity.
        max_tokens (int): Max tokens for the response.

    Returns:
        str: The generated analysis, or an error message.
    """
    # Validate input
    if not isinstance(bet_details, dict):
        logger.warning("generate_analysis called with non-dict bet_details.")
        return "Invalid bet details provided."

    game = bet_details.get("game", "Unknown Game")
    bet = bet_details.get("bet", "Unknown Bet")
    odds = bet_details.get("odds", "N/A")

    # Build system and user messages
    system_message = {
        "role": "system",
        "content": (
            "You are an expert MLB betting analyst. "
            "Provide a hype-driven, stat-backed, and persuasive analysis. "
            "Use at least three concrete statistics or historical performance references."
        )
    }
    user_prompt = (
        f"Game: {game}\n"
        f"Pick: {bet}\n"
        f"Odds: {odds}\n"
        "
        "Write a multi-paragraph analysis explaining why this pick is strong, referencing recent form, matchup advantages, and historical trends. "
        "Close with a confident prediction."
    )
    user_message = {"role": "user", "content": user_prompt}

    # Log the prompt (without leaking tokens)
    logger.info("Generating analysis with OpenAI API for pick: %s | %s | %s", game, bet, odds)

    try:
        response = await client.chat.completions.create(
            model=model,
            messages=[system_message, user_message],
            temperature=temperature,
            max_tokens=max_tokens,
        )
        text = response.choices[0].message.content.strip()
        logger.debug("OpenAI response received: %s", text[:100] + '...')
        return text

    except openai_error.OpenAIError as oe:
        logger.exception("OpenAI API error during analysis.")
        return f"Error generating analysis: {oe.__class__.__name__} - {oe}"
    except Exception as e:
        logger.exception("Unexpected error in generate_analysis.")
        return f"Unexpected error generating analysis: {e}"
