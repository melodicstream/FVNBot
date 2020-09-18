import asyncio
import datetime
import logging
import os
import random

import discord
from discord.ext import commands

log = logging.getLogger(__name__)


def env_int(name: str) -> int:
    return int(os.getenv(name))


class FVNBot(commands.Bot):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.uptime = datetime.datetime.utcnow()
        self.custom_extensions = [
            "bot.cogs.bot_manager",
            "bot.cogs.visual_novels"
        ]
        self.guild = None
        self.channels = None
        self.roles = None
        self.database_path = os.getenv("FVNBOT_DATABASE")
        self.log = log

        for extension in self.custom_extensions:
            try:
                self.load_extension(extension)
            except Exception as e:  # noqa
                log.error("Failed to load extension %s\n%s: %s", extension, type(e).__name__, e)

    async def on_ready(self):
        log.info("Logged in as %s", self.user)

        await self.change_presence(activity=discord.Game(name=f"{os.getenv('FVNBOT_PREFIX')}help"))

        self.guild = self.get_guild(env_int("FVNBOT_GUILD_ID"))

        self.channels = {
            "vn_list": self.guild.get_channel(env_int("FVNBOT_CHANNEL_VN_LIST")),
            "vn_undetermined": self.guild.get_channel(env_int("FVNBOT_CHANNEL_VN_UNDETERMINED")),
            "vn_news": self.guild.get_channel(env_int("FVNBOT_CHANNEL_VN_NEWS")),
            "top10": self.guild.get_channel(env_int("FVNBOT_CHANNEL_TOP10")),
            "logs": self.guild.get_channel(env_int("FVNBOT_CHANNEL_LOGS")),
            "bot_spam": self.guild.get_channel(env_int("FVNBOT_CHANNEL_BOT_SPAM")),
        }

        self.roles = {
            "staff": self.guild.get_role(env_int("FVNBOT_ROLE_STAFF")),
            "bot_manager": self.guild.get_role(env_int("FVNBOT_ROLE_BOT_MANAGER")),
            "update_notification": self.guild.get_role(env_int("FVNBOT_ROLE_UPDATE_NOTIFICATION")),
        }

    async def on_command(self, ctx):
        await self.channels["logs"].send(f"{ctx.author} in #{ctx.channel}: {ctx.message.content}")

    async def on_command_error(self, ctx: commands.Context, error):
        await self.react_command_error(ctx)
        if not isinstance(error, commands.CommandNotFound) and ctx.command not in ["bonk", "megabonk"]:
            await self.channels["logs"].send(f"Command error in {ctx.command}: {error}")
        if isinstance(error, (commands.ConversionError, asyncio.TimeoutError)):
            await ctx.send(str(error))
        if isinstance(error, commands.CheckFailure) and random.random() <= 0.4:
            sarcasm = [
                "Nope, not listening to you.",
                "Do you really think you can do this? <:nekolinhu:658757071268872202>",
                "You're not my master!",
                "Shiiiiin, they're trying to use the bot commands agaaaain <:pleaseno:694998032457924698>",
                "You're not my dad! Where is my dad!?",
                "Keep this up and I'll bonk you! <:bonk:711145599009030204>",
                "You can't do this!",
                "I was told to say something sarcastic.",
                "Command usage not authorized. This incident will be reported to Santa Claus.",
                "Are you sure you should be doing this? <:bonk:756470696304967731>",
                "I'm calling Chase next time!",
                "I'm calling Shin next time!",
                "<:squint:756472317680549919>",
                "Nope!",
                "Please don't use commands you're not supposed to...",
                "I'm telling the cops! <@154594175008899072>",
            ]
            await ctx.send(random.choice(sarcasm))

    async def on_command_completion(self, ctx: commands.Context):
        await self.react_command_ok(ctx)

    @staticmethod
    async def react_command_ok(ctx):
        await ctx.message.clear_reactions()
        await ctx.message.add_reaction("👌")

    @staticmethod
    async def react_command_error(ctx):
        await ctx.message.clear_reactions()
        await ctx.message.add_reaction("❌")
