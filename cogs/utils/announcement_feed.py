"""Persistent channel subscriptions and delivery for announcement feeds."""

import asyncio
import json
import logging
from dataclasses import dataclass
from pathlib import Path

import discord
from discord.ext import commands, tasks

DATA_ROOT = Path(__file__).resolve().parents[2] / "data"
log = logging.getLogger(__name__)


@dataclass
class Announcement:
    id: str
    embed: discord.Embed


def read_state(path):
    if not path.exists() or not path.read_text(encoding="utf-8").strip():
        return {}
    return json.loads(path.read_text(encoding="utf-8"))


def write_state(path, value):
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_suffix(".tmp")
    temporary.write_text(
        json.dumps(value, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    temporary.replace(path)


class AnnouncementFeed(commands.Cog):
    label = "Announcements"
    source_url = ""
    disabled_message = "This announcement feed is not configured."

    def __init__(self, client, folder, *, enabled=True, data_root=DATA_ROOT):
        self.client = client
        self.enabled = enabled
        self.channel_path = Path(data_root) / folder / "channels.json"
        self.state_path = Path(data_root) / folder / "delivery.json"
        self.channels = read_state(self.channel_path)
        self.seen = read_state(self.state_path)
        self.lock = asyncio.Lock()

    async def cog_load(self):
        if self.enabled:
            self.poll.start()

    async def cog_unload(self):
        self.poll.cancel()

    async def fetch_posts(self) -> list[Announcement]:
        raise NotImplementedError("Announcement feeds must implement fetch_posts")

    @tasks.loop(minutes=5)
    async def poll(self):
        try:
            await self.poll_once()
        except commands.BadArgument as error:
            log.warning("%s announcement check failed: %s", self.label, error)
        except Exception:
            log.exception("%s announcement check failed; will retry", self.label)

    @poll.before_loop
    async def before_poll(self):
        await self.client.wait_until_ready()

    async def poll_once(self):
        async with self.lock:
            if not self.enabled or not any(self.channels.values()):
                return
            posts = await self.fetch_posts()  # Oldest first, with stable source IDs.
            ids = [post.id for post in posts]
            for channel_id, active in list(self.channels.items()):
                if not active:
                    continue
                if channel_id not in self.seen:
                    # First successful check establishes a baseline, even for an empty feed.
                    self.seen[channel_id] = ids
                    write_state(self.state_path, self.seen)
                    continue
                pending = [
                    post for post in posts if post.id not in self.seen[channel_id]
                ]
                if not pending:
                    continue
                try:
                    channel = self.client.get_channel(int(channel_id))
                    if channel is None:
                        channel = await self.client.fetch_channel(int(channel_id))
                    for post in pending:
                        await channel.send(
                            embed=post.embed,
                            allowed_mentions=discord.AllowedMentions.none(),
                        )
                        self.seen[channel_id] = (self.seen[channel_id] + [post.id])[
                            -500:
                        ]
                        write_state(self.state_path, self.seen)
                except discord.NotFound:
                    self.channels[channel_id] = False
                    write_state(self.channel_path, self.channels)
                except discord.HTTPException:
                    # Keep failed posts pending for this channel; other channels can progress.
                    log.warning(
                        "%s delivery to channel %s failed; will retry",
                        self.label,
                        channel_id,
                    )

    async def subscription(self, ctx, active):
        await ctx.defer()
        if active:
            if not self.enabled:
                raise commands.BadArgument(self.disabled_message)
            permissions = ctx.channel.permissions_for(ctx.guild.me)
            if not (
                permissions.view_channel
                and permissions.send_messages
                and permissions.embed_links
            ):
                raise commands.BadArgument(
                    "I need View Channel, Send Messages, and Embed Links in this channel."
                )
        channel_id = str(ctx.channel.id)
        async with self.lock:
            if active and not self.channels.get(channel_id):
                self.seen.pop(channel_id, None)
            self.channels[channel_id] = active
            write_state(self.channel_path, self.channels)
            write_state(self.state_path, self.seen)
        await ctx.send(
            f"{self.label} announcements are {'on' if active else 'off'} for this channel."
        )

    async def latest(self, ctx):
        if not self.enabled:
            raise commands.BadArgument(self.disabled_message)
        await ctx.defer()
        try:
            async with self.lock:
                posts = await self.fetch_posts()
        except commands.BadArgument as error:
            log.warning("%s latest item lookup failed: %s", self.label, error)
            raise
        except Exception as error:
            log.exception("%s latest item lookup failed", self.label)
            raise commands.BadArgument(
                f"Could not fetch the latest {self.label} item. Please try again later."
            ) from error
        if not posts:
            await ctx.send(f"No items are available from {self.label} yet.")
            return
        await ctx.send(
            embed=posts[-1].embed,
            allowed_mentions=discord.AllowedMentions.none(),
        )

    async def status(self, ctx):
        state = "on" if self.channels.get(str(ctx.channel.id)) else "off"
        disabled = f" {self.disabled_message}" if not self.enabled else ""
        await ctx.send(
            f"{self.label} announcements are {state} for this channel. {self.source_url}{disabled}"
        )
