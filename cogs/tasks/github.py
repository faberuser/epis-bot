"""Poll a configured GitHub repository for new commits and PR merges."""

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
        identity = github_identity(self.repository, self.branch)
        super().__init__(
            client,
            f"github/{identity}",
            enabled=configured,
            data_root=data_root,
            name="commits",
        )
        self.source_url = (
            f"https://github.com/{self.repository}/commits/{quote(self.branch, safe='')}"
            if configured
            else ""
        )
        if configured:
            self.label = f"GitHub {self.repository} ({self.branch})"
        self.commits.invoke_without_command = True

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
        # The API returns newest first. Deliver oldest first without sorting dates,
        # which can be out of order when commits are merged or rebased.
        return [
            Announcement(item["sha"], *self.commit_embed([item]), data=item)
            for item in reversed(payload)
        ]

    def group_pending(self, pending):
        # Commits found in one check normally arrived in one push; send them together.
        if len(pending) < 2:
            return super().group_pending(pending)
        embed, attachment = self.commit_embed([post.data for post in pending])
        return [
            (
                [post.id for post in pending],
                Announcement(pending[-1].id, embed, attachment=attachment),
            )
        ]

    def commit_embed(self, items):
        """One embed listing the given commits, oldest first."""
        first, last = items[0], items[-1]
        parents = first.get("parents") or []
        url = (
            f"https://github.com/{self.repository}/compare/"
            f"{parents[0]['sha'][:12]}...{last['sha'][:12]}"
            if len(items) > 1 and parents
            else last["html_url"]
        )
        lines, changelog, authors = [], [], []
        for item in items:
            commit = item["commit"]
            message = commit["message"].strip() or "(No commit message)"
            name = (commit.get("author") or {}).get("name") or "Unknown author"
            if name not in authors:
                authors.append(name)
            summary = message.splitlines()[0][:200]
            lines.append(
                f"[`{item['sha'][:7]}`]({item['html_url']}) {summary} — {name}"
            )
            changelog.append(f"{item['sha']} ({name})\n{message}\n")
        description = "\n".join(lines)
        attachment = None
        if len(description) > 3800:
            cut = description[:3700].rsplit("\n", 1)[0]
            description = f"{cut}\n\n... and more. Full commit messages are attached in changelog.txt."
            attachment = "\n".join(changelog).encode("utf-8")
        commit = last["commit"]
        date = (commit.get("committer") or {}).get("date") or (
            commit.get("author") or {}
        ).get("date")
        embed = discord.Embed(
            title=f"{len(items)} new commit{'s' if len(items) != 1 else ''}",
            url=url,
            description=description,
            colour=settings.EMBED_COLOR,
            timestamp=datetime.fromisoformat(date) if date else None,
        )
        embed.set_author(name=", ".join(authors)[:256])
        embed.set_footer(text=f"{self.repository} · {self.branch}"[:2048])
        return embed, attachment

    @commands.hybrid_group(description="Manage GitHub branch commit announcements")
    @commands.guild_only()
    async def commits(self, ctx):
        await self.status(ctx)

    @commits.command(name="latest", description="Show the latest tracked branch commit")
    @commands.guild_only()
    @commands.cooldown(1, 30, commands.BucketType.user)
    async def commits_latest(self, ctx):
        await self.latest(ctx)

    @commits.command(
        name="status", description="Show this channel's GitHub subscription"
    )
    @commands.guild_only()
    async def commits_status(self, ctx):
        await self.status(ctx)

    @commits.command(name="on", description="Follow new commits in this channel")
    @commands.guild_only()
    @commands.has_permissions(manage_channels=True)
    async def commits_on(self, ctx):
        await self.subscription(ctx, True)

    @commits.command(
        name="off", description="Stop commit announcements in this channel"
    )
    @commands.guild_only()
    @commands.has_permissions(manage_channels=True)
    async def commits_off(self, ctx):
        await self.subscription(ctx, False)


class GitHubMerges(GitHubDeployments):
    disabled_message = (
        "GitHub merge tracking is disabled. Set GITHUB_REPO, GITHUB_BRANCH, "
        "GITHUB_DEPLOY_BRANCH and GITHUB_DEPLOY_WORKFLOW first."
    )

    def __init__(self, client, *, data_root=DATA_ROOT):
        repository = settings.GITHUB_REPO
        identity = github_identity(repository, settings.GITHUB_BRANCH)
        enabled = bool(
            repository
            and settings.GITHUB_BRANCH
            and settings.GITHUB_DEPLOY_BRANCH
            and settings.GITHUB_DEPLOY_WORKFLOW
        )
        super().__init__(
            client,
            repository,
            folder=f"github/{identity}",
            enabled=enabled,
            data_root=data_root,
            name="merges",
        )
        self.source_url = (
            f"https://github.com/{repository}/pulls?q=is%3Apr+is%3Amerged+base%3A"
            f"{quote(self.branch, safe='')}"
            if enabled
            else ""
        )
        if enabled:
            self.label = f"GitHub {repository} merges ({self.branch})"
        self.merges.invoke_without_command = True

    @commands.hybrid_group(description="Manage GitHub PR merge announcements")
    @commands.guild_only()
    async def merges(self, ctx):
        await self.status(ctx)

    @merges.command(
        name="status", description="Show this channel's GitHub merge subscription"
    )
    @commands.guild_only()
    async def merges_status(self, ctx):
        await self.status(ctx)

    @merges.command(name="on", description="Follow new PR merges in this channel")
    @commands.guild_only()
    @commands.has_permissions(manage_channels=True)
    async def merges_on(self, ctx):
        await self.subscription(ctx, True)

    @merges.command(
        name="off", description="Stop PR merge announcements in this channel"
    )
    @commands.guild_only()
    @commands.has_permissions(manage_channels=True)
    async def merges_off(self, ctx):
        await self.subscription(ctx, False)


def github_identity(repository, branch):
    # Changing the source gets its own baseline and subscription state.
    return hashlib.sha256(f"{repository.lower()}:{branch}".encode()).hexdigest()[:16]


async def setup(client):
    await client.add_cog(GitHub(client))
    await client.add_cog(GitHubMerges(client))
