import re

import discord
from discord.ext import commands
from fuzzywuzzy import process

import settings

from ..utils.menus import ChoiceView, send_result
from ..utils.routes import RouteCog, add_routes


class Guide(RouteCog):
    def __init__(self, client):
        self.client = client
        self.guild_id = settings.KRE_GUILD_ID
        self.categories = settings.KRE_CATEGORIES
        self.taken = (
            f"\n*Taken from [KR Encyclopedia]({settings.KRE_INVITE})*"
            if settings.KRE_INVITE
            else ""
        )

    def channels(self):
        if not self.guild_id or not self.categories:
            raise commands.BadArgument(
                "Guides are disabled. Configure KRE_GUILD_ID and KRE_CATEGORIES to enable them."
            )
        guild = self.client.get_guild(self.guild_id)
        if guild is None:
            raise commands.BadArgument(
                "The bot must join the configured guide server first."
            )
        channels = []
        for category_id in self.categories:
            category = guild.get_channel(category_id)
            if isinstance(category, discord.CategoryChannel):
                channels.extend(
                    channel
                    for channel in category.channels
                    if isinstance(channel, discord.TextChannel)
                    and channel.permissions_for(guild.me).view_channel
                    and channel.permissions_for(guild.me).read_message_history
                )
        return channels

    @commands.hybrid_command(
        name="guide_content",
        aliases=["guide"],
        description="Read or search the King's Raid guides",
    )
    async def guide(self, ctx, *, content: str | None = None):
        if content is None:
            await ctx.send(
                "Use `guide <topic>`, `guide list`, or `guide search <topic>`."
            )
            return
        if content.lower() in ("all", "list"):
            await self.browse(ctx)
        elif content.lower().startswith("search "):
            await self.browse(ctx, content[7:])
        else:
            await self.browse(ctx, content)

    async def browse(self, ctx, query=None):
        await ctx.defer()
        channels = self.channels()
        if query:
            labels = {
                f"{channel.category.name} / {channel.name}": channel
                for channel in channels
            }
            channels = [
                labels[match[0]]
                for match in process.extract(query, list(labels), limit=25)
                if match[1] >= 50
            ]
        if not channels:
            await ctx.send("No matching guides are available.")
            return

        async def render(channel):
            return await self.get_embed(channel)

        view = ChoiceView(
            ctx.author.id,
            [
                (f"{channel.category.name} / {channel.name}", channel)
                for channel in channels
            ],
            render,
            placeholder="Choose a guide",
        )
        embed = discord.Embed(
            title="King's Raid guides",
            description="Choose a topic below." + self.taken,
            colour=settings.EMBED_COLOR,
        )
        await send_result(ctx, embed, view=view)

    @commands.hybrid_command(description="Browse available guides")
    async def guide_list(self, ctx):
        await self.browse(ctx)

    @commands.hybrid_command(description="Search available guides")
    async def guide_search(self, ctx, *, content: str):
        await self.browse(ctx, content)

    async def get_embed(self, channel):  # get embed
        messages_ = [
            message async for message in channel.history(limit=20, oldest_first=True)
        ]
        embeds = []
        count = 1
        messages = []
        title = ""
        for message in messages_:
            if message.attachments:
                messages.append(message.attachments[0].url)
            if len(message.content) >= 1900:
                for content in message.content.splitlines():
                    if content == "":
                        continue
                    elif (
                        content.startswith("*")
                        or content.startswith("_")
                        and content.endswith("*")
                        or content.endswith("_")
                    ):
                        title += content + "\n\n"
                    else:
                        message_ = title + content
                        messages.append(message_)
                        title = ""
            else:
                if title != "":
                    messages.append(title + message.content)
                else:
                    messages.append(message.content)
                title = ""
        for message in messages:
            embed = discord.Embed(
                title=(channel.name + " guide").title(),
                description=message + f"\n{self.taken} *<#{channel.id}>*",
                color=discord.Colour.dark_purple(),
            )
            embed.set_footer(text=f"Page {count}/{len(messages)}")
            urls_start = [
                "https://cdn.discordapp.com/attachments/",
                "https://media.discordapp.net/attachments/",
            ]
            for url_start in urls_start:
                if url_start in message:
                    pic = [".png", ".jpg", ".jpeg"]
                    for fm in pic:
                        if fm in message:
                            msgc = message
                            match = re.search(
                                f"{re.escape(url_start)}(.*?){re.escape(fm)}", msgc
                            )
                            if match is None:
                                continue
                            url = match.group(1)
                            embed.set_image(url=url_start + url + fm)
                            break
            if "https://imgur.com/" in message:
                for line in (message).splitlines():
                    if "https://imgur.com/" in line:
                        embed.set_image(url=line)
                        break
            embeds.append(embed)
            count += 1
        return embeds


async def setup(bot):
    cog = Guide(bot)
    await bot.add_cog(cog)
    add_routes(
        bot,
        cog,
        {
            "guide content": "guide_content",
            "guide list": "guide_list",
            "guide search": "guide_search",
        },
    )
