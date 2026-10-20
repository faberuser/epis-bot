from pathlib import Path
from typing import Annotated

import discord
from discord import app_commands
from discord.ext import commands

import settings

from ..utils.game_data import (
    DataUnavailable,
    selected_data,
    stamp,
    version_autocomplete,
)
from ..utils.hero_rendering import HeroRendering
from ..utils.info_embed import Info_Embed
from ..utils.menus import ChoiceView, MenuResult, asset, send_result, text_pages
from ..utils.paginator import Paginator
from ..utils.routes import RouteCog, add_routes


class Heroes(RouteCog, HeroRendering):
    def __init__(self, client):
        self.client = client
        self.help = Info_Embed()
        self.menus = Paginator(client)

    async def lookup(self, ctx, hero, kind, stars=None, version=None):
        dataset = selected_data(ctx, version)
        if hero is None:
            await ctx.send(
                embed=self.help.info_embed(
                    {
                        "info": "Info",
                        "skill": "Skills",
                        "book": "Books",
                        "perk": "Perks",
                        "uw": "UW",
                        "sw": "SW",
                        "uts": "UTs",
                        "splashart": "Splashart",
                        "visual": "Visual",
                        "cos": "Costumes",
                    }.get(kind, "Heroes")
                )
            )
            return
        if stars is not None and not 0 <= stars <= 5:
            raise commands.BadArgument("Stars must be between 0 and 5.")
        classes = (
            "Knight",
            "Warrior",
            "Assassin",
            "Archer",
            "Mechanic",
            "Wizard",
            "Priest",
        )
        cls = next(
            (name for name in classes if hero.casefold() == name.casefold()), None
        )
        if cls:
            if kind == "perk":
                await send_result(
                    ctx,
                    stamp(
                        self.get_class_perk(
                            cls,
                            self.get_color(cls.lower()),
                            dataset.version,
                            dataset.language,
                        )[0],
                        dataset,
                    ),
                )
                return
            choices = []
            for name, data in dataset.entities().items():
                if data["info"]["class"] == cls:
                    choices.append((name, name))
            if not choices:
                await ctx.send("No heroes found in that class.")
                return

            async def render(value):
                obj, data, boss = dataset.find(value)
                if kind in ("story", "perk", "uts", "cos"):
                    return (
                        await self.menu_result(ctx.author.id, kind, obj, data, stars)
                        or "No images are installed for this hero."
                    )
                return await self.render(kind, obj, data, stars=stars, boss=boss)

            view = ChoiceView(
                ctx.author.id, choices, render, placeholder="Choose your hero"
            )
            await send_result(
                ctx,
                discord.Embed(title=f"{cls} heroes", colour=settings.EMBED_COLOR),
                view=view,
            )
            return
        obj, data, boss = dataset.find(hero)
        if kind == "skill":
            await self.menus.pag(ctx, stamp(self.get_skills(obj, data, boss), data))
        elif kind in ("story", "perk", "uts", "cos"):
            await self.show_menu(ctx, kind, obj, data, stars)
        else:
            await send_result(
                ctx, await self.render(kind, obj, data, stars=stars, boss=boss)
            )

    async def render(self, kind, obj, data, *, stars=None, boss=None, choice=None):
        required = {
            "info": "info",
            "skill": "skills",
            "book": "books",
            "perk": "perks",
            "story": "info",
            "cos": "costumes",
        }.get(kind, "uts" if kind.startswith("ut") else kind)
        if not data.get(required):
            raise DataUnavailable(
                f"{kind.title()} data for `{obj}` is unavailable in {data['_version']} / {data['_language']}."
            )
        return stamp(
            await self._render(kind, obj, data, stars=stars, boss=boss, choice=choice),
            data,
        )

    async def _render(self, kind, obj, data, *, stars=None, boss=None, choice=None):
        if kind == "info":
            return self.get_info(obj, data, boss)
        if kind == "skill":
            return self.get_skills(obj, data, boss)
        if kind == "book":
            return self.get_books(obj, data)
        if kind == "uw":
            return self.get_uw(obj, data, stars)
        if kind == "sw":
            return self.get_sw(obj, data)
        if kind in ("splashart", "visual"):
            return self.get_sa_vs(obj, data, kind)
        clr = self.get_color(data["info"]["class"].lower())
        if kind == "perk":
            if choice == "class":
                return self.get_class_perk(
                    data["info"]["class"], clr, data["_version"], data["_language"]
                )[0]
            sections = []
            for tier in ("t3", "t5"):
                sections.append("**" + tier.upper() + " Perks**")
                for key, value in data["perks"][tier].items():
                    if "effect" in value:
                        sections.append(f"[{key.upper()}] {value['effect']}")
                    else:
                        sections.append(f"**Skill {key}**")
                        sections.extend(
                            f"[{side.upper()}] {perk['effect']}"
                            for side, perk in value.items()
                        )
            return discord.Embed(
                title=f"{obj} Perks", description="\n".join(sections), colour=clr
            )
        if kind == "story":
            choice = choice or "Hero"
            if choice == "Hero":
                text = data["info"].get(
                    "story_", data["info"].get("story", "No story available.")
                )
            elif choice.startswith("UT"):
                text = data["uts"][choice[-1]].get("story", "No story available.")
            else:
                text = data[choice.lower()].get("story", "No story available.")
            pages = text_pages(f"{obj} {choice} Story", text, clr)
            return pages if len(pages) > 1 else pages[0]
        if kind.startswith("ut"):
            number = kind[2:] if kind != "uts" else (choice or "All")
            sections = []
            treasures = (
                data["uts"] if number == "All" else {number: data["uts"][number]}
            )
            for key, treasure in treasures.items():
                text = treasure["description"]
                for token, values in treasure["value"].items():
                    if stars is not None:
                        text = text.replace(f"({token})", values[str(stars)], 1)
                    else:
                        text += f"\n({token}): " + ", ".join(values.values())
                sections.append(f"**UT{key}: {treasure['name']}**\n{text}")
            pages = text_pages(
                f"{obj} UTs" if number == "All" else f"{obj} UT{number}",
                "\n\n".join(sections),
                clr,
            )
            if len(pages) > 1:
                return pages
            embed = pages[0]
            if number != "All":
                file = asset(
                    data["uts"][number]["thumbnail"], filename=f"ut{number}.png"
                )
                embed.set_thumbnail(url=f"attachment://ut{number}.png")
                return embed, file
            return embed
        if kind == "cos":
            path = (
                Path(choice)
                if choice
                else next(iter(sorted(Path(data["costumes"]).glob("*.png"))), None)
            )
            if path is None:
                return "No costume images are installed for this hero."
            embed = discord.Embed(title=f"{obj} - {path.stem}", colour=clr)
            embed.set_image(url="attachment://costume.png")
            return embed, asset(path, filename="costume.png")
        raise commands.BadArgument("Unknown hero information type.")

    async def show_menu(self, ctx, kind, obj, data, stars=None):
        required = {"story": "info", "perk": "perks", "uts": "uts", "cos": "costumes"}[
            kind
        ]
        if not data.get(required):
            raise DataUnavailable(
                f"{kind.title()} data for `{obj}` is unavailable in {data['_version']} / {data['_language']}."
            )
        menu = await self.menu_result(ctx.author.id, kind, obj, data, stars)
        if menu is None:
            await ctx.send("No images are installed for this hero.")
            return
        await send_result(ctx, menu.result, view=menu.view)

    async def menu_result(self, author_id, kind, obj, data, stars=None):
        if kind == "story":
            labels = (
                ["Hero"]
                + [k.upper() for k in ("uw", "sw") if k in data]
                + ["UT" + k for k in data.get("uts", {})]
            )
            choices = [(label, label) for label in labels]
        elif kind == "perk":
            choices = [
                (f"{obj}'s perks", "hero"),
                (f"{data['info']['class']}'s perks", "class"),
            ]
        elif kind == "uts":
            choices = [("All UTs", "All")] + [("UT" + k, k) for k in data["uts"]]
        else:
            choices = [
                (p.stem, str(p)) for p in sorted(Path(data["costumes"]).glob("*.png"))
            ]
        if not choices:
            return None

        async def render(choice):
            return await self.render(kind, obj, data, stars=stars, choice=choice)

        view = ChoiceView(author_id, choices, render)
        result = await render(choices[0][1])
        if isinstance(result, list):
            result = discord.Embed(
                title=f"{obj} {kind.title()}",
                description="Choose a section below to read its pages.",
                colour=settings.EMBED_COLOR,
            )
        return MenuResult(result, view)

    @commands.hybrid_command(
        name="heroes", aliases=["hero"], description="List heroes, optionally by class"
    )
    @app_commands.autocomplete(version=version_autocomplete)
    async def heroes(self, ctx, *, lst: str | None = None, version: str | None = None):
        if lst and lst.lower() not in ("list", "all"):
            await self.lookup(ctx, lst, "info", version=version)
            return
        dataset = selected_data(ctx, version)
        classes = {}
        for name, data in dataset.entities().items():
            classes.setdefault(data["info"]["class"], []).append(name)
        embed = discord.Embed(title="Heroes", colour=settings.EMBED_COLOR)
        for cls, names in classes.items():
            embed.add_field(name=cls, value=", ".join(names), inline=False)
        if not classes:
            embed.description = "No heroes are available in this version."
        await ctx.send(embed=stamp(embed, dataset))

    @commands.hybrid_command(
        name="boss",
        aliases=["bosses", "gr", "gc", "wb", "trial", "shakmeh"],
        description="List bosses or show boss information",
    )
    @app_commands.autocomplete(version=version_autocomplete)
    async def boss(self, ctx, *, lst: str | None = None, version: str | None = None):
        if lst and lst.lower() not in ("list", "all"):
            await self.lookup(ctx, lst, "info", version=version)
            return
        dataset = selected_data(ctx, version)
        names = list(dataset.entities("bosses"))
        embed = discord.Embed(
            title="Bosses",
            description="\n".join(names) or "No bosses are available in this version.",
            colour=settings.EMBED_COLOR,
        )
        await ctx.send(embed=stamp(embed, dataset))

    @commands.hybrid_command(description="Show NPC hero bonuses")
    @app_commands.autocomplete(version=version_autocomplete)
    async def npc(self, ctx, *, version: str | None = None):
        dataset = selected_data(ctx, version)
        if dataset.version != "legacy" or dataset.language != "en":
            raise DataUnavailable(f"NPC bonus data is unavailable in {dataset.label}.")
        await ctx.send(
            embed=discord.Embed(
                title=f"NPC Heroes Effect - {dataset.label}",
                description="Gladi: Arena Shop UW discount (10%)\nJuno: Hero's Inn discount (40%)\nLoman: Orvel Castle Shop discount (10%)\nMay: Normal shop discount (25%)\nNicky: One extra daily Stockade Vault Key\nVeronica: Guild Shop discount (10%)\nHanus: Allied ATK Speed +100 in Guild War\nDosarta: Two extra repeat Tower of Challenge artifact pieces\nTalisha: Central Neighborhood Ruby discount (30%)\nValance: Technomagic crafting material discount (15%)",
                colour=settings.EMBED_COLOR,
            )
        )

    @commands.hybrid_command(
        name="info",
        aliases=["information", "infor"],
        description="Show hero or boss information",
    )
    @app_commands.autocomplete(version=version_autocomplete)
    async def info(self, ctx, *, hero: str | None = None, version: str | None = None):
        await self.lookup(ctx, hero, "info", version=version)

    @commands.hybrid_command(
        name="skill", aliases=["skills"], description="Show hero or boss skills"
    )
    @app_commands.autocomplete(version=version_autocomplete)
    async def skill(self, ctx, *, hero: str | None = None, version: str | None = None):
        await self.lookup(ctx, hero, "skill", version=version)

    @commands.hybrid_command(description="Show hero or equipment stories")
    @app_commands.autocomplete(version=version_autocomplete)
    async def story(self, ctx, *, hero: str, version: str | None = None):
        await self.lookup(ctx, hero, "story", version=version)

    @commands.hybrid_command(
        name="books",
        aliases=["book", "upgrade"],
        description="Show skill book upgrades",
    )
    @app_commands.autocomplete(version=version_autocomplete)
    async def books(self, ctx, *, hero: str | None = None, version: str | None = None):
        await self.lookup(ctx, hero, "book", version=version)

    @commands.hybrid_command(
        name="perks",
        aliases=["perk", "tran", "trans", "transcend"],
        description="Show hero and class perks",
    )
    @app_commands.autocomplete(version=version_autocomplete)
    async def perks(self, ctx, *, hero: str | None = None, version: str | None = None):
        await self.lookup(ctx, hero, "perk", version=version)

    @commands.hybrid_command(aliases=["weapon"], description="Show a unique weapon")
    @app_commands.autocomplete(version=version_autocomplete)
    async def uw(
        self,
        ctx,
        hero: str | None = None,
        stars: Annotated[int | None, commands.Range[int, 0, 5]] = None,
        *,
        version: str | None = None,
    ):
        await self.lookup(ctx, hero, "uw", stars, version=version)

    @commands.hybrid_command(
        aliases=["us", "soul", "soulstone"], description="Show soul weapon information"
    )
    @app_commands.autocomplete(version=version_autocomplete)
    async def sw(self, ctx, *, hero: str | None = None, version: str | None = None):
        await self.lookup(ctx, hero, "sw", version=version)

    @commands.hybrid_command(
        aliases=["ut", "treasure", "treasures"], description="Browse unique treasures"
    )
    @app_commands.autocomplete(version=version_autocomplete)
    async def uts(
        self,
        ctx,
        hero: str | None = None,
        stars: Annotated[int | None, commands.Range[int, 0, 5]] = None,
        *,
        version: str | None = None,
    ):
        await self.lookup(ctx, hero, "uts", stars, version=version)

    @commands.hybrid_command(
        aliases=["splash", "sa", "ls", "loading", "screen"],
        description="Show hero splash artwork",
    )
    @app_commands.autocomplete(version=version_autocomplete)
    async def splashart(
        self, ctx, *, hero: str | None = None, version: str | None = None
    ):
        await self.lookup(ctx, hero, "splashart", version=version)

    @commands.hybrid_command(
        aliases=["va", "vs"], description="Show visual splash artwork"
    )
    @app_commands.autocomplete(version=version_autocomplete)
    async def visual(self, ctx, *, hero: str | None = None, version: str | None = None):
        await self.lookup(ctx, hero, "visual", version=version)

    @commands.hybrid_command(
        name="cos",
        aliases=["costume", "costumes", "skin", "skins"],
        description="Browse hero costumes",
    )
    @app_commands.autocomplete(version=version_autocomplete)
    async def cos(self, ctx, *, hero: str | None = None, version: str | None = None):
        await self.lookup(ctx, hero, "cos", version=version)

    @commands.hybrid_command(
        name="costume_theme", description="Browse costumes matching a theme"
    )
    @app_commands.autocomplete(version=version_autocomplete)
    async def costume_theme(self, ctx, *, theme: str, version: str | None = None):
        await ctx.defer()
        dataset = selected_data(ctx, version)
        choices = []
        for name, data in dataset.entities().items():
            choices.extend(
                (f"{name} - {image.stem}", (name, data, str(image)))
                for image in sorted(Path(data["costumes"]).glob("*.png"))
                if theme.casefold() in image.stem.casefold()
            )
        if not choices:
            await ctx.send("No matching costume images are installed.")
            return

        async def render(choice):
            obj, data, image = choice
            return await self.render("cos", obj, data, choice=image)

        view = ChoiceView(
            ctx.author.id, choices, render, placeholder="Choose a costume"
        )
        await send_result(ctx, await render(choices[0][1]), view=view)

    @commands.hybrid_command(
        name="ut1", aliases=["treasure1"], description="Show unique treasure 1"
    )
    @app_commands.autocomplete(version=version_autocomplete)
    async def ut1(
        self,
        ctx,
        hero: str | None = None,
        stars: Annotated[int | None, commands.Range[int, 0, 5]] = None,
        *,
        version: str | None = None,
    ):
        await self.lookup(ctx, hero, "ut1", stars, version=version)

    @commands.hybrid_command(
        name="ut2", aliases=["treasure2"], description="Show unique treasure 2"
    )
    @app_commands.autocomplete(version=version_autocomplete)
    async def ut2(
        self,
        ctx,
        hero: str | None = None,
        stars: Annotated[int | None, commands.Range[int, 0, 5]] = None,
        *,
        version: str | None = None,
    ):
        await self.lookup(ctx, hero, "ut2", stars, version=version)

    @commands.hybrid_command(
        name="ut3", aliases=["treasure3"], description="Show unique treasure 3"
    )
    @app_commands.autocomplete(version=version_autocomplete)
    async def ut3(
        self,
        ctx,
        hero: str | None = None,
        stars: Annotated[int | None, commands.Range[int, 0, 5]] = None,
        *,
        version: str | None = None,
    ):
        await self.lookup(ctx, hero, "ut3", stars, version=version)

    @commands.hybrid_command(
        name="ut4", aliases=["treasure4"], description="Show unique treasure 4"
    )
    @app_commands.autocomplete(version=version_autocomplete)
    async def ut4(
        self,
        ctx,
        hero: str | None = None,
        stars: Annotated[int | None, commands.Range[int, 0, 5]] = None,
        *,
        version: str | None = None,
    ):
        await self.lookup(ctx, hero, "ut4", stars, version=version)


async def setup(bot):
    cog = Heroes(bot)
    await bot.add_cog(cog)
    add_routes(
        bot,
        cog,
        {
            "skills hero": "skill",
            "skills boss": "skill",
            "book": "books",
            "perk": "perks",
            "ut": "uts",
            "costumes hero": "cos",
            "costumes theme": "costume_theme",
            "profile": "info",
        },
    )
