import asyncio
from collections import Counter

import discord
from discord.ext import commands
from tinydb import TinyDB, Query, where

from bot import FVNBot
from bot.helpers import VisualNovel, TABLE_VISUAL_NOVEL, TABLE_RATING
from bot.vn_input import input_name, input_abbreviations, input_undetermined, input_android_support, input_image, \
    input_store, input_authors


def check_is_staff(ctx: commands.Context):
    if ctx.guild is None:
        return False

    return ctx.bot.roles["staff"] in ctx.author.roles


class VisualNovels(commands.Cog):
    """Commands related to managing VNs."""

    def __init__(self, bot: FVNBot):
        self.bot = bot
        self.db = TinyDB(self.bot.config["database"], sort_keys=True, indent=4, separators=(",", ": "))

    @commands.command()
    async def search(self, ctx: commands.Context, *, name: str):
        """Search for a Visual Novel by name or abbreviation."""

        name = name.lower()

        vn = VisualNovel(database=self.db)

        try:
            vn.load_from_db(name=name, abbreviations=[name])
        except FileNotFoundError:
            return await ctx.send("VN not found.")

        channel = self.bot.channels["vn_undetermined" if vn.undetermined else "vn_list"]
        message = await channel.fetch_message(vn.message_id)
        await ctx.send(f"The VN {vn.name} can be found at {message.jump_url}")

    @commands.command()
    @commands.check(check_is_staff)
    async def add(self, ctx: commands.Context):
        """Interactively add a Visual Novel to the database."""

        def interactive_command_check(msg):
            return msg.author == ctx.author and ctx.channel == msg.channel

        name = await input_name(self.bot, ctx, interactive_command_check)
        abbreviations = await input_abbreviations(self.bot, ctx, interactive_command_check)
        authors = await input_authors(self.bot, ctx, interactive_command_check)
        store = await input_store(self.bot, ctx, interactive_command_check)
        image = await input_image(self.bot, ctx, interactive_command_check)
        android = await input_android_support(self.bot, ctx, interactive_command_check)
        undetermined = await input_undetermined(self.bot, ctx, interactive_command_check)

        vn = VisualNovel(
            database=self.db,
            name=name,
            abbreviations=abbreviations,
            authors=authors,
            store=store,
            image=image,
            android_support=android,
            undetermined=undetermined,
        )

        doc_id = vn.add_to_db()
        self.bot.log.info("VN added to DB with ID %s", doc_id)

        await vn.post_to_list(self.bot.channels)

        await ctx.send("VN added successfully!")

    @commands.command()
    @commands.check(check_is_staff)
    async def edit(self, ctx: commands.Context):
        """Edits the information about a VN."""

        def interactive_command_check(msg):
            return msg.author == ctx.author and ctx.channel == msg.channel

        await ctx.send("What VN do you want to edit? Enter a name or an abbreviation.")

        try:
            vn_name = await self.bot.wait_for('message', timeout=60.0, check=interactive_command_check)
        except asyncio.TimeoutError:
            return await ctx.send('You took long. Aborting.')

        vn_name = vn_name.content.lower()
        vn = VisualNovel(database=self.db)
        try:
            vn.load_from_db(name=vn_name, abbreviations=[vn_name])
        except FileNotFoundError:
            return await ctx.send("VN not found.")

        await ctx.send("""What do you want to edit about the VN? Input the corresponding number.
        1. Name
        2. Abbreviations
        3. Authors
        4. Store Link
        5. Image
        6. Android Support
        7. Is undetermined?
        """)

        try:
            choice = await self.bot.wait_for('message', timeout=60.0, check=interactive_command_check)
        except asyncio.TimeoutError:
            return await ctx.send('You took long. Aborting.')
        choice = int(choice.content.strip())

        if choice == 1:
            vn.name = await input_name(self.bot, ctx, interactive_command_check)
        if choice == 2:
            vn.abbreviations = await input_abbreviations(self.bot, ctx, interactive_command_check)
        if choice == 3:
            vn.authors = await input_authors(self.bot, ctx, interactive_command_check)
        if choice == 4:
            vn.store = await input_store(self.bot, ctx, interactive_command_check)
        if choice == 5:
            vn.image = await input_image(self.bot, ctx, interactive_command_check)
        if choice == 6:
            vn.android_support = await input_android_support(self.bot, ctx, interactive_command_check)
        if choice == 7:
            vn.undetermined = await input_undetermined(self.bot, ctx, interactive_command_check)

        vn.update_to_db()
        await vn.update_to_list(self.bot.channels)

        await ctx.send("VN updated successfully.")

    @commands.command()
    @commands.check(check_is_staff)
    async def rebuild(self, ctx: commands.Context):
        """Reposts all the VNs again in the VN channels."""

        async for message in self.bot.channels["vn_undetermined"].history(limit=None):
            await message.delete()

        async for message in self.bot.channels["vn_list"].history(limit=None):
            await message.delete()

        for entry in self.db.table(TABLE_VISUAL_NOVEL).all():
            vn = VisualNovel(database=self.db)
            vn.load_from_db(doc_id=entry.doc_id)
            await vn.post_to_list(self.bot.channels)

        await self.bot.react_command_ok(ctx)

    @commands.command()
    @commands.check(check_is_staff)
    async def migrate(self, ctx: commands.Context):
        """Migrate the votes from the old lists."""

        def interactive_command_check(msg):
            return msg.author == ctx.author and ctx.channel == msg.channel

        await ctx.send("What VN do you want to migrate? Enter a name or an abbreviation.")

        try:
            vn_name = await self.bot.wait_for('message', timeout=60.0, check=interactive_command_check)
        except asyncio.TimeoutError:
            return await ctx.send('You took long. Aborting.')

        vn_name = vn_name.content.lower()
        vn = VisualNovel(database=self.db)
        try:
            vn.load_from_db(name=vn_name, abbreviations=[vn_name])
        except FileNotFoundError:
            return await ctx.send("VN not found.")

        await ctx.send("Please enter the ID of the message with the original votes.")

        try:
            original_votes_message_id = await self.bot.wait_for('message', timeout=60.0,
                                                                check=interactive_command_check)
        except asyncio.TimeoutError:
            return await ctx.send('You took long. Aborting.')

        original_votes_message_id = int(original_votes_message_id.content)

        old_vn_undetermined = self.bot.guild.get_channel(488386154882793473)
        old_vn_list = self.bot.guild.get_channel(479777207934517275)

        try:
            message = await old_vn_undetermined.fetch_message(original_votes_message_id)
        except:
            message = await old_vn_list.fetch_message(original_votes_message_id)

        shin_id = 154594175008899072
        Rating = Query()

        for reaction in message.reactions:
            async for user in reaction.users():
                if user.id == shin_id:
                    continue
                query = (Rating.member_id == user.id) & (Rating.vn_id == vn.doc_id)
                if reaction.emoji == "👍":
                    self.db.table(TABLE_RATING).upsert({"member_id": user.id, "vn_id": vn.doc_id, "rating": 1}, query)
                if reaction.emoji == "👎":
                    self.db.table(TABLE_RATING).upsert({"member_id": user.id, "vn_id": vn.doc_id, "rating": -1}, query)

        await ctx.send("VN's votes successfully migrated.")

    @commands.command()
    async def votes(self, ctx: commands.Context, member: discord.Member = None):
        """Shows the list of all the VNs that the member voted for.
        If not given any member, it shows the list of whoever called the command.
        """

        member = member or ctx.author

        upvoted = []
        downvoted = []

        for doc in self.db.table(TABLE_RATING).search(where("member_id") == member.id):
            name = self.db.table(TABLE_RATING).get(doc_id=doc["vn_id"])["name"]
            if doc["rating"] == 1:
                upvoted.append(f"{name}")
            else:
                downvoted.append(f"{name}\n")

        message = "```Upvoted```\n{}\n```Downvoted```\n{}".format("\n".join(upvoted), "\n".join(downvoted))

        await ctx.send(message)

    @commands.command()
    @commands.check(check_is_staff)
    async def cleanleavers(self, ctx: commands.Context):
        """Removes the votes from people that aren't in the server anymore."""

        to_remove = [
            document["member_id"]
            for document in self.db.table(TABLE_RATING).all()
            if not self.bot.guild.get_member(document["member_id"])
        ]

        self.db.table(TABLE_RATING).remove(doc_ids=to_remove)

        await ctx.send(f"{len(to_remove)} leavers removed from the votes! Don't forget to run the `rebuild` command.")

    @commands.command()
    @commands.check(check_is_staff)
    async def generatetop10(self, ctx: commands.Context):
        """Posts the top 10 list of VNs by rating.
        Generates a list of the top 10 VNs in absolute ranks (ups minus downs), clears the top 10 channel and posts the
        new VNs in the channel, sorted by rating.
        """

        return await ctx.send("Currently unimplemented.")

        counter = Counter()

        for doc in self.db.table(TABLE_RATING).all():
            counter[doc["vn_id"]] += doc["rating"]

        top_10 = counter.most_common(10)

        for vn_id, rating in top_10:
            pass

    @commands.command()
    @commands.check(check_is_staff)
    async def update(self, ctx: commands.Context):
        """Posts a VN update in the VN News Channel."""

        def interactive_command_check(msg):
            return msg.author == ctx.author and ctx.channel == msg.channel

        await ctx.send("What VN do you want to publish an update? Enter a name or an abbreviation.")

        try:
            vn_name = await self.bot.wait_for('message', timeout=60.0, check=interactive_command_check)
        except asyncio.TimeoutError:
            return await ctx.send('You took long. Aborting.')

        vn_name = vn_name.content.lower()
        vn = VisualNovel(database=self.db)
        try:
            vn.load_from_db(name=vn_name, abbreviations=[vn_name])
        except FileNotFoundError:
            return await ctx.send("VN not found.")

        await ctx.send("What is the URL to the update?")

        try:
            url = await self.bot.wait_for('message', timeout=60.0, check=interactive_command_check)
        except asyncio.TimeoutError:
            return await ctx.send('You took long. Aborting.')
        url = url.content

        await ctx.send("What is the title of the update?")

        try:
            title = await self.bot.wait_for('message', timeout=60.0, check=interactive_command_check)
        except asyncio.TimeoutError:
            return await ctx.send('You took long. Aborting.')
        title = title.content

        embed = discord.Embed(
            colour=discord.Colour.blurple(),
            title=f"{vn.name}: {title}",
            url=url,
        )
        embed.add_field(name="Current Ratings", value=vn.calculate_ratings())
        embed.add_field(name="Abbreviations", value=vn.pretty_abbreviations())
        embed.add_field(name="Android Support", value="Yes" if vn.android_support else "No")
        embed.set_author(name="FVN Bot", icon_url="https://media.discordapp.net/attachments/729276573496246304/747178571834982431/bonkshinbookmirrored.png")
        embed.set_footer(text=f"Brought to you by Furry Visual Novels server. Join us for vn-lists, development channels and more. discord.gg/GFjSPkh")

        msg = await self.bot.channels["vn_news"].send("<@&622819741702160387>", embed=embed)
        await msg.publish()

    @commands.Cog.listener()
    async def on_raw_reaction_add(self, payload):
        channel_id = payload.channel_id
        message_id = payload.message_id
        member = payload.member
        emoji = payload.emoji

        if member == self.bot.user:
            return

        channel = None

        if channel_id == self.bot.channels["vn_list"].id:
            channel = self.bot.channels["vn_list"]

        if channel_id == self.bot.channels["vn_undetermined"].id:
            channel = self.bot.channels["vn_undetermined"]

        if not channel:
            return

        message = await channel.fetch_message(message_id)
        await message.remove_reaction(emoji, member)

        vn = VisualNovel(database=self.db)
        vn.load_from_db(message_id=message_id)

        Rating = Query()
        query = (Rating.member_id == member.id) & (Rating.vn_id == vn.doc_id)

        if emoji.name == "👍":
            self.db.table(TABLE_RATING).upsert({"member_id": member.id, "vn_id": vn.doc_id, "rating": 1}, query)

        if emoji.name == "👎":
            self.db.table(TABLE_RATING).upsert({"member_id": member.id, "vn_id": vn.doc_id, "rating": -1}, query)

        if emoji.name == "❌":
            self.db.table(TABLE_RATING).remove(query)

        await vn.update_entry_ratings(message)

    async def cog_command_error(self, ctx: commands.Context, error):
        await ctx.message.clear_reactions()
        await self.bot.react_command_error(ctx)


def setup(bot):
    bot.add_cog(VisualNovels(bot))
