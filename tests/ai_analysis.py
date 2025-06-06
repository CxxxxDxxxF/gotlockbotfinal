import openai
import os

openai.api_key = os.getenv("OPENAI_API_KEY")

def generate_analysis(bet_details: dict) -> str:
    prompt = (
        f"You're a professional MLB betting analyst. Analyze this bet based on the details:
"
        f"Game: {bet_details.get('game')}
"
        f"Pick: {bet_details.get('pick')}
"
        f"Units: {bet_details.get('units')}
"
        f"Date: {bet_details.get('date')} Time: {bet_details.get('time')}
"
        f"VIP: {bet_details.get('vip')}
"
        "Give a short paragraph of betting insight backed by real recent stats."
    )

    try:
        response = openai.ChatCompletion.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": "You are an expert MLB betting analyst."},
                {"role": "user", "content": prompt}
            ]
        )
        return response["choices"][0]["message"]["content"]
    except Exception as e:
        return f"Error generating analysis: {e}"
