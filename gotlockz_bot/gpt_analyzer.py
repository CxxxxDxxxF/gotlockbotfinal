import openai
from config import OPENAI_API_KEY

openai.api_key = OPENAI_API_KEY


def build_vip_prompt(bet: dict, mlb_context: dict) -> str:
    prompt = f"""
You are a hype-driven, stat-backed MLB betting analyst. Today is {bet['date']}.
Game: {bet['teamA']} vs {bet['teamB']}.
Starter {mlb_context['pitcherA_stats'].get('name')} Stats (Last 3): ERA {mlb_context['pitcherA_stats'].get('ERA')}, WHIP {mlb_context['pitcherA_stats'].get('WHIP')}, K/9 {mlb_context['pitcherA_stats'].get('K9')}
Starter {mlb_context['pitcherB_stats'].get('name')} Stats (Last 3): ERA {mlb_context['pitcherB_stats'].get('ERA')}, WHIP {mlb_context['pitcherB_stats'].get('WHIP')}, K/9 {mlb_context['pitcherB_stats'].get('K9')}
Our Pick: {bet['teamA']} {bet['line']} @ {bet['odds']}. Units: {bet['units']}.
Structuring:

1. Header: "VIP PLAY #{bet['play_number']}: {bet['teamA']} vs {bet['teamB']} – {bet['line']} @ {bet['odds']} ({bet['units']} Units)"
2. Body:
   • Paragraph 1: Why we love the play—mention form, historical edge, numbers.
   • Paragraph 2: Supporting statistical bullet points.
   • Paragraph 3: Closing hype—call to action.
"""
    return prompt


def build_research_prompt(teamA: str, teamB: str, ml: dict, spread: float, total: float,
                          pitcherA_stats: dict, pitcherB_stats: dict,
                          teamA_metrics: dict, teamB_metrics: dict) -> str:
    return f"""
You are an expert MLB data analyst. Provide a concise 100-word "Quick Pick" verdict
plus 2–3 bullet highlights. Data below:

Teams: {teamA} vs {teamB}
Lines: Moneyline: {ml.get(teamA)} / {ml.get(teamB)} | Spread: {spread} | Total: {total}

Starter {pitcherA_stats.get('name')} (Last 5 starts): ERA {pitcherA_stats.get('ERA')},
WHIP {pitcherA_stats.get('WHIP')}, K/9 {pitcherA_stats.get('K9')}

Starter {pitcherB_stats.get('name')} (Last 5 starts): ERA {pitcherB_stats.get('ERA')},
WHIP {pitcherB_stats.get('WHIP')}, K/9 {pitcherB_stats.get('K9')}

{teamA} Offense: R/G {teamA_metrics['RPG']:.2f}, BA vs RHP {teamA_metrics['BA_vs_RHP']:.3f},
Bullpen ERA (14d) {teamA_metrics['BP_ERA_14']:.2f}

{teamB} Offense: R/G {teamB_metrics['RPG']:.2f}, BA vs LHP {teamB_metrics['BA_vs_LHP']:.3f},
Bullpen ERA (14d) {teamB_metrics['BP_ERA_14']:.2f}

Please give a bottom-line pick with reasoning and highlight 2–3 key stats.
"""


def call_openai(prompt: str) -> str:
    response = openai.ChatCompletion.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": "You are an expert MLB betting analyst."},
            {"role": "user", "content": prompt},
        ],
        max_tokens=800,
        temperature=0.7,
    )
    return response.choices[0].message.content.strip()
