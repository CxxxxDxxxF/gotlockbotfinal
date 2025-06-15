import os
from openai import OpenAI
import traceback

# Initialize OpenAI client using the new v1+ SDK
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

def generate_analysis(details):
    """
    Uses GPT to generate a hype betting breakdown based on parsed bet details.
    """
    try:
        game = details.get("game", "Unknown Game")
        bet = details.get("bet", "Unknown Bet")
        odds = details.get("odds", "N/A")

        prompt = (
            f"You're a professional sports betting analyst. Write a high-energy, hype-filled breakdown "
            f"for the following bet:\n\n"
            f"📅 Game: {game}\n"
            f"📈 Bet: {bet} ({odds})\n\n"
            f"Your response should sound confident and sharp, like it's coming from a sports handicapper hyping it up to clients. "
            f"Use stats, recent performance trends, and persuasive phrasing. Keep it 3-5 sentences."
        )

        response = client.chat.completions.create(
            model="gpt-4",  # Or use "gpt-3.5-turbo" if needed
            messages=[
                {"role": "system", "content": "You are a sharp and confident sports betting analyst."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.85
        )

        return response.choices[0].message.content.strip()

    except Exception as e:
        print(f"❌ GPT analysis failed: {e}")
        traceback.print_exc()
        return "Unable to generate AI analysis."
