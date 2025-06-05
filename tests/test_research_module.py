import pytest

from gotlockz_bot.research_module import research

class DummyChannel:
    def __init__(self):
        self.sent = []
    async def send(self, *args, **kwargs):
        self.sent.append((args, kwargs))

class DummyCtx:
    def __init__(self):
        self.channel = DummyChannel()
    async def reply(self, *args, **kwargs):
        self.channel.sent.append(('reply', args, kwargs))
    async def send(self, *args, **kwargs):
        await self.channel.send(*args, **kwargs)

@pytest.mark.asyncio
async def test_research(monkeypatch):
    ctx = DummyCtx()
    monkeypatch.setattr('gotlockz_bot.research_module.get_line_for_matchup', lambda a,b: {"moneyline": {a: -150, b: +130}, "spread": -1.5, "total": 8.5})
    monkeypatch.setattr('gotlockz_bot.research_module.get_team_metrics', lambda t: {"probable_starter": t+" P", "RPG": 4.5, "BA_vs_RHP": 0.265, "BA_vs_LHP": 0.254, "BP_ERA_14": 3.55})
    monkeypatch.setattr('gotlockz_bot.research_module.get_last_five_stats', lambda p: {"name": p, "ERA": 2.8, "WHIP": 1.0, "K9": 9})
    monkeypatch.setattr('gotlockz_bot.research_module.call_openai', lambda prompt: "verdict")
    await research(ctx, matchup="Yankees vs Astros")
    assert ctx.channel.sent
    embed = ctx.channel.sent[0][1]['embed']
    assert embed.title.startswith('\ud83d\udd0d Research')
    assert len(embed.fields) == 6
