import types
import pytest

from gotlockz_bot.discord_commands import postpick

class DummyAttachment:
    def __init__(self, url):
        self.url = url

class DummyMessage:
    def __init__(self):
        self.attachments = [DummyAttachment('http://example.com/img.png')]
        from datetime import datetime
        self.created_at = datetime.utcnow()

class DummyChannel:
    def __init__(self):
        self.sent = []
    async def send(self, *args, **kwargs):
        self.sent.append((args, kwargs))

class DummyCtx:
    def __init__(self):
        self.message = DummyMessage()
        self.channel = DummyChannel()
    async def reply(self, *args, **kwargs):
        self.channel.sent.append(('reply', args, kwargs))

@pytest.mark.asyncio
async def test_postpick(monkeypatch):
    ctx = DummyCtx()
    # monkeypatch dependencies
    async def fake_download(url):
        # create temp file
        import tempfile
        p = tempfile.NamedTemporaryFile(delete=False, suffix='.txt')
        p.write(b'NYY ML -150')
        p.close()
        return p.name
    monkeypatch.setattr('gotlockz_bot.discord_commands.download_attachment', fake_download)
    monkeypatch.setattr('gotlockz_bot.discord_commands.image_to_text', lambda x: 'NYY ML -150')
    monkeypatch.setattr('gotlockz_bot.discord_commands.parse_bets_from_text', lambda t: [{"teamA": "New York Yankees", "line": "ML", "odds": -150}])
    monkeypatch.setattr('gotlockz_bot.discord_commands.get_today_schedule', lambda: {"New York Yankees vs Boston Red Sox": {}})
    monkeypatch.setattr('gotlockz_bot.discord_commands.get_team_metrics', lambda team: {"probable_starter": None})
    monkeypatch.setattr('gotlockz_bot.discord_commands.get_last_five_stats', lambda x: {})
    monkeypatch.setattr('gotlockz_bot.discord_commands.call_openai', lambda prompt: "analysis")
    monkeypatch.setattr('gotlockz_bot.discord_commands.append_pick_to_sheet', lambda *a, **k: None)
    monkeypatch.setattr('gotlockz_bot.discord_commands.get_count_of_type', lambda *a, **k: 0)
    await postpick(ctx, 3)
    assert ctx.channel.sent
    title = ctx.channel.sent[0][1]['embed'].title if isinstance(ctx.channel.sent[0][1]['embed'], types.SimpleNamespace) else ctx.channel.sent[0][1]['embed'].title
    assert 'VIP PLAY #1' in title
