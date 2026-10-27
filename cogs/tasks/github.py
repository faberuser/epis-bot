"""Poll a configured GitHub branch for new commits."""

import hashlib
import re
from datetime import datetime
from urllib.parse import quote

import aiohttp
import discord
from discord.ext import commands

import settings

from ..utils.announcement_feed import (
    DATA_ROOT,
    Announcement,
    AnnouncementFeed,
    write_state,
)
from ..utils.github_deployments import GitHubDeployments


class GitHub(AnnouncementFeed):
    label = "GitHub commits"
    disabled_message = (
        "GitHub tracking is disabled. Set GITHUB_REPO and GITHUB_BRANCH first."
    )

    def __init__(self, client, *, data_root=DATA_ROOT):
        self.repository = settings.GITHUB_REPO
        self.branch = settings.GITHUB_BRANCH
        if self.repository and not re.fullmatch(
            r"[A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+", self.repository
        ):
            raise ValueError("GITHUB_REPO must use owner/repository format")
        configured = bool(self.repository and self.branch)
        # Changing the source gets its own baseline and subscription state.
        identity = hashlib.sha256(
            f"{self.repository.lower()}:{self.branch}".encode()
        ).hexdigest()[:16]
        super().__init__(
            client, f"github/{identity}", enabled=configured, data_root=data_root
        )
        self.source_url = (
            f"https://github.com/{self.repository}/commits/{quote(self.branch, safe='')}"
            if configured
            else ""
        )
        if configured:
            self.label = f"GitHub {self.repository} ({self.branch})"
        self.github.invoke_without_command = True
        deployment_identity = hashlib.sha256(
            f"{settings.GITHUB_DEPLOY_BRANCH}:{settings.GITHUB_DEPLOY_WORKFLOW}".encode()
        ).hexdigest()[:16]
        self.deployments = GitHubDeployments(
            self,
            folder=f"github/{identity}/deployments/{deployment_identity}",
            enabled=configured
            and bool(settings.GITHUB_DEPLOY_BRANCH and settings.GITHUB_DEPLOY_WORKFLOW),
            data_root=data_root,
        )

    async def cog_load(self):
        await super().cog_load()
        await self.deployments.cog_load()

    async def cog_unload(self):
        await self.deployments.cog_unload()
        await super().cog_unload()

    def reset_delivery(self, channel_id):
        super().reset_delivery(channel_id)
        self.deployments.seen.pop(channel_id, None)
        write_state(self.deployments.state_path, self.deployments.seen)

    async def fetch_posts(self):
        headers = {
            "Accept": "application/vnd.github+json",
            "X-GitHub-Api-Version": "2022-11-28",
            "User-Agent": "epis-bot",
        }
        if settings.GITHUB_TOKEN:
            headers["Authorization"] = f"Bearer {settings.GITHUB_TOKEN}"
        async with (
            aiohttp.ClientSession(
                headers=headers, timeout=aiohttp.ClientTimeout(total=20)
            ) as session,
            session.get(
                f"https://api.github.com/repos/{self.repository}/commits",
                params={"sha": self.branch, "per_page": 100},
            ) as response,
        ):
            response.raise_for_status()
            payload = await response.json()
        if not isinstance(payload, list):
            raise TypeError("GitHub returned an unexpected commit response")
        posts = []
        # The API returns newest first. Deliver oldest first without sorting dates,
        # which can be out of order when commits are merged or rebased.
        for item in reversed(payload):
            commit = item["commit"]
            message = commit["message"].strip() or "(No commit message)"
            author = commit.get("author") or {}
            committer = commit.get("committer") or {}
            date = committer.get("date") or author.get("date")
            embed = discord.Embed(
                title=f"{item['sha'][:7]} · {message.splitlines()[0]}"[:256],
                url=item["html_url"],
                description=message[:3800],
                colour=settings.EMBED_COLOR,
                timestamp=datetime.fromisoformat(date) if date else None,
            )
            embed.set_author(name=(author.get("name") or "Unknown author")[:256])
            embed.set_footer(text=f"{self.repository} · {self.branch}"[:2048])
            posts.append(Announcement(item["sha"], embed))
        return posts

    @commands.hybrid_group(description="Manage GitHub branch commit announcements")
    @commands.guild_only()
    async def github(self, ctx):
        await self.status(ctx)

    @github.command(name="latest", description="Show the latest tracked branch commit")
    @commands.guild_only()
    @commands.cooldown(1, 30, commands.BucketType.user)
    async def github_latest(self, ctx):
        await self.latest(ctx)

    @github.command(
        name="status", description="Show this channel's GitHub subscription"
    )
    @commands.guild_only()
    async def github_status(self, ctx):
        await self.status(ctx)

    @github.command(name="on", description="Follow new commits in this channel")
    @commands.guild_only()
    @commands.has_permissions(manage_channels=True)
    async def github_on(self, ctx):
        await self.subscription(ctx, True)

    @github.command(name="off", description="Stop commit announcements in this channel")
    @commands.guild_only()
    @commands.has_permissions(manage_channels=True)
    async def github_off(self, ctx):
        await self.subscription(ctx, False)


async def setup(client):
    await client.add_cog(GitHub(client))
