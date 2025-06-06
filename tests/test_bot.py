import os
import sys

import pytest
import discord

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
import bot

class DummyUser:
    mention = "@tester"

class DummyResponse:
    def __init__(self):
        self.deferred = False
    async def defer(self, ephemeral=True):
        self.deferred = ephemeral

class DummyFollowup:
    def __init__(self):
        self.sent = None
    async def send(self, content, ephemeral=True):
        self.sent = (content, ephemeral)

class DummyInteraction:
    def __init__(self):
        self.user = DummyUser()
        self.response = DummyResponse()
        self.followup = DummyFollowup()

class DummyChannel:
    def __init__(self):
        self.content = None
        self.embed = None
        self.mention = "#channel"
    async def send(self, *, content=None, embed=None):
        self.content = content
        self.embed = embed

@pytest.mark.asyncio
async def test_postpick_sends_analysis_and_embed():
    interaction = DummyInteraction()
    channel = DummyChannel()
    await bot.postpick.callback(interaction, 2.5, "Test analysis", channel)

    assert channel.content == "Test analysis"
    assert isinstance(channel.embed, discord.Embed)
    assert "2.5" in channel.embed.description
    assert interaction.followup.sent[0].startswith("✅ Your pick")
