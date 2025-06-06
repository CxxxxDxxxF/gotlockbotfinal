import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from image_processing import parse_bet_details


def test_parse_units_detection():
    text = "Bet is 1.5 units"
    result = parse_bet_details(text)
    assert result["units"] == "1.5"


def test_parse_vip_detection():
    text = "VIP pick\nBet is 2 units"
    result = parse_bet_details(text)
    assert result["vip"] == "Yes"
    assert result["units"] == "2"

