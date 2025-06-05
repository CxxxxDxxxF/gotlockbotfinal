from gotlockz_bot.utils import implied_prob_from_ml, format_moneyline, format_date
import datetime

def test_implied_prob():
    assert abs(implied_prob_from_ml(-150) - 0.6) < 0.001
    assert abs(implied_prob_from_ml(120) - 0.4545) < 0.01

def test_format_moneyline():
    assert format_moneyline(-150) == '-150'
    assert format_moneyline(120) == '+120'

def test_format_date():
    d = datetime.datetime(2025, 6, 5)
    assert format_date(d) == '2025-06-05'
