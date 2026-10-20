"""Watch the King's Raid X account without blocking the Discord event loop."""

import asyncio

import discord
import requests
import tweepy
from discord.ext import commands
from tweepy.client import Response

import settings

from ..utils.announcement_feed import DATA_ROOT, Announcement, AnnouncementFeed

USERNAME = "kingsraid_msg"


class TimeoutSession(requests.Session):
    def request(self, *args, **kwargs):
        kwargs.setdefault("timeout", 20)
        return super().request(*args, **kwargs)


class Twitter(AnnouncementFeed):
    label = "King's Raid Twitter / X"
    source_url = f"https://x.com/{USERNAME}"
    disabled_message = (
        "Twitter polling is disabled. Set BEARER_TOKEN with access to the X API first."
    )

    def __init__(self, client, *, data_root=DATA_ROOT):
        token = getattr(settings, "BEARER_TOKEN", "")
        super().__init__(client, "twitter", enabled=bool(token), data_root=data_root)
        self.api = (
            tweepy.Client(bearer_token=token, wait_on_rate_limit=False)
            if token
            else None
        )
        if self.api:
            self.api.session.close()
            self.api.session = TimeoutSession()
        self.user_id = None
        self.twitter.invoke_without_command = True

    async def cog_unload(self):
        await super().cog_unload()
        if self.api:
            self.api.session.close()

    def fetch_tweets(self):
        api = self.api
        if api is None:
            return []
        if self.user_id is None:
            response = api.get_user(username=USERNAME, user_auth=False)
            if not isinstance(response, Response) or response.data is None:
                raise ValueError(f"X account @{USERNAME} was not found")
            self.user_id = response.data.id
        response = api.get_users_tweets(
            self.user_id,
            max_results=100,
            exclude=["replies", "retweets"],
            tweet_fields=["created_at"],
            user_auth=False,
        )
        if not isinstance(response, Response) or response.errors:
            raise ValueError("X could not return the account timeline")
        return response.data or []

    async def fetch_posts(self):
        tweets = await asyncio.to_thread(self.fetch_tweets)
        posts = []
        for tweet in sorted(tweets, key=lambda item: int(item.id)):
            embed = discord.Embed(
                title=f"@{USERNAME}",
                url=f"{self.source_url}/status/{tweet.id}",
                description=tweet.text[:4000],
                colour=discord.Colour.from_rgb(29, 161, 242),
                timestamp=tweet.created_at,
            )
            embed.set_author(name=f"King's Raid (@{USERNAME})", url=self.source_url)
            embed.set_footer(text="Twitter / X")
            posts.append(Announcement(str(tweet.id), embed))
        return posts

    @commands.hybrid_group(
        description="Manage King's Raid Twitter announcements",
    )
    @commands.guild_only()
    async def twitter(self, ctx):
        await self.status(ctx)

    @twitter.command(name="latest", description="Show the latest King's Raid tweet")
    @commands.guild_only()
    @commands.cooldown(1, 30, commands.BucketType.user)
    async def twitter_latest(self, ctx):
        await self.latest(ctx)

    @twitter.command(
        name="status", description="Show this channel's Twitter subscription"
    )
    @commands.guild_only()
    async def twitter_status(self, ctx):
        await self.status(ctx)

    @twitter.command(
        name="on", description="Follow new King's Raid tweets in this channel"
    )
    @commands.guild_only()
    @commands.has_permissions(manage_channels=True)
    async def twitter_on(self, ctx):
        await self.subscription(ctx, True)

    @twitter.command(name="off", description="Stop King's Raid tweets in this channel")
    @commands.guild_only()
    @commands.has_permissions(manage_channels=True)
    async def twitter_off(self, ctx):
        await self.subscription(ctx, False)


async def setup(client):
    await client.add_cog(Twitter(client))
