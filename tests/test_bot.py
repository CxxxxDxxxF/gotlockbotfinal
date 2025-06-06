import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

import discord
import bot


def test_postpick_command_registered():
    guild = discord.Object(id=bot.GUILD_ID)
    cmds = {cmd.name: cmd for cmd in bot.tree.get_commands(guild=guild)}
    assert "postpick" in cmds
    command = cmds["postpick"]
    param_names = [p.name for p in command.parameters]
    assert param_names == ["units", "channel"]
