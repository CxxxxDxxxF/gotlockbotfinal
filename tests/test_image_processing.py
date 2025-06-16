import pytest
import os
import asyncio
from types import SimpleNamespace

import bot
from bot import postpick

# --- Dummy classes to simulate Discord objects ---
class DummyAttachment:
    def __init__(self, filename):
        self.filename = filename
        self.saved_path = None

    async def save(self, path):
        # Simulate saving the file by recording the path
        self.saved_path = path
        # Create an empty file to satisfy cleanup logic
        open(path, 'wb').close()

class DummyChannel:
    def __init__(self):
        self.sent_messages = []

    async def send(self, content):
        self.sent_messages.append(content)

class DummyFollowup:
    def __init__(self):
        self.messages = []

    async def send(self, content, ephemeral=False):
        self.messages.append((content, ephemeral))

class DummyResponse:
    def __init__(self):
        self.deferred = False

    async def defer(self, ephemeral=False):
        self.deferred = True

class DummyInteraction:
    def __init__(self, channel):
        self.channel = channel
        self.response = DummyResponse()
        self.followup = DummyFollowup()

# Mark async tests
@pytest.mark.asyncio
async def test_postpick_happy_path(monkeypatch, tmp_path):
    # Prepare dummy attachment and channel
    attachment = DummyAttachment('slip.png')
    channel = DummyChannel()
    interaction = DummyInteraction(channel)

    # Monkey-patch save logic
    monkeypatch.setattr(bot, 'async_save_attachment', lambda att, path: attachment.save(path))
    # Monkey-patch OCR and parsing
    sample_details = {'game': 'Alpha @ Beta', 'bet': 'Alpha – Moneyline', 'odds': '+120'}
    monkeypatch.setattr(bot, 'extract_text_from_image', lambda path: 'ignored')
    monkeypatch.setattr(bot, 'parse_bet_details', lambda text: sample_details)
    # Monkey-patch analysis generation
    monkeypatch.setattr(bot, 'generate_analysis', lambda details: asyncio.Future())
    fut = asyncio.Future()
    fut.set_result('PERFECT ANALYSIS')
    monkeypatch.setattr(bot, 'generate_analysis', lambda details: fut)

    # Call the command
    await postpick.callback(interaction, units=2.5, channel=channel, image=attachment)

    # Ensure the bot deferred the response
    assert interaction.response.deferred is True
    # Ensure followup success message
    assert ('✅ VIP pick posted successfully.', True) in interaction.followup.messages
    # Ensure channel.send was called with the composed message
    assert len(channel.sent_messages) == 1
    sent = channel.sent_messages[0]
    assert 'VIP PLAY #1' in sent
    assert 'Alpha @ Beta' in sent
    assert 'Alpha – Moneyline' in sent
    assert '+120' in sent
    assert '2.5' in sent
    assert 'PERFECT ANALYSIS' in sent

@pytest.mark.asyncio
async def test_postpick_bad_units(monkeypatch):
    # Setup dummy interaction and channel
    attachment = DummyAttachment('slip.png')
    channel = DummyChannel()
    interaction = DummyInteraction(channel)

    # Call with invalid units
    await postpick.callback(interaction, units=0, channel=channel, image=attachment)

    # Should not defer, but send an ephemeral error
    assert interaction.followup.messages[0][0] == '❌ Units must be greater than zero.'
    assert interaction.followup.messages[0][1] is True
