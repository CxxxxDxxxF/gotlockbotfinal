import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

import discord
import bot
import pytest
import asyncio


class DummyResponse:
    async def defer(self, ephemeral=True):
        self.ephemeral = ephemeral


class DummyFollowup:
    def __init__(self):
        self.sent = []

    async def send(self, *args, **kwargs):
        self.sent.append((args, kwargs))


class DummyInteraction:
    def __init__(self):
        self.response = DummyResponse()
        self.followup = DummyFollowup()


class DummyAttachment:
    def __init__(self, filename: str):
        self.filename = filename

    async def save(self, path: str):
        with open(path, "w") as f:
            f.write("data")


def test_postpick_command_registered():
    guild = discord.Object(id=bot.GUILD_ID)
    cmds = {cmd.name: cmd for cmd in bot.tree.get_commands(guild=guild)}
    assert "postpick" in cmds
    command = cmds["postpick"]
    param_names = [p.name for p in command.parameters]
    assert param_names == ["units", "channel"]


def test_analyze_bet_file_cleanup(monkeypatch):
    interaction = DummyInteraction()
    attachment = DummyAttachment("cleanup.txt")

    monkeypatch.setattr(bot, "extract_text_from_image", lambda p: "text")
    monkeypatch.setattr(bot, "parse_bet_details", lambda t: {})
    monkeypatch.setattr(bot, "generate_analysis", lambda d: "analysis")

    asyncio.run(bot.analyze_bet.callback(interaction, attachment))

    assert not os.path.exists(f"/tmp/{attachment.filename}")


def test_ping_command(monkeypatch):
    interaction = DummyInteraction()
    monkeypatch.setattr(
        discord.ext.commands.Bot,
        "latency",
        property(lambda self: 0.123),
    )

    asyncio.run(bot.ping.callback(interaction))

    assert interaction.response.ephemeral
    args, kwargs = interaction.followup.sent[0]
    assert args[0].startswith("Pong!")
    assert kwargs["ephemeral"] is True
