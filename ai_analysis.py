import os
import logging
import openai

log = logging.getLogger(__name__)

openai.api_key = os.getenv("OPENAI_API_KEY")


async def generate_analysis(bet_details: dict) -> str:
    """Generate a short analysis of the bet using OpenAI asynchronously."""
    if not openai.api_key:
        log.warning("OPENAI_API_KEY is not configured; skipping analysis")
        return "AI analysis unavailable"

    system_msg = (
        "You are a helpful assistant that analyzes MLB bets. "
        "Provide a concise recommendation based on the following details."
    )
    user_content = "\n".join(f"{k}: {v}" for k, v in bet_details.items())

    try:
        response = await openai.ChatCompletion.acreate(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": system_msg},
                {"role": "user", "content": user_content},
            ],
            max_tokens=150,
        )
        return response.choices[0].message["content"].strip()
    except Exception as exc:  # pragma: no cover - network failure
        log.error("OpenAI request failed: %s", exc)
        return "Unable to generate AI analysis."
