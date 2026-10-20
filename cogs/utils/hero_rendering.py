"""Shared hero and boss embed rendering."""

import discord

from .find_obj import get_color
from .game_data import GameData
from .menus import asset, text_pages


class HeroRendering:
    get_color = staticmethod(get_color)

    def get_info(self, obj, data, boss=None):
        clr = self.get_color(data["info"]["class"].lower())
        des = ""
        if boss:
            for info in data["info"]:
                if info == "thumbnail" or info == "class":
                    continue
                else:
                    des += (
                        "**"
                        + info.replace("_", " ").title()
                        + "**: "
                        + data["info"][info]
                        + "\n"
                    )
        else:
            for info in data["info"]:
                if info == "thumbnail":
                    continue
                elif info == "story":
                    des += "\n**Story**" + "\n" + data["info"][info]
                elif info == "story_":
                    pass
                else:
                    des += (
                        "**"
                        + info.replace("_", " ").title()
                        + "**: "
                        + data["info"][info]
                        + "\n"
                    )
        embed = discord.Embed(
            title=obj + " Info",
            description=des,
            colour=clr,
        )
        name = f"{obj}_ico.png"
        if " " in name:
            name = name.replace(" ", "_")
        file = asset(data["info"]["thumbnail"], filename=name)
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
        clr = self.get_color(data["info"]["class"].lower())
        des = ""
        for book in data["books"]:
            des += "**Skill " + book + "**\n"
            for upgrade in data["books"][book]:
                des += (
                    "[UPGRADE " + upgrade + "] " + data["books"][book][upgrade] + "\n"
                )
            des += "\n"
        embed = discord.Embed(
            title=obj + " Books",
            description=des,
            colour=clr,
        )
        return embed

    def get_class_perk(self, cls, clr, version=None, language=None):
        dataset = GameData(version, language)
        des = "**T1 Perks**\n"
        t1 = dataset.table("classes/General.json")["perks"]["t1"]
        for perk in t1:
            des += "**" + perk + "**\n" + t1[perk] + "\n"
        des += "\n**T2 Perks**\n"
        t2 = dataset.table(f"classes/{cls}.json")["perks"]["t2"]
        for perk in t2:
            des += "**" + perk + "**\n" + t2[perk] + "\n"
        embed = discord.Embed(
            title=cls + " Perks",
            description=des,
            colour=clr,
        )
        return embed, des

    def get_uw(self, obj, data, stars: int | None = None):
        clr = self.get_color(data["info"]["class"].lower())
        des = ""
        des = data["uw"]["name"] + "\n\n" + data["uw"]["description"] + "\n\n"
        if stars is not None:
            des = "☆☆☆☆☆".replace("☆", "★", stars) + "\n" + des
            for value in data["uw"]["value"]:
                des = des.replace(
                    f"({value})", data["uw"]["value"][value][str(stars)], 1
                )
        else:
            for value in data["uw"]["value"]:
                des += "(" + value + "): "
                for vl in data["uw"]["value"][value]:
                    des += data["uw"]["value"][value][vl] + ", "
                des = des[:-2] + "\n"
        embed = discord.Embed(
            title=obj + " UW",
            description=des,
            colour=clr,
        )
        name = f"{obj}_uw.png"
        if " " in name:
            name = name.replace(" ", "_")
        file = asset(data["uw"]["thumbnail"], filename=name)
        embed.set_thumbnail(url=f"attachment://{name}")
        return embed, file

    def get_sw(self, obj, data):
        clr = self.get_color(data["info"]["class"].lower())
        des = ""
        des = (
            "**Requirement**: "
            + data["sw"]["requirement"]
            + "\n\n"
            + data["sw"]["description"]
        )
        for adv in data["sw"]["advancement"]:
            des += "\n\n**Advancement " + adv + "**\n" + data["sw"]["advancement"][adv]
        embed = discord.Embed(
            title=obj + " SW",
            description=des,
            colour=clr,
        )
        embed.set_footer(
            text=f"Cooldown: {data['sw']['cooldown']} | Uses: {data['sw']['uses']}"
        )
        file = None
        thumbnail = data["sw"].get("thumbnail")
        if thumbnail:
            name = f"{obj}_sw.png".replace(" ", "_")
            file = asset(thumbnail, filename=name)
            if file:
                embed.set_thumbnail(url=f"attachment://{name}")
        return embed, file

    def get_sa_vs(self, obj, data, cate):
        clr = self.get_color(data["info"]["class"].lower())
        embed = discord.Embed(
            title=obj + " " + cate.title(),
            colour=clr,
        )
        name = f"{obj}_{cate}.png"
        if " " in name:
            name = name.replace(" ", "_")
        file = asset(data[cate], filename=name)
        embed.set_image(url=f"attachment://{name}")
        return embed, file
