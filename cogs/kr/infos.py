import json
from pathlib import Path

import discord
from discord.ext import commands

from config import config
from ..utils import find_obj
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

    async def lookup(self, ctx, hero, kind, stars=None):
        if hero is None:
            await ctx.send(embed=self.help.info_embed({"info": "Infos", "skill": "Skills", "book": "Books", "perk": "Perks", "uw": "UWs", "sw": "SWs", "uts": "UTs", "splashart": "Splashart", "visual": "Visual", "cos": "Costumes"}.get(kind, "Heroes")))
            return
        if stars is not None and not 0 <= stars <= 5:
            raise commands.BadArgument("Stars must be between 0 and 5.")
        classes = ("Knight", "Warrior", "Assassin", "Archer", "Mechanic", "Wizard", "Priest")
        cls = next((name for name in classes if hero.casefold() == name.casefold()), None)
        if cls:
            if kind == "perk":
                await send_result(ctx, self.get_class_perk(cls, self.get_color(cls.lower()))[0])
                return
            choices = []
            for path in sorted(Path("data/kr/table-data/heroes").glob("*.json")):
                data = json.loads(path.read_text(encoding="utf-8"))
                if data["infos"]["class"] == cls:
                    choices.append((path.stem, path.stem))
            if not choices:
                await ctx.send("No heroes found in that class.")
                return
            async def render(value):
                obj, data, boss = find_obj.find_(value)
                if kind in ("story", "perk", "uts", "cos"):
                    return await self.menu_result(ctx.author.id, kind, obj, data, stars) or "No images are installed for this hero."
                return await self.render(kind, obj, data, stars=stars, boss=boss)
            view = ChoiceView(ctx.author.id, choices, render, placeholder="Choose your hero")
            await send_result(ctx, discord.Embed(title=f"{cls} heroes", colour=config.embed_color), view=view)
            return
        obj, data, boss = find_obj.find_(hero)
        if kind == "skill":
            await self.menus.pag(ctx, self.get_skills(obj, data, boss))
        elif kind in ("story", "perk", "uts", "cos"):
            await self.show_menu(ctx, kind, obj, data, stars)
        else:
            await send_result(ctx, await self.render(kind, obj, data, stars=stars, boss=boss))

    async def render(self, kind, obj, data, *, stars=None, boss=None, choice=None):
        if kind == "info":
            return self.get_infos(obj, data, boss)
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
        clr = self.get_color(data["infos"]["class"].lower())
        if kind == "perk":
            if choice == "class":
                return self.get_class_perk(data["infos"]["class"], clr)[0]
            sections = []
            for tier in ("t3", "t5"):
                sections.append("**" + tier.upper() + " Perks**")
                for key, value in data["perks"][tier].items():
                    if "effect" in value:
                        sections.append(f"[{key.upper()}] {value['effect']}")
                    else:
                        sections.append(f"**Skill {key}**")
                        sections.extend(f"[{side.upper()}] {perk['effect']}" for side, perk in value.items())
            return discord.Embed(title=f"{obj} Perks", description="\n".join(sections), colour=clr)
        if kind == "story":
            choice = choice or "Hero"
            if choice == "Hero":
                text = data["infos"].get("story_", data["infos"].get("story", "No story available."))
            elif choice.startswith("UT"):
                text = data["uts"][choice[-1]].get("story", "No story available.")
            else:
                text = data[choice.lower()].get("story", "No story available.")
            pages = text_pages(f"{obj} {choice} Story", text, clr)
            return pages if len(pages) > 1 else pages[0]
        if kind.startswith("ut"):
            number = kind[2:] if kind != "uts" else (choice or "All")
            sections = []
            treasures = data["uts"] if number == "All" else {number: data["uts"][number]}
            for key, treasure in treasures.items():
                text = treasure["description"]
                for token, values in treasure["value"].items():
                    if stars is not None:
                        text = text.replace(f"({token})", values[str(stars)], 1)
                    else:
                        text += f"\n({token}): " + ", ".join(values.values())
                sections.append(f"**UT{key}: {treasure['name']}**\n{text}")
            pages = text_pages(f"{obj} UTs" if number == "All" else f"{obj} UT{number}", "\n\n".join(sections), clr)
            if len(pages) > 1:
                return pages
            embed = pages[0]
            if number != "All":
                file = asset(data["uts"][number]["thumbnail"], filename=f"ut{number}.png")
                embed.set_thumbnail(url=f"attachment://ut{number}.png")
                return embed, file
            return embed
        if kind == "cos":
            path = Path(choice) if choice else next(iter(sorted(Path(data["costumes"]).glob("*.png"))), None)
            if path is None:
                return "No costume images are installed for this hero."
            embed = discord.Embed(title=f"{obj} - {path.stem}", colour=clr)
            embed.set_image(url="attachment://costume.png")
            return embed, asset(path, filename="costume.png")
        raise commands.BadArgument("Unknown hero information type.")

    async def show_menu(self, ctx, kind, obj, data, stars=None):
        menu = await self.menu_result(ctx.author.id, kind, obj, data, stars)
        if menu is None:
            await ctx.send("No images are installed for this hero.")
            return
        await send_result(ctx, menu.result, view=menu.view)

    async def menu_result(self, author_id, kind, obj, data, stars=None):
        if kind == "story":
            labels = ["Hero"] + [k.upper() for k in ("uw", "sw") if k in data] + ["UT" + k for k in data.get("uts", {})]
            choices = [(label, label) for label in labels]
        elif kind == "perk":
            choices = [(f"{obj}'s perks", "hero"), (f"{data['infos']['class']}'s perks", "class")]
        elif kind == "uts":
            choices = [("All UTs", "All")] + [("UT" + k, k) for k in data["uts"]]
        else:
            choices = [(p.stem, str(p)) for p in sorted(Path(data["costumes"]).glob("*.png"))]
        if not choices:
            return None
        async def render(choice):
            return await self.render(kind, obj, data, stars=stars, choice=choice)
        view = ChoiceView(author_id, choices, render)
        result = await render(choices[0][1])
        if isinstance(result, list):
            result = discord.Embed(title=f"{obj} {kind.title()}", description="Choose a section below to read its pages.", colour=config.embed_color)
        return MenuResult(result, view)

    @commands.hybrid_command(name="heroes", aliases=["hero"], description="List heroes, optionally by class")
    async def heroes(self, ctx, *, lst: str = None):
        if lst and lst.lower() not in ("list", "all"):
            await self.lookup(ctx, lst, "info")
            return
        classes = {}
        for path in sorted(Path("data/kr/table-data/heroes").glob("*.json")):
            data = json.loads(path.read_text(encoding="utf-8"))
            classes.setdefault(data["infos"]["class"], []).append(path.stem)
        embeds = [discord.Embed(title=cls, description=", ".join(names), colour=config.embed_color) for cls, names in classes.items()]
        await self.menus.pag(ctx, embeds)

    @commands.hybrid_command(description="Show NPC hero bonuses")
    async def npc(self, ctx):
        await ctx.send(embed=discord.Embed(title="NPC Heroes Effect", description="Gladi: Arena Shop UW discount (10%)\nJuno: Hero's Inn discount (40%)\nLoman: Orvel Castle Shop discount (10%)\nMay: Normal shop discount (25%)\nNicky: One extra daily Stockade Vault Key\nVeronica: Guild Shop discount (10%)\nHanus: Allied ATK Speed +100 in Guild War\nDosarta: Two extra repeat Tower of Challenge artifact pieces\nTalisha: Central Neighborhood Ruby discount (30%)\nValance: Technomagic crafting material discount (15%)", colour=config.embed_color))

    @commands.hybrid_command(name="info", aliases=["infos", "information", "infor"], description="Show hero or boss information")
    async def info(self, ctx, *, hero: str = None):
        await self.lookup(ctx, hero, "info")

    @commands.hybrid_command(name="skill", aliases=["skills"], description="Show hero or boss skills")
    async def skill(self, ctx, *, hero: str = None):
        await self.lookup(ctx, hero, "skill")

    @commands.hybrid_command(description="Show hero or equipment stories")
    async def story(self, ctx, *, hero: str):
        await self.lookup(ctx, hero, "story")

    @commands.hybrid_command(name="books", aliases=["book", "upgrade"], description="Show skill book upgrades")
    async def books(self, ctx, *, hero: str = None):
        await self.lookup(ctx, hero, "book")

    @commands.hybrid_command(name="perks", aliases=["perk", "tran", "trans", "transcend"], description="Show hero and class perks")
    async def perks(self, ctx, *, hero: str = None):
        await self.lookup(ctx, hero, "perk")

    @commands.hybrid_command(aliases=["weapon"], description="Show a unique weapon")
    async def uw(self, ctx, hero: str = None, stars: commands.Range[int, 0, 5] = None):
        await self.lookup(ctx, hero, "uw", stars)

    @commands.hybrid_command(aliases=["us", "soul", "soulstone"], description="Show soul weapon information")
    async def sw(self, ctx, *, hero: str = None):
        await self.lookup(ctx, hero, "sw")

    @commands.hybrid_command(aliases=["ut", "treasure", "treasures"], description="Browse unique treasures")
    async def uts(self, ctx, hero: str = None, stars: commands.Range[int, 0, 5] = None):
        await self.lookup(ctx, hero, "uts", stars)

    @commands.hybrid_command(aliases=["splash", "sa", "ls", "loading", "screen"], description="Show hero splash artwork")
    async def splashart(self, ctx, *, hero: str = None):
        await self.lookup(ctx, hero, "splashart")

    @commands.hybrid_command(aliases=["va", "vs"], description="Show visual splash artwork")
    async def visual(self, ctx, *, hero: str = None):
        await self.lookup(ctx, hero, "visual")

    @commands.hybrid_command(name="cos", aliases=["costume", "costumes", "skin", "skins"], description="Browse hero costumes")
    async def cos(self, ctx, *, hero: str = None):
        await self.lookup(ctx, hero, "cos")

    @commands.hybrid_command(name="costume_theme", description="Browse costumes matching a theme")
    async def costume_theme(self, ctx, *, theme: str):
        await ctx.defer()
        choices = []
        for path in sorted(Path("data/kr/table-data/heroes").glob("*.json")):
            data = json.loads(path.read_text(encoding="utf-8"))
            choices.extend((f"{path.stem} - {image.stem}", (path.stem, data, str(image))) for image in sorted(Path(data["costumes"]).glob("*.png")) if theme.casefold() in image.stem.casefold())
        if not choices:
            await ctx.send("No matching costume images are installed.")
            return
        async def render(choice):
            obj, data, image = choice
            return await self.render("cos", obj, data, choice=image)
        view = ChoiceView(ctx.author.id, choices, render, placeholder="Choose a costume")
        await send_result(ctx, await render(choices[0][1]), view=view)

    @commands.hybrid_command(name="boss", aliases=["bosses", "gr", "gc", "wb", "trial", "shakmeh"], description="List bosses")
    async def boss(self, ctx):
        await ctx.send(embed=self.help.info_embed("Bosses"))

    @commands.hybrid_command(name="tm_gear", aliases=["tm", "technomagic", "tmgear", "technomagicgear", "technomagic_gear"], description="Show Technomagic gear effects")
    async def tm_gear(self, ctx, boss: str = None, class_: str = None):
        data = json.loads(Path("data/kr/table-data/technomagic_gear.json").read_text(encoding="utf-8"))
        from fuzzywuzzy import process
        if boss is None:
            await ctx.send("Choose a boss: " + ", ".join(data))
            return
        match = process.extractOne(boss, list(data))[0]
        item = data[match]
        classes = item["classes"]
        if class_:
            key = process.extractOne(class_, list(classes))[0]
            classes = {key: classes[key]}
        await ctx.send(embed=discord.Embed(title=match, description="\n\n".join(f"**{key}**: {value}" for key, value in classes.items()), colour=discord.Colour.from_rgb(*item["colour"])))

    @commands.hybrid_command(name="ut1", aliases=["treasure1"], description="Show unique treasure 1")
    async def ut1(self, ctx, hero: str = None, stars: commands.Range[int, 0, 5] = None):
        await self.lookup(ctx, hero, "ut1", stars)

    @commands.hybrid_command(name="ut2", aliases=["treasure2"], description="Show unique treasure 2")
    async def ut2(self, ctx, hero: str = None, stars: commands.Range[int, 0, 5] = None):
        await self.lookup(ctx, hero, "ut2", stars)

    @commands.hybrid_command(name="ut3", aliases=["treasure3"], description="Show unique treasure 3")
    async def ut3(self, ctx, hero: str = None, stars: commands.Range[int, 0, 5] = None):
        await self.lookup(ctx, hero, "ut3", stars)

    @commands.hybrid_command(name="ut4", aliases=["treasure4"], description="Show unique treasure 4")
    async def ut4(self, ctx, hero: str = None, stars: commands.Range[int, 0, 5] = None):
        await self.lookup(ctx, hero, "ut4", stars)


async def setup(bot):
    cog = Heroes(bot)
    await bot.add_cog(cog)
    add_routes(bot, cog, {
        "infos hero": "info", "infos boss": "info", "skills hero": "skill", "skills boss": "skill",
        "book": "books", "perk": "perks", "ut": "uts", "costumes hero": "cos",
        "costumes theme": "costume_theme", "technomagic gear": "tm_gear", "profile": "info",
    })
