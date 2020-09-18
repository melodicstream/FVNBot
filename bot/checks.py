from discord.ext import commands


def check_is_staff(ctx: commands.Context):
    if ctx.guild is None:
        return False

    return ctx.bot.roles["staff"] in ctx.author.roles


def check_is_bot_manager(ctx: commands.Context):
    if ctx.guild is None:
        return False

    return ctx.bot.roles["bot_manager"] in ctx.author.roles


def check_in_botspam(ctx: commands.Context):
    if ctx.guild is None:
        return False

    return ctx.bot.channels["bot_spam"] == ctx.channel
