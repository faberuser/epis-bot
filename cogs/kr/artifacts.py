import re

import discord
from discord import app_commands
from discord.ext import commands
from fuzzywuzzy import process

import settings

from ..utils.game_data import (
    DataUnavailable,
    GameData,
    selected_data,
    stamp,
    version_autocomplete,
)
from ..utils.menus import ChoiceView, asset, send_result
from ..utils.paginator import Paginator
from ..utils.routes import RouteCog, add_routes


class Artifact(RouteCog):
    def __init__(self, client):
        self.client = client

    @commands.hybrid_command(
        name="atf",
        aliases=["artifact", "artifacts", "arti", "art"],
        description="Look up an artifact",
    )
    @app_commands.autocomplete(version=version_autocomplete)
    async def artifact(
        self, ctx, *, name: str | None = None, version: str | None = None
    ):
        dataset = selected_data(ctx, version)
        if name is None:
            await ctx.send(
                "Use `artifact <name>`, `artifact search <name>`, or `artifact all`."
            )
        elif name.lower() in ("all", "list"):
            await self.show_all(ctx, dataset)
        elif name.lower().startswith("search "):
            await self.search(ctx, name[7:], dataset)
        else:
            result = self.get_artifact(name, dataset)
            if isinstance(result[1], list):
                await self.show_choices(ctx, result[1], result[0], dataset)
            else:
                await send_result(ctx, result)

    async def show_choices(self, ctx, names, embed, dataset):
        if not names:
            raise DataUnavailable(f"No artifacts are available in {dataset.label}.")
        view = ChoiceView(
            ctx.author.id,
            [(name, name) for name in dict.fromkeys(names)],
            lambda name: self.get_artifact(name, dataset),
            placeholder="Choose an artifact",
        )
        await send_result(ctx, stamp(embed, dataset), view=view)

    async def search(self, ctx, name, dataset):
        _data, names, _all_names, _aliases = self.get_all_artifacts(dataset)
        matches = process.extract(name, names, limit=25)
        await self.show_choices(
            ctx,
            [match[0] for match in matches],
            discord.Embed(title=f"Results for {name}", colour=settings.EMBED_COLOR),
            dataset,
        )

    @commands.hybrid_command(description="Search artifacts")
    @app_commands.autocomplete(version=version_autocomplete)
    async def artifact_search(self, ctx, *, name: str, version: str | None = None):
        await self.search(ctx, name, selected_data(ctx, version))

    async def show_all(self, ctx, dataset):
        names = list(dataset.artifacts())
        pages = [
            discord.Embed(
                title="Artifacts",
                description="\n".join(names[i : i + 30]),
                colour=settings.EMBED_COLOR,
            )
            for i in range(0, len(names), 30)
        ]
        await Paginator(self.client).pag(ctx, stamp(pages, dataset))

    @commands.hybrid_command(description="List all artifacts")
    @app_commands.autocomplete(version=version_autocomplete)
    async def artifact_all(self, ctx, *, version: str | None = None):
        await self.show_all(ctx, selected_data(ctx, version))

    def get_all_artifacts(self, version=None):
        dataset = version if isinstance(version, GameData) else GameData(version)
        artifacts = dataset.artifacts()
        names = list(artifacts)
        aliases = {}
        for name, item in artifacts.items():
            for alias in [item.get("id", name), *(item.get("aliases") or [])]:
                aliases[alias] = name
        return artifacts, names, names + list(aliases), aliases

    def get_artifact(self, query, version=None):
        dataset = version if isinstance(version, GameData) else GameData(version)
        artifacts, names, all_names, aliases = self.get_all_artifacts(dataset)
        match = process.extractOne(query, all_names)
        if match is None:
            raise DataUnavailable(f"No artifacts are available in {dataset.label}.")
        if match[1] < 60:
            return discord.Embed(title="Did you mean", colour=settings.EMBED_COLOR), [
                item[0] for item in process.extract(query, names, limit=5)
            ]
        name = aliases.get(match[0], match[0])
        item = artifacts[name]
        description = (
            item["description"]
            + "\n\n"
            + "\n".join(
                f"({key}): {value}" for key, value in (item.get("value") or {}).items()
            )
        )
        embed = discord.Embed(
            title=name, description=description, colour=settings.EMBED_COLOR
        )
        filename = re.sub(r"[^a-zA-Z0-9_.-]", "_", name) + ".png"
        file = asset(item["thumbnail"], filename=filename)
        embed.set_thumbnail(url=f"attachment://{filename}")
        return stamp((embed, file), dataset)


async def setup(bot):
    cog = Artifact(bot)
    await bot.add_cog(cog)
    add_routes(
        bot,
        cog,
        {
            "artifact name": "atf",
            "artifact search": "artifact_search",
            "artifact all": "artifact_all",
        },
    )
