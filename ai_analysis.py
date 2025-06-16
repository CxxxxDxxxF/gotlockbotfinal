import os
import logging
from openai import OpenAI

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Check for API key at startup
API_KEY = os.getenv("OPENAI_API_KEY")
if not API_KEY:
    raise RuntimeError("OPENAI_API_KEY environment variable not set.")

client = OpenAI(api_key=API_KEY)

async def generate_analysis(
    bet_details: dict,
    model: str = "gpt-4",
    temperature: float = 0.7
) -> str:
    """
    Generates a concise, data-driven betting analysis for MLB picks.

    Args:
        bet_details (dict): Dictionary containing bet information.
        model (str): OpenAI model to use (default: "gpt-4").
        temperature (float): Sampling temperature for output randomness.

    Returns:
        str: Generated analysis or error message.
    """
    if not isinstance(bet_details, dict):
        logger.warning("bet_details is not a dictionary.")
        return "Invalid bet details provided."

    # Extract details with sensible defaults
    game  = bet_details.get("game", "Unknown Game")
    pick  = bet_details.get("bet", bet_details.get("pick", "Unknown Bet"))
    units = bet_details.get("units", "N/A")
    date  = bet_details.get("date", "N/A")
    time  = bet_details.get("time", "")
    vip   = bet_details.get("vip", False)

    # Build the user prompt
    prompt = (
        "You're a professional MLB betting analyst. "
        "Provide a concise, data-driven insight for the following bet:\n\n"
        f"Game: {game}\n"
        f"Pick: {pick}\n"
        f"Units: {units}\n"
        f"Date: {date} {time}\n"
        f"VIP: {vip}\n"
    )

    try:
        # Call synchronously since this method is not async
        response = client.chat.completions.create(
            model=model,
            messages=[
                {"role": "system", "content": "You are an expert MLB betting analyst."},
                {"role": "user",   "content": prompt}
            ],
            temperature=temperature,
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        logger.exception("Error generating analysis.")
        return f"Error generating analysis: {e}"
