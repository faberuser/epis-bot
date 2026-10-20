"""Shared hero and boss embed rendering."""

import discord

from .find_obj import get_color
from .game_data import GameData
from .menus import asset, text_pages


class HeroRendering:
    get_color = staticmethod(get_color)

    def get_info(self, obj, data, boss=None):
        info = data["info"]
        hidden_fields = {"thumbnail", "class"} if boss else {"thumbnail", "story_"}
        sections = []
        for key, value in info.items():
            if key in hidden_fields:
                continue
            if key == "story" and not boss:
                sections.append(f"\n**Story**\n{value}")
            else:
                sections.append(f"**{key.replace('_', ' ').title()}**: {value}\n")
        embed = discord.Embed(
            title=f"{obj} Info",
            description="".join(sections),
            colour=self.get_color(info["class"].lower()),
        )
        name = f"{obj}_ico.png".replace(" ", "_")
        file = asset(info["thumbnail"], filename=name)
        embed.set_thumbnail(url=f"attachment://{name}")
        return embed, file

    def get_skills(self, obj, data, boss=None):
        colour = self.get_color(data["info"]["class"].lower())
        skills = data["skills"]
        groups = (
            skills.items()
            if any(key.startswith("page") for key in skills)
            else [(None, skills)]
        )
        embeds = []
        for group, entries in groups:
            sections = []
            for number, skill in entries.items():
                details = "".join(
                    f" [{label}: {skill[key]}]"
                    for key, label in (("cost", "Cost"), ("cooldown", "Cooldown"))
                    if skill.get(key) is not None
                )
                sections.append(
                    f"**Skill {number}: {skill['name']}{details}**\n{skill['description']}\n\n"
                )
            title = f"{obj} Skills" + (f" ({group.title()})" if group else "")
            embeds.extend(text_pages(title, "".join(sections), colour))
        if len(embeds) > 1:
            for number, embed in enumerate(embeds, 1):
                embed.set_footer(text=f"Page {number}/{len(embeds)}")
        return embeds

    def get_books(self, obj, data):
        sections = []
        for skill, upgrades in data["books"].items():
            details = "".join(
                f"[UPGRADE {level}] {effect}\n" for level, effect in upgrades.items()
            )
            sections.append(f"**Skill {skill}**\n{details}\n")
        return discord.Embed(
            title=f"{obj} Books",
            description="".join(sections),
            colour=self.get_color(data["info"]["class"].lower()),
        )

    def get_class_perk(self, cls, clr, version=None, language=None):
        dataset = GameData(version, language)
        tiers = (
            ("T1", dataset.table("classes/General.json")["perks"]["t1"]),
            ("T2", dataset.table(f"classes/{cls}.json")["perks"]["t2"]),
        )
        sections = []
        for tier, perks in tiers:
            details = "".join(
                f"**{name}**\n{effect}\n" for name, effect in perks.items()
            )
            sections.append(f"**{tier} Perks**\n{details}")
        description = "\n".join(sections)
        embed = discord.Embed(
            title=f"{cls} Perks",
            description=description,
            colour=clr,
        )
        return embed, description

    def get_uw(self, obj, data, stars: int | None = None):
        weapon = data["uw"]
        description = f"{weapon['name']}\n\n{weapon['description']}\n\n"
        if stars is not None:
            description = "☆☆☆☆☆".replace("☆", "★", stars) + "\n" + description
            for token, values in weapon["value"].items():
                description = description.replace(f"({token})", values[str(stars)], 1)
        else:
            for token, values in weapon["value"].items():
                suffix = ": " + ", ".join(values.values()) if values else ""
                description += f"({token}){suffix}\n"
        embed = discord.Embed(
            title=f"{obj} UW",
            description=description,
            colour=self.get_color(data["info"]["class"].lower()),
        )
        name = f"{obj}_uw.png".replace(" ", "_")
        file = asset(weapon["thumbnail"], filename=name)
        embed.set_thumbnail(url=f"attachment://{name}")
        return embed, file

    def get_sw(self, obj, data):
        weapon = data["sw"]
        description = (
            f"**Requirement**: {weapon['requirement']}\n\n{weapon['description']}"
        )
        for level, effect in weapon["advancement"].items():
            description += f"\n\n**Advancement {level}**\n{effect}"
        embed = discord.Embed(
            title=f"{obj} SW",
            description=description,
            colour=self.get_color(data["info"]["class"].lower()),
        )
        embed.set_footer(
            text=f"Cooldown: {weapon['cooldown']} | Uses: {weapon['uses']}"
        )
        file = None
        thumbnail = weapon.get("thumbnail")
        if thumbnail:
            name = f"{obj}_sw.png".replace(" ", "_")
            file = asset(thumbnail, filename=name)
            if file:
                embed.set_thumbnail(url=f"attachment://{name}")
        return embed, file

    def get_sa_vs(self, obj, data, cate):
        embed = discord.Embed(
            title=f"{obj} {cate.title()}",
            colour=self.get_color(data["info"]["class"].lower()),
        )
        name = f"{obj}_{cate}.png".replace(" ", "_")
        file = asset(data[cate], filename=name)
        embed.set_image(url=f"attachment://{name}")
        return embed, file
