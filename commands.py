import discord
from discord import app_commands


def register_commands(tree: app_commands.CommandTree, guild_id: int):
    """Register application commands on the provided command tree."""

    @tree.command(
        name="postpick",
        description="Register a pick and post it to your chosen channel",
        guild=discord.Object(id=guild_id),
    )
    @app_commands.describe(
        units="How many units (e.g. 1.0) to wager on this pick",
        channel="Which channel to post the pick in",
    )
    async def postpick(
        interaction: discord.Interaction, units: float, channel: discord.TextChannel
    ):
        """/postpick handler."""
        await interaction.response.defer(ephemeral=True)
        embed = discord.Embed(
            title="\U0001F4E3 New Pick Posted!",
            description=f"**Units:** {units}\n**Picked by:** {interaction.user.mention}",
        )
        embed.set_footer(text="Good luck! \U0001F340")
        await channel.send(embed=embed)
        await interaction.followup.send(
            f"\u2705 Your pick of **{units} units** has been posted in {channel.mention}.",
            ephemeral=True,
        )

    return postpick
