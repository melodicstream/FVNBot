import asyncio
import datetime
import io
import json
import random

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
    async def embedpost(self, ctx: commands.Context, channel: discord.TextChannel):
        """Posts an embed to a certain channel."""

        file = await ctx.message.attachments[0].to_file()
        embed = discord.Embed.from_dict(json.load(file.fp))
        await channel.send(embed=embed)

    @commands.command()
    async def embedget(self, ctx: commands.Context, channel: discord.TextChannel, message_id: int):
        """Gets an embed from a certain channel and message.

        Returned in JSON format.
        """

        message = await channel.fetch_message(message_id)
        embed = message.embeds[0]

        with io.StringIO() as f:
            content = json.dumps(embed.to_dict(), sort_keys=True, indent=4)
            f.write(content)
            f.seek(0)
            file = discord.File(f, filename="embedget.txt")
            await ctx.send(file=file)

    @commands.command()
    async def embededit(self, ctx: commands.Context, channel: discord.TextChannel, message_id: int):
        """Edits an already existing embed via JSON format."""

        file = await ctx.message.attachments[0].to_file()
        embed = discord.Embed.from_dict(json.load(file.fp))

        message = await channel.fetch_message(message_id)
        await message.edit(embed=embed)

    @commands.command()
    async def bonk(self, ctx: commands.Context, member: discord.Member):
        """Bonks another person."""

        if member.id == 154594175008899072:
            return await self._dont_bonk_shin(ctx)

        await ctx.send(
            f"{ctx.author.display_name} bonked {member.display_name}!   <:bonk:711145599009030204>"
        )

        if member.id == 129819557115199488 and random.random() < 0.2:
            return await self._dont_bonk_melo(ctx)

    @commands.command()
    async def megabonk(self, ctx: commands.Context, member: discord.Member, amount: int = 1):
        """Megabonks another person."""

        if member.id == 154594175008899072:
            return await self._dont_bonk_shin(ctx)

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
                await self.bot.wait_for('message', timeout=60.0 * 10, check=interactive_command_check)
            except asyncio.TimeoutError:
                return

            await ctx.send(f"{member.mention}\n{bonk}")

        await ctx.send(embed=discord.Embed(title="Putting the hammer down and returning to normal operation."))

        if member.id == 129819557115199488 and random.random() < 0.2:
            return await self._dont_bonk_melo(ctx)

    async def _dont_bonk_shin(self, ctx: commands.Context):
        await self.bot.react_command_error(ctx)

        messages = [
            "I... I can't do this!",
            "I refuse!",
            "I can't hurt Shin!",
            "H-He's my dad!",
            "Well that's not a nice thing to ask...",
        ]
        await ctx.send(random.choice(messages))

    async def _dont_bonk_melo(self, ctx: commands.Context):
        messages = [
            "There. Are you happy now? YOU FUCKING OBLITERATED THE MELO!!!",
            "Melo's just a poor boy from a poor family! Spare his head from this monstrosity!",
            "Maybe if we bonk Melo enough he'll forget that banana pizza was ever a thing...",
            "Uh... is it normal if his head has a slight dent after the bonk?",
            "This bonk made a different sound than the others... Better bonk again to make sure!",
        ]
        await ctx.send(random.choice(messages))


def setup(bot):
    bot.add_cog(Staff(bot))
