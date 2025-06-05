import pytest
from gotlockz_bot.portfolio_module import myportfolio

class DummyChannel:
    def __init__(self):
        self.sent = []
    async def send(self, embed=None, **kwargs):
        self.sent.append(embed)

class DummyAuthor:
    def __init__(self):
        self.id = 1
        self.display_name = 'User'

class DummyCtx:
    def __init__(self):
        self.channel = DummyChannel()
        self.author = DummyAuthor()
    async def reply(self, *args, **kwargs):
        self.channel.sent.append('reply')
    async def send(self, embed=None, **kwargs):
        await self.channel.send(embed=embed)

@pytest.mark.asyncio
async def test_myportfolio(monkeypatch):
    ctx = DummyCtx()
    monkeypatch.setattr('gotlockz_bot.portfolio_module.get_all_picks_for_user', lambda uid: [
        {"Units": 2, "Odds": -150, "Result": "W", "Payout": 3.33},
        {"Units": 1.5, "Odds": +120, "Result": "L", "Payout": 0},
        {"Units": 2, "Odds": -110, "Result": "P", "Payout": 2},
    ])
    await myportfolio(ctx)
    assert ctx.channel.sent
    embed = ctx.channel.sent[0]
    assert embed.fields[0].value == '3'
    assert embed.fields[1].value == '1-1-1'
