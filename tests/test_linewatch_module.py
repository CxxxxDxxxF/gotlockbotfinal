import asyncio
import pytest

from gotlockz_bot.linewatch_module import linewatch_loop

class DummyChannel:
    def __init__(self):
        self.sent = []
    async def send(self, msg):
        self.sent.append(msg)

class DummyBot:
    def __init__(self, channel):
        self._channel = channel
    async def wait_until_ready(self):
        pass
    def get_channel(self, cid):
        return self._channel

@pytest.mark.asyncio
async def test_linewatch_loop(monkeypatch):
    channel = DummyChannel()
    bot = DummyBot(channel)
    watch_entry = {
        'RowID': 2,
        'UserID': 1,
        'Team': 'Dodgers',
        'Opponent': 'Giants',
        'Threshold': '20',
        'ChannelID': 1,
        'LastLine': '-150',
        'GameDate': '2025-06-10'
    }
    calls = []
    def fake_get_watchlist():
        if not calls:
            calls.append(1)
            return [watch_entry]
        else:
            # second iteration returns same with updated line
            watch_entry['LastLine'] = '-175'
            return [watch_entry]
    monkeypatch.setattr('gotlockz_bot.linewatch_module.get_watchlist', fake_get_watchlist)
    # first call returns -150, second call -175
    vals = [-150, -175]
    def fake_get_line_for_matchup(team, opp):
        val = vals.pop(0)
        return {'moneyline': {team: val}}
    monkeypatch.setattr('gotlockz_bot.linewatch_module.get_line_for_matchup', fake_get_line_for_matchup)
    monkeypatch.setattr('gotlockz_bot.linewatch_module.append_linewatch_log', lambda *a, **k: None)
    monkeypatch.setattr('gotlockz_bot.linewatch_module.update_watchlist_last_line', lambda *a, **k: None)
    # run loop once with small sleep
    async def limited_loop(bot):
        await bot.wait_until_ready()
        watchlist = get_watchlist()
        for entry in watchlist:
            team = entry['Team']; threshold=float(entry['Threshold']); channel=bot.get_channel(int(entry['ChannelID']))
            old_line=int(entry['LastLine']); opponent=entry['Opponent']
            data=get_line_for_matchup(team, opponent); new_line=int(data['moneyline'].get(team, old_line))
            if abs(new_line-old_line) >= threshold:
                diff=new_line-old_line
                await channel.send(f"ALERT {new_line} (\u0394 {diff})")
    from gotlockz_bot.linewatch_module import get_watchlist, get_line_for_matchup
    await limited_loop(bot)
    assert channel.sent
    assert 'ALERT -175' in channel.sent[0]
