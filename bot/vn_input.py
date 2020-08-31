import asyncio


async def input_name(bot, ctx, check):
    await ctx.send("What's the name of the VN?")

    try:
        name = await bot.wait_for('message', timeout=60.0, check=check)
        return name.content
    except asyncio.TimeoutError:
        return await ctx.send('You took long. Aborting.')


async def input_abbreviations(bot, ctx, check):
    await ctx.send("What are the abbreviations that this VN will be known for? Enter them separated by spaces. If there are no abbreviations, type \"none\"")

    try:
        abbreviations = await bot.wait_for('message', timeout=60.0, check=check)

        if abbreviations.content.strip().lower() == "none":
            return []

        return [abbreviation.lower() for abbreviation in abbreviations.content.split()]
    except asyncio.TimeoutError:
        return await ctx.send('You took long. Aborting.')


async def input_authors(bot, ctx, check):
    await ctx.send("Who are the owners of this VN? Enter their names separated by commas.")

    try:
        authors = await bot.wait_for('message', timeout=60.0, check=check)
        return [author.strip() for author in authors.content.split(",")]
    except asyncio.TimeoutError:
        return await ctx.send('You took long. Aborting.')


async def input_store(bot, ctx, check):
    await ctx.send("What is the store link? (itch.io, Steam, etc)")

    try:
        store = await bot.wait_for('message', timeout=60.0, check=check)
        return store.content
    except asyncio.TimeoutError:
        return await ctx.send('You took long. Aborting.')


async def input_image(bot, ctx, check):
    await ctx.send("Please upload an image to use as a preview")

    try:
        image = await bot.wait_for('message', timeout=60.0, check=check)
        return image.attachments[0].url
    except asyncio.TimeoutError:
        return await ctx.send('You took long. Aborting.')


async def input_android_support(bot, ctx, check):
    await ctx.send("Does this VN work on Android phones? Type yes or no.")

    try:
        android = await bot.wait_for('message', timeout=60.0, check=check)
        return "yes" in android.content
    except asyncio.TimeoutError:
        return await ctx.send('You took long. Aborting.')


async def input_undetermined(bot, ctx, check):
    await ctx.send("Is it an undetermined VN? Type yes or no.")

    try:
        undetermined = await bot.wait_for('message', timeout=60.0, check=check)
        return "yes" in undetermined.content
    except asyncio.TimeoutError:
        return await ctx.send('You took long. Aborting.')
