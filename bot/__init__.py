import datetime
import logging
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

        await self.change_presence(activity=discord.Game(name="?help"))

        self.guild = self.get_guild(self.config["guild_id"])

        self.channels = {
            "logs": self.guild.get_channel(self.config["channels"]["logs"]),
            "vn_list": self.guild.get_channel(self.config["channels"]["vn_list"]),
            "vn_undetermined": self.guild.get_channel(self.config["channels"]["vn_undetermined"]),
            "vn_news": self.guild.get_channel(self.config["channels"]["vn_news"]),
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
            log.error("Command error in %s:\n%s", ctx.command, tb)
            await self.channels["logs"].send(f"Command error in {ctx.command}:\n{tb}")
        if isinstance(error, (commands.CheckFailure, commands.ConversionError)):
            await self.react_command_error(ctx)
            await ctx.send(str(error))

    @staticmethod
    async def react_command_ok(ctx):
        await ctx.message.add_reaction("👌")

    @staticmethod
    async def react_command_error(ctx):
        await ctx.message.add_reaction("❌")
