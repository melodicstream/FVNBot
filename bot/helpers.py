import re

import discord
from tinydb import Query, where

TABLE_VISUAL_NOVEL = "visual_novel"
TABLE_RATING = "rating"


class VisualNovel:
    def __init__(self, *, database, name=None, undetermined=None, android_support=None, image=None, store=None,
                 authors=None, abbreviations=None):
        self.db = database
        self.doc_id = None
        self.name = name
        self.abbreviations = abbreviations
        self.authors = authors
        self.store = store
        self.image = image
        self.android_support = android_support
        self.undetermined = undetermined
        self.message_id = None

    async def post_to_list(self, channel_list):
        embed = discord.Embed(
            colour=discord.Colour.blurple(),
            title=self.name,
            url=self.store,
        )

        embed.add_field(name="Current Ratings", value=self.calculate_ratings())
        embed.add_field(name="Abbreviations", value=self.pretty_abbreviations())
        embed.add_field(name="Android Support", value="Yes" if self.android_support else "No")
        embed.set_image(url=self.image)
        embed.set_author(name="FVN Bot", icon_url="https://media.discordapp.net/attachments/729276573496246304/747178571834982431/bonkshinbookmirrored.png")
        embed.set_footer(text=f"{self.name}, by {', '.join(self.authors)}")

        channel = channel_list["vn_undetermined" if self.undetermined else "vn_list"]

        message = await channel.send(embed=embed)
        await message.add_reaction("👍")
        await message.add_reaction("👎")
        await message.add_reaction("❌")

        if self.doc_id:
            self.db.table(TABLE_VISUAL_NOVEL).update({"message_id": message.id}, doc_ids=[self.doc_id])
        else:
            raise Exception("VN database ID not found before saving to list.")

    async def update_to_list(self, channel_list):
        try:
            channel = channel_list["vn_undetermined" if self.undetermined else "vn_list"]
            message = await channel.fetch_message(self.message_id)

            embed = message.embeds[0]

            embed.add_field(name="Current Ratings", value=self.calculate_ratings())
            embed.add_field(name="Abbreviations", value=self.pretty_abbreviations())
            embed.add_field(name="Android Support", value="Yes" if self.android_support else "No")
            embed.set_image(url=self.image)
            embed.set_author(name="FVN Bot", icon_url="https://media.discordapp.net/attachments/729276573496246304/747178571834982431/bonkshinbookmirrored.png")
            embed.set_footer(text=f"{self.name}, by {', '.join(self.authors)}")

            await message.edit(embed=embed)

        except discord.NotFound:
            channel = channel_list["vn_undetermined" if not self.undetermined else "vn_list"]
            message = await channel.fetch_message(self.message_id)
            await message.delete()

            await self.post_to_list(channel_list)

    async def update_entry_ratings(self, message):
        ratings = self.calculate_ratings()

        embed = message.embeds[0]
        embed.set_field_at(0, name="Current Ratings", value=ratings)

        await message.edit(embed=embed)

    def calculate_ratings(self):
        ratings_up = 0
        ratings_down = 0

        for ratings in self.db.table(TABLE_RATING).search(where("vn_id") == self.doc_id):
            if ratings["rating"] == 1:
                ratings_up += 1
            if ratings["rating"] == -1:
                ratings_down += 1

        return f"👍 {ratings_up} 👎 {ratings_down}"

    def add_to_db(self):
        self.doc_id = self.db.table(TABLE_VISUAL_NOVEL).insert({
            "name": self.name,
            "abbreviations": self.abbreviations,
            "authors": self.authors,
            "store": self.store,
            "image": self.image,
            "android_support": self.android_support,
            "undetermined": self.undetermined,
            "message_id": None
        })
        return self.doc_id

    def update_to_db(self):
        VN = Query()
        self.db.table(TABLE_VISUAL_NOVEL).update({
            "name": self.name,
            "abbreviations": self.abbreviations,
            "authors": self.authors,
            "store": self.store,
            "image": self.image,
            "android_support": self.android_support,
            "undetermined": self.undetermined,
            "message_id": self.message_id
        }, doc_ids=[self.doc_id])

    def load_from_db(self, *, doc_id=None, name=None, abbreviations=None, message_id=None):
        def fill_fields(fields):
            self.doc_id = fields.doc_id
            self.name = fields["name"]
            self.abbreviations = fields["abbreviations"]
            self.authors = fields["authors"]
            self.store = fields["store"]
            self.image = fields["image"]
            self.android_support = fields["android_support"]
            self.undetermined = fields["undetermined"]
            self.message_id = fields["message_id"]

        VN = Query()

        if doc_id:
            document = self.db.table(TABLE_VISUAL_NOVEL).get(doc_id=doc_id)
            fill_fields(document)
            return

        vns = None

        if message_id:
            vns = self.db.table(TABLE_VISUAL_NOVEL).search(VN.message_id == message_id)

        if name:
            vns = self.db.table(TABLE_VISUAL_NOVEL).search(VN.name.test(lambda s: s.lower() == name.lower()))

        if abbreviations:
            vns = self.db.table(TABLE_VISUAL_NOVEL).search(VN.abbreviations.any(abbreviations))

        if vns:
            fill_fields(vns[0])
            return

        raise FileNotFoundError("No VN Found.")

    def pretty_abbreviations(self):
        if not self.abbreviations:
            return "-"
        return ", ".join(self.abbreviations)
