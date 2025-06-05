from gotlockz_bot.gpt_analyzer import build_vip_prompt

def test_build_vip_prompt_contains_fields():
    bet = {
        'teamA': 'New York Yankees',
        'teamB': 'Boston Red Sox',
        'line': -1.5,
        'odds': +120,
        'date': '2025-06-06',
        'units': 3,
        'type': 'VIP',
        'play_number': 1,
    }
    mlb_context = {
        'pitcherA_stats': {'name': 'Gerrit Cole', 'ERA': 2.85, 'WHIP': 1.05, 'K9': 8.2},
        'pitcherB_stats': {'name': 'Chris Sale', 'ERA': 3.10, 'WHIP': 1.15, 'K9': 7.9},
    }
    prompt = build_vip_prompt(bet, mlb_context)
    assert 'VIP PLAY #1' in prompt
    assert '2025-06-06' in prompt
    assert 'Gerrit Cole' in prompt
    assert '-1.5' in prompt
    assert '+120' in prompt
    assert '3 Units' in prompt
