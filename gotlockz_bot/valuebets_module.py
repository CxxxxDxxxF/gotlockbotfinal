"""Helpers to identify value bets."""


def is_value_bet(probability: float, decimal_odds: float) -> bool:
    """Return True if the bet has positive expected value."""
    implied_prob = 1 / decimal_odds
    return probability > implied_prob
