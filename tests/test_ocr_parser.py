from gotlockz_bot.ocr_parser import image_to_text, parse_bets_from_text


def test_parse_bets_from_text(tmp_path):
    # create fake text to simulate OCR
    text = 'NYY ML -150\nBOS -1.5 +120'
    bets = parse_bets_from_text(text)
    assert isinstance(bets, list) and bets
    for bet in bets:
        assert 'teamA' in bet and 'line' in bet and 'odds' in bet
    assert bets[0]['teamA'] == 'New York Yankees'
    assert bets[0]['odds'] == -150
