import asyncio
import datetime
import logging
import random
import traceback

import discord
from discord.ext import commands

log = logging.getLogger(__name__)


class FVNBot(commands.Bot):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.uptime = datetime.datetime.utcnow()
        self.config = kwargs["config"]
        self.custom_extensions = self.config["extensions"]
        self.guild = None
        self.channels = None
        self.roles = None
        self.log = log

        for extension in self.custom_extensions:
            try:
                self.load_extension(extension)
            except Exception as e:  # noqa
                log.error(
                    "Failed to load extension %s\n%s: %s",
                    extension,
                    type(e).__name__,
                    e,
                )

    async def on_ready(self):
        log.info("Logged in as %s", self.user)

        await self.change_presence(activity=discord.Game(name="vn.help"))

        self.guild = self.get_guild(self.config["guild_id"])

        self.channels = {
            "vn_list": self.guild.get_channel(self.config["channels"]["vn_list"]),
            "vn_undetermined": self.guild.get_channel(self.config["channels"]["vn_undetermined"]),
            "vn_news": self.guild.get_channel(self.config["channels"]["vn_news"]),
            "top10": self.guild.get_channel(self.config["channels"]["top10"]),
            "logs": self.guild.get_channel(self.config["channels"]["logs"]),
            "bot_spam": self.guild.get_channel(self.config["channels"]["bot_spam"]),
        }

        self.roles = {
            "staff": self.guild.get_role(self.config["roles"]["staff"]),
        }

    async def on_command(self, ctx):
        await self.channels["logs"].send(f"{ctx.author} in #{ctx.channel}: {ctx.message.content}")

    async def on_command_error(self, ctx: commands.Context, error):
        tb = "".join(
            traceback.format_exception(type(error), error, error.__traceback__)
        )
        if not isinstance(error, commands.CommandNotFound):
            await self.channels["logs"].send(f"Command error in {ctx.command}:\n{tb}")
        if isinstance(error, (commands.ConversionError, asyncio.TimeoutError)):
            await self.react_command_error(ctx)
            await ctx.send(str(error))
        if isinstance(error, commands.CheckFailure):
            await self.react_command_error(ctx)
            if random.random() <= 0.25:
                sarcasm = [
                    "You really think you can do this?",
                    "Pffft. Try again in another lifetime.",
                    "I was told to say something sarcastic.",
                    "Please don't try this command again. It hurts me :(",
                    "Nope. You can't do that. If you try that again, you get the banana pizza.",
                    "Nope, not listening to you.",
                    "Do you really think you can do this? <:nekolinhu:658757071268872202>",
                    "You're not my master!",
                    "You're not my dad! Where is my dad!?",
                    "Keep this up and I'll bonk you! <:bonk:711145599009030204>",
                    "I'm telling Nathan!",
                ]
                await ctx.send(random.choice(sarcasm))

    @staticmethod
    async def react_command_ok(ctx):
        await ctx.message.add_reaction("👌")

    @staticmethod
    async def react_command_error(ctx):
        await ctx.message.add_reaction("❌")
