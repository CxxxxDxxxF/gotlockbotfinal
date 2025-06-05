import pytest
from gotlockz_bot.valuebets_module import valuebets

class DummyChannel:
    def __init__(self):
        self.sent = []
    async def send(self, embed=None, **kwargs):
        self.sent.append(embed)

class DummyCtx:
    def __init__(self):
        self.channel = DummyChannel()
    async def send(self, embed=None, **kwargs):
        await self.channel.send(embed=embed)
    async def reply(self, *args, **kwargs):
        self.channel.sent.append('reply')

@pytest.mark.asyncio
async def test_valuebets(monkeypatch):
    ctx = DummyCtx()
    monkeypatch.setattr('gotlockz_bot.valuebets_module.get_all_upcoming_odds', lambda: {
        'Yankees vs Red Sox': {
            'moneyline': {'Yankees': -200, 'Red Sox': +180},
            'spread': -1.5,
            'total': 9.0
        }
    })
    monkeypatch.setattr('gotlockz_bot.valuebets_module.get_proj_win_pct', lambda team: 0.63 if team=='Yankees' else 0.48)
    await valuebets(ctx, 0.05)
    assert ctx.channel.sent
    embed = ctx.channel.sent[0]
    assert embed.fields[0].name == 'Yankees vs Red Sox'
