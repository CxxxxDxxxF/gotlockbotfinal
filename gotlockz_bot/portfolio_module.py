"""Simple portfolio tracking for wagers."""


class Portfolio:
    def __init__(self):
        self.bets = []

    def add_bet(self, team: str, amount: float, odds: float):
        self.bets.append({"team": team, "amount": amount, "odds": odds})

    def total_exposure(self) -> float:
        return sum(b["amount"] for b in self.bets)

    def clear(self):
        self.bets.clear()
