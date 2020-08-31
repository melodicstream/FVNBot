import asyncio
import datetime

import discord
from discord.ext import commands

from bot import FVNBot


class Staff(commands.Cog):
    """Staff-only commands for the bot."""

    def __init__(self, bot: FVNBot):
        self.bot = bot

    async def cog_check(self, ctx: commands.Context):
        return self.bot.roles["staff"] in ctx.author.roles

    @commands.command()
    async def status(self, ctx: commands.Context, *, status: str):
        """Changes the bot's status. Can only be used by the staff."""
        await self.bot.change_presence(activity=discord.Game(name=status))

    @commands.command()
    async def echo(self, ctx: commands.Context, channel: discord.TextChannel, *, message: str):
        """Echos any message in any channel of the server."""
        await channel.send(message)

    @commands.command()
    async def source(self, ctx: commands.Context, channel: discord.TextChannel, *, message: str):
        """This is the source code of the bot!"""
        await channel.send("https://github.com/melodicstream/FVNBot")

    @commands.command()
    async def backups(self, ctx: commands.Context, channel: discord.TextChannel, *, message: str):
        """This is the link for the database backups!"""
        await channel.send("https://github.com/melodicstream/FVNBot-backup")

    @commands.command()
    async def cleanup(self, ctx: commands.Context, limit=None):
        """Deletes the bot's messages for cleanup.
        You can specify how many messages to look for.
        """

        limit = limit or 10

        def is_me(m):
            return m.author.id == self.bot.user.id

        deleted = await ctx.channel.purge(limit=limit, check=is_me)
        await ctx.send(f"Deleted {len(deleted)} message(s)", delete_after=5)
        await self.bot.react_command_ok(ctx)

    @commands.command()
    async def uptime(self, ctx: commands.Context):
        """Tells you how long the bot has been up for."""

        now = datetime.datetime.utcnow()
        delta = now - self.bot.uptime
        hours, remainder = divmod(int(delta.total_seconds()), 3600)
        minutes, seconds = divmod(remainder, 60)
        days, hours = divmod(hours, 24)

        fmt = "{h}h {m}m {s}s"
        if days:
            fmt = "{d}d " + fmt

        await ctx.send(
            content="Uptime: {}".format(
                fmt.format(d=days, h=hours, m=minutes, s=seconds)
            )
        )

    @commands.command()
    async def bonk(self, ctx: commands.Context, member: discord.Member):
        """Bonks another person."""
        await ctx.send(
            f"{ctx.author.display_name} bonked user {member.display_name} <:bonk:711145599009030204>"
        )

    @commands.command()
    async def megabonk(self, ctx: commands.Context, member: discord.Member, amount: int = 1):
        """Megabonks another person."""

        bonk = """
<:bonk:711145599009030204><:bonk:711145599009030204>                <:bonk:711145599009030204>          <:bonk:711145599009030204>            <:bonk:711145599009030204>     <:bonk:711145599009030204>        <:bonk:711145599009030204>
<:bonk:711145599009030204>     <:bonk:711145599009030204>     <:bonk:711145599009030204>     <:bonk:711145599009030204>     <:bonk:711145599009030204><:bonk:711145599009030204>      <:bonk:711145599009030204>     <:bonk:711145599009030204>      <:bonk:711145599009030204>
<:bonk:711145599009030204><:bonk:711145599009030204>          <:bonk:711145599009030204>     <:bonk:711145599009030204>     <:bonk:711145599009030204>      <:bonk:711145599009030204><:bonk:711145599009030204>     <:bonk:711145599009030204><:bonk:711145599009030204>
<:bonk:711145599009030204>     <:bonk:711145599009030204>     <:bonk:711145599009030204>     <:bonk:711145599009030204>     <:bonk:711145599009030204>            <:bonk:711145599009030204>     <:bonk:711145599009030204>     <:bonk:711145599009030204>
<:bonk:711145599009030204><:bonk:711145599009030204>                <:bonk:711145599009030204>          <:bonk:711145599009030204>            <:bonk:711145599009030204>     <:bonk:711145599009030204>       <:bonk:711145599009030204>
        """

        def interactive_command_check(msg):
            return msg.author == member and ctx.channel == msg.channel

        await ctx.send(embed=discord.Embed(title="Raising the bonk hammer..."))

        for _ in range(amount):
            try:
                await self.bot.wait_for('message', timeout=120.0, check=interactive_command_check)
            except asyncio.TimeoutError:
                return

            await ctx.send(f"{member.mention}\n{bonk}")

        await ctx.send(embed=discord.Embed(title="Putting the hammer down and returning to normal operation."))


def setup(bot):
    bot.add_cog(Staff(bot))
