"""Official KING's RAID RE:VERSE announcements from Steam's public news API."""

import html
import re
from datetime import UTC, datetime
from urllib.parse import urlsplit

import aiohttp
import discord
from discord.ext import commands

import settings

from ..utils.announcement_feed import DATA_ROOT, Announcement, AnnouncementFeed

APP_ID = 3689540
NEWS_API = "https://api.steampowered.com/ISteamNews/GetNewsForApp/v2/"
OFFICIAL_FEED = "steam_community_announcements"


def web_url(value):
    value = html.unescape(value).strip().strip("\"'")
    value = value.replace(
        "{STEAM_CLAN_IMAGE}", "https://clan.akamai.steamstatic.com/images"
    )
    try:
        parsed = urlsplit(value)
    except ValueError:
        return None
    return value if parsed.scheme in ("http", "https") and parsed.netloc else None


def steam_content(contents):
    """Convert Steam BBCode to Discord text and extract its first usable image."""
    text = html.unescape(contents).replace("\xa0", " ")
    image = None

    def extract_image(match):
        nonlocal image
        attributes, body = match.groups()
        source = re.search(r"""\bsrc\s*=\s*("[^"]*"|'[^']*'|[^\s\]]+)""", attributes)
        candidate = web_url(source.group(1) if source else body)
        if candidate and image is None:
            image = candidate
        return ""

    text = re.sub(
        r"\[img\b([^\]]*)\](.*?)\[/img\]",
        extract_image,
        text,
        flags=re.IGNORECASE | re.DOTALL,
    )
    text = re.sub(r"<br\s*/?>", "\n", text, flags=re.IGNORECASE)
    text = re.sub(r"</p\s*>", "\n\n", text, flags=re.IGNORECASE)
    text = re.sub(r"<[^>]+>", "", text)

    def link(match):
        target, label = match.groups()
        target = web_url(target)
        label = label.strip()
        if not target:
            return label
        if label == target:
            return target
        target = target.replace("(", "%28").replace(")", "%29")
        return f"[{label}]({target})"

    text = re.sub(
        r"\[url=([^\]]+)\](.*?)\[/url\]",
        link,
        text,
        flags=re.IGNORECASE | re.DOTALL,
    )

    def emphasis(match, marker):
        body = match.group(1)
        if not body.strip():
            return body
        leading = body[: len(body) - len(body.lstrip())]
        trailing = body[len(body.rstrip()) :]
        return leading + marker + body.strip() + marker + trailing

    for tag, marker in (("b", "**"), ("i", "*"), ("u", "__"), ("strike", "~~")):
        text = re.sub(
            rf"\[{tag}\](.*?)\[/{tag}\]",
            lambda match, marker=marker: emphasis(match, marker),
            text,
            flags=re.IGNORECASE | re.DOTALL,
        )
    text = re.sub(
        r"\[h[1-6]\](.*?)\[/h[1-6]\]",
        lambda match: "\n\n**" + match.group(1).strip() + "**\n\n",
        text,
        flags=re.IGNORECASE | re.DOTALL,
    )
    text = re.sub(r"\[\*\]\s*(?:\[p\])?", "\n- ", text, flags=re.IGNORECASE)
    text = re.sub(
        r"\[/?(?:p|list|olist|tr|table|quote)\b[^\]]*\]|\[hr\s*/?\]",
        "\n\n",
        text,
        flags=re.IGNORECASE,
    )
    text = re.sub(r"\[/(?:td|th)\]", " | ", text, flags=re.IGNORECASE)
    # Only remove known formatting tags; bracketed article text such as [CBT] stays.
    text = re.sub(
        r"\[/?(?:b|i|u|strike|h[1-6]|td|th|\*|code|previewyoutube|url)\b[^\]]*\]|\[/\*\]",
        "",
        text,
        flags=re.IGNORECASE,
    )
    text = re.sub(r"[ \t]+\n", "\n", text)
    text = re.sub(r"\n{3,}", "\n\n", text).strip()
    return text, image


def news_post(item):
    text, image = steam_content(item.get("contents", ""))
    embed = discord.Embed(
        title=html.unescape(item["title"])[:256],
        url=item["url"],
        description=text[:3800]
        + (
            "\n\nRead the full announcement using the title link."
            if len(text) > 3800
            else ""
        ),
        colour=discord.Colour.from_rgb(23, 26, 33),
        timestamp=datetime.fromtimestamp(item["date"], tz=UTC),
    )
    embed.set_author(
        name="KING's RAID RE:VERSE", url=f"https://store.steampowered.com/app/{APP_ID}/"
    )
    embed.set_footer(text="Steam • Official announcements")
    if image:
        embed.set_image(url=image)
    return Announcement(str(item["gid"]), embed)


class Steam(AnnouncementFeed):
    label = "KING's RAID RE:VERSE Steam"
    source_url = f"https://store.steampowered.com/news/app/{APP_ID}"

    def __init__(self, client, *, data_root=DATA_ROOT):
        super().__init__(client, "steam", data_root=data_root)
        self.steam.invoke_without_command = True

    async def fetch_posts(self):
        async with (
            aiohttp.ClientSession(timeout=aiohttp.ClientTimeout(total=20)) as session,
            session.get(
                NEWS_API,
                proxy=settings.STEAM_PROXY_URL,
                params={
                    "appid": APP_ID,
                    "count": 100,
                    "maxlength": 0,
                    "feeds": OFFICIAL_FEED,
                },
            ) as response,
        ):
            response.raise_for_status()
            payload = await response.json()
        news = payload["appnews"]
        if int(news["appid"]) != APP_ID:
            raise ValueError("Steam returned news for a different game")
        return [
            news_post(item)
            for item in sorted(
                news["newsitems"], key=lambda item: (item["date"], str(item["gid"]))
            )
            if item.get("feedname") == OFFICIAL_FEED
            and int(item.get("appid", APP_ID)) == APP_ID
        ]

    @commands.hybrid_group(
        description="Manage KING's RAID RE:VERSE Steam announcements",
    )
    @commands.guild_only()
    async def steam(self, ctx):
        await self.status(ctx)

    @steam.command(name="latest", description="Show the latest Steam announcement")
    @commands.guild_only()
    @commands.cooldown(1, 30, commands.BucketType.user)
    async def steam_latest(self, ctx):
        await self.latest(ctx)

    @steam.command(name="status", description="Show this channel's Steam subscription")
    @commands.guild_only()
    async def steam_status(self, ctx):
        await self.status(ctx)

    @steam.command(
        name="on", description="Follow new Steam announcements in this channel"
    )
    @commands.guild_only()
    @commands.has_permissions(manage_channels=True)
    async def steam_on(self, ctx):
        await self.subscription(ctx, True)

    @steam.command(name="off", description="Stop Steam announcements in this channel")
    @commands.guild_only()
    @commands.has_permissions(manage_channels=True)
    async def steam_off(self, ctx):
        await self.subscription(ctx, False)


async def setup(client):
    await client.add_cog(Steam(client))
