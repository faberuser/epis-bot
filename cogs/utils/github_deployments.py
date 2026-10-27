"""Main-branch PR summaries and estimates based on the deployment workflow."""

import math
from datetime import UTC, datetime, timedelta
from urllib.parse import quote

import aiohttp
import discord

import settings

from .announcement_feed import Announcement, AnnouncementFeed


def is_pr_merge(commit):
    return len(commit.get("parents", [])) > 1 and commit["commit"][
        "message"
    ].startswith("Merge pull request #")


def parse_time(value):
    return datetime.fromisoformat(value)


def deployment_notice(run, previous, finished_at, *, now=None):
    """Never describe a completed or failed workflow as an upcoming restart."""
    now = now or datetime.now(UTC)
    if run["status"] == "completed":
        if run.get("conclusion") == "success":
            return (
                "The deployment workflow has finished successfully. The server may "
                "already be updating or restarting; brief network errors are possible."
            )
        return (
            f"The deployment workflow finished with status `{run.get('conclusion')}`. "
            "A server update is not confirmed."
        )
    warning = (
        "Please save your progress. Expect a brief disconnection or network errors "
        "while the server updates and restarts."
    )
    if previous is None or finished_at is None:
        return (
            "A server update is being prepared; no timing estimate is available yet.\n"
            + warning
        )
    duration = (finished_at - parse_time(previous["run_started_at"])).total_seconds()
    if duration <= 0:
        return (
            "A server update is being prepared; no timing estimate is available yet.\n"
            + warning
        )
    minutes = max(1, math.ceil(duration / 60))
    if run["status"] != "in_progress":
        return (
            f"The deployment is queued or waiting for approval. Once started, it may "
            f"take about {minutes} minutes.\n{warning}"
        )
    estimate = parse_time(run["run_started_at"]) + timedelta(minutes=minutes)
    remaining = math.ceil((estimate - now).total_seconds() / 60)
    if remaining > 0:
        return (
            f"The server is expected to update in approximately **{remaining} "
            f"minute{'s' if remaining != 1 else ''}** (<t:{int(estimate.timestamp())}:R>).\n"
            f"{warning}"
        )
    return (
        "The deployment is taking longer than the previous successful run; "
        f"the update may happen soon, but its timing is uncertain.\n{warning}"
    )


class GitHubDeployments(AnnouncementFeed):
    label = "GitHub Server Deployments"

    def __init__(self, parent, *, folder, enabled, data_root):
        super().__init__(parent.client, folder, enabled=enabled, data_root=data_root)
        self.repository = parent.repository
        self.branch = settings.GITHUB_DEPLOY_BRANCH
        self.workflow = settings.GITHUB_DEPLOY_WORKFLOW
        self.channels = parent.channels
        self.channel_path = parent.channel_path
        self.lock = parent.lock
        # Authenticated polling can warn promptly without exhausting the public API limit.
        self.poll.change_interval(minutes=1 if settings.GITHUB_TOKEN else 5)

    async def api(self, session, path, **params):
        async with session.get(
            f"https://api.github.com/repos/{self.repository}/{path}", params=params
        ) as response:
            response.raise_for_status()
            return await response.json()

    async def previous_merge(self, session, merge, history):
        # Follow main's first-parent history, avoiding merges made inside development.
        cursor = merge["parents"][0]["sha"]
        while True:
            if cursor not in history:
                batch = await self.api(session, "commits", sha=cursor, per_page=100)
                history.update((item["sha"], item) for item in batch)
            commit = history[cursor]
            if is_pr_merge(commit):
                return cursor
            if not commit["parents"]:
                # The first PR has no preceding merge; compare against pre-merge main.
                return merge["parents"][0]["sha"]
            cursor = commit["parents"][0]["sha"]

    async def changes(self, session, base, head):
        commits = []
        page = 1
        while True:
            payload = await self.api(
                session, f"compare/{base}...{head}", per_page=100, page=page
            )
            batch = payload["commits"]
            commits.extend(item for item in batch if item["sha"] != head)
            if len(batch) < 100:
                return commits
            page += 1

    async def timing(self, session, runs, current):
        previous = next(
            (
                run
                for run in runs
                if run["run_number"] < current["run_number"]
                and run["status"] == "completed"
                and run.get("conclusion") == "success"
            ),
            None,
        )
        if previous is None or current["status"] == "completed":
            return previous, None
        completed = []
        page = 1
        while True:
            payload = await self.api(
                session, f"actions/runs/{previous['id']}/jobs", per_page=100, page=page
            )
            jobs = payload["jobs"]
            completed.extend(
                parse_time(job["completed_at"])
                for job in jobs
                if job.get("completed_at")
            )
            if len(jobs) < 100:
                break
            page += 1
        return previous, max(completed) if completed else None

    async def fetch_posts(self):
        headers = {"Accept": "application/vnd.github+json", "User-Agent": "epis-bot"}
        if settings.GITHUB_TOKEN:
            headers["Authorization"] = f"Bearer {settings.GITHUB_TOKEN}"
        async with aiohttp.ClientSession(
            headers=headers, timeout=aiohttp.ClientTimeout(total=30)
        ) as session:
            commits = await self.api(session, "commits", sha=self.branch, per_page=100)
            history = {item["sha"]: item for item in commits}
            # Restrict detection to the first-parent main history, not merged side branches.
            merges = []
            cursor = commits[0]["sha"] if commits else None
            while cursor in history:
                commit = history[cursor]
                if is_pr_merge(commit):
                    merges.append(commit)
                cursor = commit["parents"][0]["sha"] if commit["parents"] else None
            initialized = [
                set(self.seen[channel])
                for channel, active in self.channels.items()
                if active and channel in self.seen
            ]
            posts = []
            runs = None
            for merge in reversed(merges):
                identity = merge["sha"]
                if not initialized or all(identity in seen for seen in initialized):
                    # Baseline/known entries are never delivered, so need no API enrichment.
                    posts.append(Announcement(identity, discord.Embed()))
                    continue
                if runs is None:
                    payload = await self.api(
                        session,
                        f"actions/workflows/{quote(self.workflow, safe='')}/runs",
                        branch=self.branch,
                        event="push",
                        per_page=100,
                    )
                    runs = sorted(
                        payload["workflow_runs"],
                        key=lambda run: run["run_number"],
                        reverse=True,
                    )
                run = next(
                    (item for item in runs if item["head_sha"] == identity), None
                )
                if run is None:
                    # Workflow creation can lag behind a merge. Retry before marking delivered.
                    raise RuntimeError(
                        "Waiting for the deployment workflow for a new main merge"
                    )
                base = await self.previous_merge(session, merge, history)
                changes = await self.changes(session, base, identity)
                previous, finished_at = await self.timing(session, runs, run)
                messages = [
                    f"[{item['sha'][:7]}]({item['html_url']}) {item['commit']['message'].strip()}"
                    for item in changes
                ]
                full_text = "\n".join(messages) or "No additional commit messages."
                embed = discord.Embed(
                    title=merge["commit"]["message"].splitlines()[0][:256],
                    url=merge["html_url"],
                    description=full_text[:3500],
                    colour=settings.EMBED_COLOR,
                    timestamp=parse_time(merge["commit"]["committer"]["date"]),
                )
                if len(full_text) > 3500:
                    embed.description = full_text[:3500] + (
                        "\n\nFull commit messages are attached in changelog.txt."
                    )
                embed.add_field(
                    name="Server Availability",
                    value=deployment_notice(run, previous, finished_at),
                    inline=False,
                )
                embed.add_field(
                    name="Deployment Workflow",
                    value=f"[View build and deployment]({run['html_url']})",
                    inline=False,
                )
                embed.set_footer(
                    text=f"{self.repository} · {self.branch} · {len(changes)} commits"
                )
                posts.append(
                    Announcement(
                        identity,
                        embed,
                        attachment=full_text.encode("utf-8")
                        if len(full_text) > 3500
                        else None,
                    )
                )
            return posts
