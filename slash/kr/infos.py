import discord, json, asyncio, os, asyncio, re
import re as research
from fuzzywuzzy import process
from discord.ext import commands

from discord_slash.utils.manage_components import create_actionrow, spread_to_rows, create_button, wait_for_component, create_select, create_select_option
from discord_slash.utils.manage_commands import create_choice, create_option
from discord_slash.model import ButtonStyle
from discord_slash import cog_ext, SlashContext

from ..utils import paginator, check_permisison, embed_file, find_obj
from config import config

client = discord.Client()


class Heroes(commands.Cog):
    def __init__(self, client):
        self.client = client
        self.paginator = paginator.Paginator(self.client).paginator
        self.check = check_permisison.view_channels
        self.embed_file = embed_file.embed_file
        self.find = find_obj.find
        self.find_boss = find_obj.find_boss
        self.find_ = find_obj.find_
        self.get_color = find_obj.get_color


    @cog_ext.cog_slash(name='heroes', 
                    description='Hero Commands',
                    guild_ids=config.guild_ids) # slash list king's raid heroes command
    async def heroes_(self, ctx: SlashContext):
        lst = list
        class_ = {
            'archer': '',
            'assassin': '',
            'knight': '',
            'mechanic': '',
            'priest': '',
            'warrior': '',
            'wizard': ''
        }
        with open('./data/emojis.json') as e:
            re = json.load(e)
        emojis = re['heroes']
        for obj in os.listdir('./data/kr/table-data/heroes'):
            with open(f'./data/kr/table-data/heroes/{obj}') as f:
                re = json.load(f)
            emj = emojis[obj[:-5]]
            if re['infos']['class'] == 'Archer':
                class_['archer']+=(emj+' ')
            elif re['infos']['class'] == 'Assassin':
                class_['assassin']+=(emj+' ')
            elif re['infos']['class'] == 'Knight':
                class_['knight']+=(emj+' ')
            elif re['infos']['class'] == 'Mechanic':
                class_['mechanic']+=(emj+' ')
            elif re['infos']['class'] == 'Priest':
                class_['priest']+=(emj+' ')
            elif re['infos']['class'] == 'Warrior':
                class_['warrior']+=(emj+' ')
            elif re['infos']['class'] == 'Wizard':
                class_['wizard']+=(emj+' ')
        embed = discord.Embed(title="King's Raid Heroes", colour=config.embed_color)
        for cls_ in class_:
            embed.add_field(name=cls_.capitalize(), value=class_[cls_])
        if self.check(ctx.guild, ctx.channel) == True:
            await ctx.send(embed=embed, hidden=True)
        else:
            await ctx.send(embed=embed)


    @cog_ext.cog_slash(name='npc',
                    description="Give NPC Hero's Effect",
                    guild_ids=config.guild_ids)
    async def npc_(self, ctx: SlashContext): # slash npc command
        embed = discord.Embed(
            title="NPC Heroes Effect",
            description=("`Gladi` - Gives a 10% discount on Unique Weapons in the Arena Shop.\n"+
            "`Juno` - You may purchase Hero's Inn item(s) at a 40% discount.\n"+
            "`Loman` - You may purchase Orvel Castle Shop items with a 10% discount.\n"+
            "`May` - May's normal shop items can be bought at a 25% discounted rate.\n"+
            "`Nicky` - Increases daily recharge for Stockade Vault Key by 1.\n"+
            "`Veronica` - Gives a 10% discount on items in the Guild Shop.\n"+
            "`Hanus` - Increases ATK Speed of all allies by 100 in the Guild War.\n"+
            "`Dosarta` - By completing repeat mission for Tower of Challenge, you can obtain 2 more Artifacts Pieces as a reward. Loot Booster will be applied to additional rewards.\n"+
            "`Talisha` - Gives a 30% discount on Ruby consumption at Orvel Central Neighborhood.\n"+
            "`Valance` - Material cost is discounted by 15% for Technomagic Crafting."),
            colour=config.embed_color,
        )
        if self.check(ctx.guild, ctx.channel) == True:
            await ctx.send(embed=embed, hidden=True)
        else:
            await ctx.send(embed=embed)


    # @cog_ext.cog_slash(
    #                 name='infos',
    #                 description="Give Hero or Boss's Basic Infomations",
    #                 guild_ids=config.guild_ids,
    #                 options=[
    #                     create_option(
    #                         name="input",
    #                         description="Input a hero or boss",
    #                         option_type=3,
    #                         required=True
    #                     ),
    #                 ])
    # async def infos(self, ctx: SlashContext, *, input: str):
    #     if self.check(ctx.guild, ctx.channel) == True:
    #         await ctx.send(content="This command can't be used here...", hidden=True)
    #     else:
    #         re, data, boss = self.find_(input)
    #         embed, file = self.get_infos(re, data)
    #         await ctx.send(embed=embed, file=file)


    @cog_ext.cog_subcommand(
                    base='infos',
                    name='hero',
                    description="Give Hero's Basic Infomations",
                    guild_ids=config.guild_ids,
                    options=[
                        create_option(
                            name="hero",
                            description="Input a hero",
                            option_type=3,
                            required=True
                        ),
                    ]) # slash hero's info command
    async def infos_hero(self, ctx: SlashContext, *, hero: str):
        await self.infos_hero_s(ctx, hero)

    @cog_ext.cog_slash(
                    name='info',
                    description="An aliase of infos hero",
                    guild_ids=config.guild_ids,
                    options=[
                        create_option(
                            name="hero",
                            description="Input a hero",
                            option_type=3,
                            required=True
                        ),
                    ]) # slash hero's info command
    async def info_hero(self, ctx: SlashContext, *, hero: str):
        await self.infos_hero_s(ctx, hero)

    async def infos_hero_s(self, ctx, hero):
        if self.check(ctx.guild, ctx.channel) == True:
            await ctx.send(content="This command can't be used here...", hidden=True)
        else:
            re, data = self.find(hero)
            embed, file = self.get_infos(re, data)
            await ctx.send(embed=embed, file=file)


    @cog_ext.cog_subcommand(
                    base='infos',
                    name='boss',
                    description="Give Boss's Basic Infomations",
                    guild_ids=config.guild_ids,
                    options=[
                        create_option(
                            name="boss",
                            description="Input a boss",
                            option_type=3,
                            required=True
                        ),
                    ]) # slash boss's info command
    async def infos_boss(self, ctx: SlashContext, *, boss: str):
        if self.check(ctx.guild, ctx.channel) == True:
            await ctx.send(content="This command can't be used here...", hidden=True)
        else:
            re, data = self.find_boss(boss)
            embed, file = self.get_infos(re, data)
            await ctx.send(embed=embed, file=file)


    @cog_ext.cog_slash(
                    name='story',
                    description="Give Hero's item's story",
                    guild_ids=config.guild_ids,
                    options=[
                        create_option(
                            name="hero",
                            description="Input a hero",
                            option_type=3,
                            required=True
                        ),
                    ]) # slash story command
    async def story(self, ctx: SlashContext, *, hero: str):
        if self.check(ctx.guild, ctx.channel) == True:
            await ctx.send(content="This command can't be used here...", hidden=True)
        else:
            re, data = self.find(hero)
            await self.get_story(re, data, ctx)


    # @cog_ext.cog_slash(
    #                 name='skills',
    #                 description="Give Hero or Boss's Skills",
    #                 guild_ids=config.guild_ids,
    #                 options=[
    #                     create_option(
    #                         name="input",
    #                         description="Input a hero or boss",
    #                         option_type=3,
    #                         required=True
    #                     )
    #                 ])
    # async def skills(self, ctx: SlashContext, *, input: str):
    #     re, data, boss = self.find_(input)
    #     embeds = self.get_skills(re, data, boss)
    #     if self.check(ctx.guild, ctx.channel) == True:
    #         if len(embeds) > 1:
    #             await ctx.send(content="This command can't be used here...", hidden=True)
    #         else:
    #             await ctx.send(embed=embeds[0], hidden=True)
    #     else:
    #         if len(embeds) > 1:
    #             await self.paginator(ctx, embeds)
    #         else:
    #             await ctx.send(embed=embeds[0])


    @cog_ext.cog_subcommand(
                    base='skills',
                    name='hero',
                    description="Give Hero's Skills",
                    guild_ids=config.guild_ids,
                    options=[
                        create_option(
                            name="hero",
                            description="Input a hero",
                            option_type=3,
                            required=True
                        )
                    ]) # slash hero's skill command
    async def skills_hero(self, ctx: SlashContext, *, hero: str):
        await self.skills_hero_s(ctx, hero)

    @cog_ext.cog_slash(
                    name='skill',
                    description="An aliase of skills hero",
                    guild_ids=config.guild_ids,
                    options=[
                        create_option(
                            name="hero",
                            description="Input a hero",
                            option_type=3,
                            required=True
                        )
                    ]) # slash hero's skill command
    async def skill_hero(self, ctx: SlashContext, *, hero: str):
        await self.skills_hero_s(ctx, hero)

    async def skills_hero_s(self, ctx, hero):
        re, data = self.find(hero)
        embeds = self.get_skills(re, data)
        if self.check(ctx.guild, ctx.channel) == True:
            if len(embeds) > 1:
                await ctx.send(content="This command can't be used here...", hidden=True)
            else:
                await ctx.send(embed=embeds[0], hidden=True)
        else:
            if len(embeds) > 1:
                await self.paginator(ctx, embeds)
            else:
                await ctx.send(embed=embeds[0])


    @cog_ext.cog_subcommand(
                    base='skills',
                    name='boss',
                    description="Give Boss's Skills",
                    guild_ids=config.guild_ids,
                    options=[
                        create_option(
                            name="boss",
                            description="Input or boss",
                            option_type=3,
                            required=True
                        )
                    ]) # slash boss's skill command
    async def skills_boss(self, ctx: SlashContext, *, boss: str):
        re, data = self.find_boss(boss)
        embeds = self.get_skills(re, data)
        if self.check(ctx.guild, ctx.channel) == True:
            if len(embeds) > 1:
                await ctx.send(content="This command can't be used here...", hidden=True)
            else:
                await ctx.send(embed=embeds[0], hidden=True)
        else:
            if len(embeds) > 1:
                await self.paginator(ctx, embeds)
            else:
                await ctx.send(embed=embeds[0])


    @cog_ext.cog_slash(name='books',
                    description="Give Hero's Books",
                    guild_ids=config.guild_ids,
                    options=[
                        create_option(
                            name="hero",
                            description="Input a hero",
                            option_type=3,
                            required=True
                        )
                    ]) # slash books command
    async def books_(self, ctx: SlashContext, *, hero: str):
        await self.book_s(ctx, hero)

    @cog_ext.cog_slash(name='book',
                    description="An aliase of books",
                    guild_ids=config.guild_ids,
                    options=[
                        create_option(
                            name="hero",
                            description="Input a hero",
                            option_type=3,
                            required=True
                        )
                    ]) # slash books command
    async def book_(self, ctx: SlashContext, *, hero: str):
        await self.book_s(ctx, hero)

    async def book_s(self, ctx, hero):
        re, data = self.find(hero)
        embed = self.get_books(re, data)
        if self.check(ctx.guild, ctx.channel) == True:
            await ctx.send(embed=embed, hidden=True)
        else:
            await ctx.send(embed=embed)


    @cog_ext.cog_slash(name='perks',
                    description="Give Hero's Perks",
                    guild_ids=config.guild_ids,
                    options=[
                        create_option(
                            name="hero",
                            description="Input a hero",
                            option_type=3,
                            required=True
                        )
                    ]) # slash perks command
    async def perks_(self, ctx: SlashContext, *, hero: str):
        await self.perk_s(ctx, hero)

    @cog_ext.cog_slash(name='perk',
                    description="An aliase of perks",
                    guild_ids=config.guild_ids,
                    options=[
                        create_option(
                            name="hero",
                            description="Input a hero",
                            option_type=3,
                            required=True
                        )
                    ]) # slash perks command
    async def perk_(self, ctx: SlashContext, *, hero: str):
        await self.perk_s(ctx, hero)

    async def perk_s(self, ctx, hero):
        re, data = self.find(hero)
        await self.get_perks(re, data, ctx)


    @cog_ext.cog_slash(name='uw',
                    description="Give Hero's Unique Weapon",
                    guild_ids=config.guild_ids,
                    options=[
                        create_option(
                            name="hero",
                            description="Input a hero",
                            option_type=3,
                            required=True
                        ),
                        create_option(
                            name="stars",
                            description="Input stars",
                            option_type=4,
                            required=False,
                            choices=[
                                create_choice(name=0, value=0),
                                create_choice(name=1, value=1),
                                create_choice(name=2, value=2),
                                create_choice(name=3, value=3),
                                create_choice(name=4, value=4),
                                create_choice(name=5, value=5),
                            ]
                        )
                    ]) # slash uw command
    async def uw_(self, ctx: SlashContext, *, hero: str, stars: int=None):
        if self.check(ctx.guild, ctx.channel) == True:
            await ctx.send(content="This command can't be used here...", hidden=True)
        else:
            re, data = self.find(hero)
            embed, file = self.get_uw(re, data, stars)
            await ctx.send(embed=embed, file=file)


    @cog_ext.cog_slash(name='sw',
                    description="Give Hero's Soul Weapon",
                    guild_ids=config.guild_ids,
                    options=[
                        create_option(
                            name="hero",
                            description="Input a hero",
                            option_type=3,
                            required=True
                        )
                    ]) # slash sw command
    async def sw_(self, ctx: SlashContext, *, hero: str):
        if self.check(ctx.guild, ctx.channel) == True:
            await ctx.send(content="This command can't be used here...", hidden=True)
        else:
            re, data = self.find(hero)
            embed, file = self.get_sw(re, data)
            await ctx.send(embed=embed, file=file)


    @cog_ext.cog_slash(name='uts',
                    description="Give Hero's Unique Treasures",
                    guild_ids=config.guild_ids,
                    options=[
                        create_option(
                            name="hero",
                            description="Input a hero",
                            option_type=3,
                            required=True
                        ),
                        create_option(
                            name="stars",
                            description="Input stars",
                            option_type=4,
                            required=False,
                            choices=[
                                create_choice(name=0, value=0),
                                create_choice(name=1, value=1),
                                create_choice(name=2, value=2),
                                create_choice(name=3, value=3),
                                create_choice(name=4, value=4),
                                create_choice(name=5, value=5),
                            ]
                        )
                    ]) # slash uts command
    async def uts_(self, ctx: SlashContext, *, hero: str, stars:int=None):
        await self.ut_s(ctx, hero, stars)

    @cog_ext.cog_slash(name='ut',
                    description="An aliase of uts",
                    guild_ids=config.guild_ids,
                    options=[
                        create_option(
                            name="hero",
                            description="Input a hero",
                            option_type=3,
                            required=True
                        ),
                        create_option(
                            name="stars",
                            description="Input stars",
                            option_type=4,
                            required=False,
                            choices=[
                                create_choice(name=0, value=0),
                                create_choice(name=1, value=1),
                                create_choice(name=2, value=2),
                                create_choice(name=3, value=3),
                                create_choice(name=4, value=4),
                                create_choice(name=5, value=5),
                            ]
                        )
                    ]) # slash uts command
    async def ut_(self, ctx: SlashContext, *, hero: str, stars:int=None):
        await self.ut_s(ctx, hero, stars)

    async def ut_s(self, ctx, hero, stars):
        re, data = self.find(hero)
        if hero.startswith('1'):
            if self.check(ctx.guild, ctx.channel) == True:
                await ctx.send(content="This command can't be used here...", hidden=True)
            else:
                embed, file = await self.get_uts(re, data, 1, stars=stars)
                await ctx.send(embed=embed, file=file)
        elif hero.startswith('2'):
            if self.check(ctx.guild, ctx.channel) == True:
                await ctx.send(content="This command can't be used here...", hidden=True)
            else:
                embed, file = await self.get_uts(re, data, 2, stars=stars)
                await ctx.send(embed=embed, file=file)
        elif hero.startswith('3'):
            if self.check(ctx.guild, ctx.channel) == True:
                await ctx.send(content="This command can't be used here...", hidden=True)
            else:
                embed, file = await self.get_uts(re, data, 3, stars=stars)
                await ctx.send(embed=embed, file=file)
        elif hero.startswith('4'):
            if self.check(ctx.guild, ctx.channel) == True:
                await ctx.send(content="This command can't be used here...", hidden=True)
            else:
                embed, file = await self.get_uts(re, data, 4, stars=stars)
                await ctx.send(embed=embed, file=file)
        else:
            await self.get_uts(re, data, ctx=ctx, stars=stars)


    @cog_ext.cog_slash(name='ut1',
                    description="Give Hero's Unique Treasure 1 (Skill 1)",
                    guild_ids=config.guild_ids,
                    options=[
                        create_option(
                            name="hero",
                            description="Input a hero",
                            option_type=3,
                            required=True
                        ),
                        create_option(
                            name="stars",
                            description="Input stars",
                            option_type=4,
                            required=False,
                            choices=[
                                create_choice(name=0, value=0),
                                create_choice(name=1, value=1),
                                create_choice(name=2, value=2),
                                create_choice(name=3, value=3),
                                create_choice(name=4, value=4),
                                create_choice(name=5, value=5),
                            ]
                        )
                    ]) # slash ut 1 command
    async def ut1_(self, ctx: SlashContext, *, hero: str, stars:int=None):
        if self.check(ctx.guild, ctx.channel) == True:
            await ctx.send(content="This command can't be used here...", hidden=True)
        else:
            re, data = self.find(hero)
            embed, file = await self.get_uts(re, data, 1, stars=stars)
            await ctx.send(embed=embed, file=file)


    @cog_ext.cog_slash(name='ut2',
                    description="Give Hero's Unique Treasure 2 (Skill 2)",
                    guild_ids=config.guild_ids,
                    options=[
                        create_option(
                            name="hero",
                            description="Input a hero",
                            option_type=3,
                            required=True
                        ),
                        create_option(
                            name="stars",
                            description="Input stars",
                            option_type=4,
                            required=False,
                            choices=[
                                create_choice(name=0, value=0),
                                create_choice(name=1, value=1),
                                create_choice(name=2, value=2),
                                create_choice(name=3, value=3),
                                create_choice(name=4, value=4),
                                create_choice(name=5, value=5),
                            ]
                        )
                    ]) # slash ut 2 command
    async def ut2_(self, ctx: SlashContext, *, hero: str, stars:int=None):
        if self.check(ctx.guild, ctx.channel) == True:
            await ctx.send(content="This command can't be used here...", hidden=True)
        else:
            re, data = self.find(hero)
            embed, file = await self.get_uts(re, data, 2, stars=stars)
            await ctx.send(embed=embed, file=file)


    @cog_ext.cog_slash(name='ut3',
                    description="Give Hero's Unique Treasure 3 (Skill 3)",
                    guild_ids=config.guild_ids,
                    options=[
                        create_option(
                            name="hero",
                            description="Input a hero",
                            option_type=3,
                            required=True
                        ),
                        create_option(
                            name="stars",
                            description="Input stars",
                            option_type=4,
                            required=False,
                            choices=[
                                create_choice(name=0, value=0),
                                create_choice(name=1, value=1),
                                create_choice(name=2, value=2),
                                create_choice(name=3, value=3),
                                create_choice(name=4, value=4),
                                create_choice(name=5, value=5),
                            ]
                        )
                    ]) # slash ut 3 command
    async def ut3_(self, ctx: SlashContext, *, hero: str, stars:int=None):
        if self.check(ctx.guild, ctx.channel) == True:
            await ctx.send(content="This command can't be used here...", hidden=True)
        else:
            re, data = self.find(hero)
            embed, file = await self.get_uts(re, data, 3, stars=stars)
            await ctx.send(embed=embed, file=file)


    @cog_ext.cog_slash(name='ut4',
                    description="Give Hero's Unique Treasure 4 (Skill 4)",
                    guild_ids=config.guild_ids,
                    options=[
                        create_option(
                            name="hero",
                            description="Input a hero",
                            option_type=3,
                            required=True
                        ),
                        create_option(
                            name="stars",
                            description="Input stars",
                            option_type=4,
                            required=False,
                            choices=[
                                create_choice(name=0, value=0),
                                create_choice(name=1, value=1),
                                create_choice(name=2, value=2),
                                create_choice(name=3, value=3),
                                create_choice(name=4, value=4),
                                create_choice(name=5, value=5),
                            ]
                        )
                    ]) # slash ut 4 command
    async def ut4_(self, ctx: SlashContext, *, hero: str, stars:int=None):
        if self.check(ctx.guild, ctx.channel) == True:
            await ctx.send(content="This command can't be used here...", hidden=True)
        else:
            re, data = self.find(hero)
            embed, file = await self.get_uts(re, data, 4, stars=stars)
            await ctx.send(embed=embed, file=file)


    @cog_ext.cog_slash(name='splashart',
                    description="Give Hero's Splashart",
                    guild_ids=config.guild_ids,
                    options=[
                        create_option(
                            name="hero",
                            description="Input a hero",
                            option_type=3,
                            required=True
                        )
                    ]) # slash splashart command
    async def splashart_(self, ctx: SlashContext, *, hero: str):
        if self.check(ctx.guild, ctx.channel) == True:
            await ctx.send(content="This command can't be used here...", hidden=True)
        else:
            re, data = self.find(hero)
            embed, file = self.get_sa_vs(re, data, 'splashart')
            await ctx.send(embed=embed, file=file)


    @cog_ext.cog_slash(name='visual',
                    description="Give Hero's Visual",
                    guild_ids=config.guild_ids,
                    options=[
                        create_option(
                            name="hero",
                            description="Input a hero",
                            option_type=3,
                            required=True
                        )
                    ]) # slash visual splashart command
    async def visual_(self, ctx: SlashContext, *, hero: str):
        if self.check(ctx.guild, ctx.channel) == True:
            await ctx.send(content="This command can't be used here...", hidden=True)
        else:
            re, data = self.find(hero)
            try:
                embed, file = self.get_sa_vs(re, data, 'visual')
                await ctx.send(embed=embed, file=file)
            except:
                await ctx.send(f"Can't get Visual of `{hero}`.", hidden=True)


    @cog_ext.cog_subcommand(
                    base='costumes',
                    name='hero',
                    description="Give horny Hero's costumes",
                    guild_ids=config.guild_ids,
                    options=[
                        create_option(
                            name="hero",
                            description="Input a hero",
                            option_type=3,
                            required=True
                        )
                    ]) # slash hero's costumes command
    async def costumes_hero(self, ctx: SlashContext, *, hero: str):
        await self.costumes_hero_s(ctx, hero)

    @cog_ext.cog_slash(
                    name='cos',
                    description="An aliase of costumes hero",
                    guild_ids=config.guild_ids,
                    options=[
                        create_option(
                            name="hero",
                            description="Input a hero",
                            option_type=3,
                            required=True
                        )
                    ]) # slash hero's costumes command
    async def cos_hero(self, ctx: SlashContext, *, hero: str):
        await self.costumes_hero_s(ctx, hero)

    async def costumes_hero_s(self, ctx, hero):
        re, data = self.find(hero)
        await self.get_costumes(re, data, ctx)


    @cog_ext.cog_subcommand(
                    base='costumes',
                    name='theme',
                    description="Give horny Hero's costumes by theme",
                    guild_ids=config.guild_ids,
                    options=[
                        create_option(
                            name="theme",
                            description="Input a costumes theme",
                            option_type=3,
                            required=True,
                            choices=[
                                create_choice(name='Basic', value='Basic'), # 0
                                create_choice(name='Butler', value='Butler'), # 1
                                create_choice(name='Casual', value='Casual'), # 2
                                create_choice(name='Christmas', value='Christmas'), # 3
                                create_choice(name='Corrupted Swimsuit', value='Corrupted Swimsuit'), # 4
                                create_choice(name='Dessert', value='Dessert'), # 5
                                create_choice(name='Fallen', value='Fallen'), # 6
                                create_choice(name='Frozen', value='Frozen'), # 7
                                create_choice(name='Halloween', value='Halloween'), # 8
                                create_choice(name='Halloween Swimsuit', value='Halloween Swimsuit'), # 9
                                create_choice(name='Idol', value='Idol'), # 10
                                create_choice(name='League of Honor', value='League of Honor'), # 11
                                create_choice(name='Limited', value='Limited'), # 12
                                create_choice(name='Maid', value='Maid'), # 13
                                create_choice(name='Pajama', value='Pajama'), # 14
                                create_choice(name='School', value='School'), # 15
                                create_choice(name='Sci-fi', value='Sci-fi'), # 16
                                create_choice(name='Sincere', value='Sincere'), # 17
                                create_choice(name='Sport', value='Sport'), # 18
                                create_choice(name='Substory', value='Substory'), # 19
                                create_choice(name='Swimsuit', value='Swimsuit'), # 20
                                create_choice(name='Wedding', value='Wedding'), # 21
                                create_choice(name='Wedding Swimsuit', value='Wedding Swimsuit'), # 22
                                create_choice(name='Working', value='Working'), # 23
                                create_choice(name='World', value='World'), # 24
                            ])
                    ]) # slash theme costumes command
    async def costumes_theme(self, ctx: SlashContext, *, theme: str):
        if self.check(ctx.guild, ctx.channel) == True:
            await ctx.send(content="This command can't be used here...", hidden=True)
            return
        await ctx.defer()
        ls = []
        for hero in os.listdir('./data/kr/table-data/heroes'):
            with open(f'./data/kr/table-data/heroes/{hero}') as f:
                re_ = json.load(f)['costumes']
                for costume in os.listdir(re_):
                    if theme in costume:
                        ls.append((hero[:-5], costume[:-4]))
        len_ = len(ls)
        if len_ > 25:
            def chunks(lst, n):
                for i in range(0, len(lst), n):
                    yield lst[i:i + n]
            menus = []
            for hero in ls:
                with open(f'./data/emojis.json') as r:
                    emoji = json.load(r)['heroes'][hero[0]]
                splited = re.split('(\d+)', emoji)
                emoji_ = self.client.get_emoji(int(splited[1]))
                cos = hero[1]
                if '%' in cos:
                    cos = cos.replace('%', '?')
                menus.append(create_select_option(label=hero[0], description=cos, emoji=emoji_, value=(hero[0]+' - '+hero[1])))
            menus_s = list(chunks(menus, 25))
            count = 1
            menus_rows = []
            for menus_ in menus_s:
                menus_rows.append(create_actionrow(create_select(menus_, placeholder=f'Choose your hero (Page {count}/{len(menus_s)})', max_values=1)))
                count+=1
            max_ = len(menus_rows)

            buttons = [create_button(style=ButtonStyle.blue, label="\u25c0"), create_button(style=ButtonStyle.blue, label="\u25b6")]
            button_row = create_actionrow(*buttons)

            index = 0
            count = 0
            msg = None
            _embed_ = None

            def embed():
                embed = discord.Embed(title=f'{theme} Costumes Theme', colour=config.embed_color)
                return embed

            while True:
                try:
                    action_rows = [menus_rows[index], button_row]
                    if count == 0:
                        _embed_ = embed()
                        msg = await ctx.send(embed=_embed_, components=action_rows)
                        count+=1
                    interactions: ComponentContext = await wait_for_component(self.client, components=action_rows, timeout=120.0, check=lambda x: x.author_id == ctx.author.id)
                    try:
                        selected_hero = interactions.selected_options[0].split(' - ')
                        with open(f'./data/kr/table-data/heroes/{selected_hero[0]}.json') as f:
                            data = json.load(f)
                        clr = self.get_color(data['infos']['class'].lower())
                        name = selected_hero[0] + ' ' + selected_hero[1] + '.png'
                        if ' ' in name:
                            name = name.replace(' ', '_')
                        if '?' in name:
                            name = name.replace('?', '')
                        if '%' in name:
                            name = name.replace('%', '')
                        if '(' in name or ')' in name:
                            name = (name.replace('(', '_')).replace(')', '_')
                        title = f'{selected_hero[0]} - {selected_hero[1]}'
                        if '%' in title:
                            title = title.replace('%', '?')
                        file = discord.File(data['costumes']+f'/{selected_hero[1]}.png', filename=name)
                        embed_ = discord.Embed(title=title, colour=clr)
                        embed_.set_image(url=f'attachment://{name}')
                        _embed_ = await self.embed_file(self.client, embed_, file)
                        await interactions.edit_origin(embed=_embed_)
                    except:
                        if interactions.component['label'] == "\u25c0":
                            index -= 1
                            if index < 0:
                                index = max_ - 1
                        elif interactions.component['label'] == "\u25b6":
                            index += 1
                            if index == max_:
                                index = 0
                        await interactions.edit_origin(embed=_embed_, components=[menus_rows[index], button_row])
                except asyncio.TimeoutError:
                    await msg.edit(content='Timeout! Please try again.', components=None)
                    break
        else:
            menus = []
            for hero in ls:
                with open(f'./data/emojis.json') as r:
                    emoji = json.load(r)['heroes'][hero[0]]
                splited = re.split('(\d+)', emoji)
                emoji_ = self.client.get_emoji(int(splited[1]))
                cos = hero[1]
                if '%' in cos:
                    cos = cos.replace('%', '?')
                menus.append(create_select_option(label=hero[0], description=cos, emoji=emoji_, value=(hero[0]+' - '+hero[1])))
            action_row = create_actionrow(create_select(menus, placeholder='Choose your hero', max_values=1))
            embed = discord.Embed(title=f'{theme} Costumes Theme', colour=config.embed_color)
            msg = await ctx.send(embed=embed, components=[action_row])
            while True:
                try:
                    menus: ComponentContext = await wait_for_component(self.client, components=action_row, timeout=120.0, check=lambda x: x.author_id == ctx.author.id)
                    selected_hero = menus.selected_options[0].split(' - ')
                    with open(f'./data/kr/table-data/heroes/{selected_hero[0]}.json') as f:
                        data = json.load(f)
                    clr = self.get_color(data['infos']['class'].lower())
                    name = selected_hero[0] + ' ' + selected_hero[1] + '.png'
                    if ' ' in name:
                        name = name.replace(' ', '_')
                    if '?' in name:
                        name = name.replace('?', '')
                    if '%' in name:
                        name = name.replace('%', '')
                    if '(' in name or ')' in name:
                        name = (name.replace('(', '_')).replace(')', '_')
                    title = f'{selected_hero[0]} - {selected_hero[1]}'
                    if '%' in title:
                        title = title.replace('%', '?')
                    file = discord.File(data['costumes']+f'/{selected_hero[1]}.png', filename=name)
                    embed_ = discord.Embed(title=title, colour=clr)
                    embed_.set_image(url=f'attachment://{name}')
                    _embed_ = await self.embed_file(self.client, embed_, file)
                    await menus.edit_origin(embed=_embed_)
                except asyncio.TimeoutError:
                    await msg.edit(content='Timeout! Please try again.', components=None)
                    break


    def get_infos(self, obj, data, boss=None):
        clr = self.get_color(data['infos']['class'].lower())
        des = ''
        if boss:
            for info in data['infos']:
                if info == 'thumbnail':
                    continue
                elif info == 'class':
                    continue
                else:
                    des+='**'+info.title()+'**: '+data['infos'][info]+'\n'
        else:
            for info in data['infos']:
                if info == 'thumbnail':
                    continue
                elif info == 'story':
                    des+='\n**Story**'+'\n'+data['infos'][info]
                elif info == 'story_':
                    pass
                else:
                    des+='**'+info.title()+'**: '+data['infos'][info]+'\n'
        embed = discord.Embed(
            title=obj + ' Infos',
            description=des,
            colour=clr,
        )
        name = f'{obj}_ico.png'
        if ' ' in name:
            name = name.replace(' ', '_')
        file = discord.File(data['infos']['thumbnail'], filename=name)
        embed.set_thumbnail(url=f'attachment://{name}')
        return embed, file

    async def get_story(self, obj, data, ctx):
        clr = self.get_color(data['infos']['class'].lower())
        hero_story_ = discord.Embed(
            title=obj + ' Story',
            description=data['infos']['story_'],
            colour=clr,
        )
        name = f'{obj}_ico.png'
        name = name.replace(' ', '_')
        file = discord.File(data['infos']['thumbnail'], filename=name)
        hero_story_.set_thumbnail(url=f'attachment://{name}')
        hero_story = await self.embed_file(self.client, hero_story_, file)

        buttons_1 = [
            create_button(style=ButtonStyle.blue, label="Hero"),
            create_button(style=ButtonStyle.blue, label="UW"),
            create_button(style=ButtonStyle.blue, label="SW"),
            ]
        buttons_2 = [
            create_button(style=ButtonStyle.blue, label="UT1"),
            create_button(style=ButtonStyle.blue, label="UT2"),
            create_button(style=ButtonStyle.blue, label="UT3"),
            create_button(style=ButtonStyle.blue, label="UT4"),
            ]
        action_row_1 = create_actionrow(*buttons_1)
        action_row_2 = create_actionrow(*buttons_2)
        msg = await ctx.send(embed=hero_story, components=[action_row_1, action_row_2])

        while True:
            try:
                button_ctx: ComponentContext = await wait_for_component(self.client, components=[action_row_1, action_row_2], timeout=60.0, check=lambda x: x.author_id == ctx.author.id)
                if button_ctx.component['label'] == f"Hero":
                    await button_ctx.edit_origin(embed=hero_story)
                elif button_ctx.component['label'] == f"UW":
                    uw_story_ = discord.Embed(
                        title=obj + "'s UW Story",
                        description=data['uw']['story'],
                        colour=clr,
                    )
                    name = f'{obj}_uw.png'
                    name = name.replace(' ', '_')
                    file = discord.File(data['uw']['thumbnail'], filename=name)
                    uw_story_.set_thumbnail(url=f'attachment://{name}')
                    uw_story = await self.embed_file(self.client, uw_story_, file)
                    await button_ctx.edit_origin(embed=uw_story)
                elif button_ctx.component['label'] == f"SW":
                    sw_story_ = discord.Embed(
                        title=obj + "'s SW Story",
                        description=data['sw']['story'],
                        colour=clr,
                    )
                    name = f'{obj}_sw.png'
                    name = name.replace(' ', '_')
                    file = discord.File(data['sw']['thumbnail'], filename=name)
                    sw_story_.set_thumbnail(url=f'attachment://{name}')
                    sw_story = await self.embed_file(self.client, sw_story_, file)
                    await button_ctx.edit_origin(embed=sw_story)
                elif button_ctx.component['label'] == f"UT1":
                    ut1_story_ = discord.Embed(
                        title=obj + "'s UT1 Story",
                        description=data['uts']['1']['story'],
                        colour=clr,
                    )
                    name = f'{obj}_ut1.png'
                    name = name.replace(' ', '_')
                    file = discord.File(data['uts']['1']['thumbnail'], filename=name)
                    ut1_story_.set_thumbnail(url=f'attachment://{name}')
                    ut1_story = await self.embed_file(self.client, ut1_story_, file)
                    await button_ctx.edit_origin(embed=ut1_story)
                elif button_ctx.component['label'] == f"UT2":
                    ut2_story_ = discord.Embed(
                        title=obj + "'s UT2 Story",
                        description=data['uts']['2']['story'],
                        colour=clr,
                    )
                    name = f'{obj}_ut2.png'
                    name = name.replace(' ', '_')
                    file = discord.File(data['uts']['2']['thumbnail'], filename=name)
                    ut2_story_.set_thumbnail(url=f'attachment://{name}')
                    ut2_story = await self.embed_file(self.client, ut2_story_, file)
                    await button_ctx.edit_origin(embed=ut2_story)
                elif button_ctx.component['label'] == f"UT3":
                    ut3_story_ = discord.Embed(
                        title=obj + "'s UT3 Story",
                        description=data['uts']['3']['story'],
                        colour=clr,
                    )
                    name = f'{obj}_ut3.png'
                    name = name.replace(' ', '_')
                    file = discord.File(data['uts']['4']['thumbnail'], filename=name)
                    ut3_story_.set_thumbnail(url=f'attachment://{name}')
                    ut3_story = await self.embed_file(self.client, ut3_story_, file)
                    await button_ctx.edit_origin(embed=ut3_story)
                elif button_ctx.component['label'] == f"UT4":
                    ut4_story_ = discord.Embed(
                        title=obj + "'s UT4 Story",
                        description=data['uts']['4']['story'],
                        colour=clr,
                    )
                    name = f'{obj}_ut4.png'
                    name = name.replace(' ', '_')
                    file = discord.File(data['uts']['4']['thumbnail'], filename=name)
                    ut4_story_.set_thumbnail(url=f'attachment://{name}')
                    ut4_story = await self.embed_file(self.client, ut4_story_, file)
                    await button_ctx.edit_origin(embed=ut4_story)
            except asyncio.TimeoutError:
                buttons = []
                for row in msg.components:
                    for button in row['components']:
                        button['disabled'] = True
                        buttons.append(button)
                action_row = spread_to_rows(*buttons, max_in_row=5)
                await msg.edit(content='Timeout! Please try again.', components=action_row)
                break


    def get_skills(self, obj, data, boss=None):
        clr = self.get_color(data['infos']['class'].lower())
        des = ''
        embeds = []
        for page in data['skills']:
            if page.startswith('page'):
                for skill in data['skills'][page]:
                    try:
                        try:
                            des+=('**Skill '+skill+': '+data['skills'][page][skill]['name']+' [Cost: '+
                                data['skills'][page][skill]['cost']+'] [Cooldown: '+data['skills'][page][skill]['cooldown']+']**\n'+
                                data['skills'][page][skill]['description']+'\n\n')
                        except:
                            des+=('**Skill '+skill+': '+data['skills'][page][skill]['name']+' [Cooldown: '+data['skills'][page][skill]['cooldown']+']**\n'+
                                data['skills'][page][skill]['description']+'\n\n')
                    except:
                        des+=('**Skill '+skill+': '+data['skills'][page][skill]['name']+'**\n'+
                            data['skills'][page][skill]['description']+'\n\n')
                embed = discord.Embed(
                    title=obj + ' Skills (' + page.title() + ')',
                    description=des,
                    colour=clr,
                    )
                embeds.append(embed)
                des = ''
            else:
                for skill in data['skills']:
                    try:
                        des+=('**Skill '+skill+': '+data['skills'][skill]['name']+' [Cost: '+
                            data['skills'][skill]['cost']+'] [Cooldown: '+data['skills'][skill]['cooldown']+']**\n'+
                            data['skills'][skill]['description']+'\n\n')
                    except:
                        des+=('**Skill '+skill+': '+data['skills'][skill]['name']+'**\n'+
                            data['skills'][skill]['description']+'\n\n')
                embed = discord.Embed(
                    title=obj + ' Skills',
                    description=des,
                    colour=clr,
                )
                embeds.append(embed)
                break
        count = 0
        if len(embeds) >= 2:
            for embed in embeds:
                embeds[count].set_footer(text=f'Page {count+1}/{len(embeds)}')
                count+=1
        return embeds

    def get_books(self, obj, data):
        clr = self.get_color(data['infos']['class'].lower())
        des = ''
        for book in data['books']:
            des+='**Skill '+book+'**\n'
            for upgrade in data['books'][book]:
                des+='[UPGRADE '+upgrade+'] '+data['books'][book][upgrade]+'\n'
            des+='\n'
        embed = discord.Embed(
            title=obj + ' Books',
            description=des,
            colour=clr,
        )
        return embed

    async def get_perks(self, obj, data, ctx):
        clr = self.get_color(data['infos']['class'].lower())
        des = '**T3 Perks**\n'
        for skill in data['perks']['t3']:
            des+='**Skill '+skill+'**\n'
            for perk in data['perks']['t3'][skill]:
                des+='['+perk.upper()+'] '+data['perks']['t3'][skill][perk]['effect']+'\n'
        des+='\n**T5 Perks**\n'
        for perk in data['perks']['t5']:
            des+='['+perk.upper()+'] '+data['perks']['t5'][perk]['effect']+'\n'
        hero_embed = discord.Embed(
            title=obj + ' Perks',
            description=des,
            colour=clr,
        )

        if self.check(ctx.guild, ctx.channel) == True:
            await ctx.send(embed=hero_embed, hidden=True)
            return
        else:
            buttons = [create_button(style=ButtonStyle.green, label=f"{obj}'s Perks"), create_button(style=ButtonStyle.red, label=f"{data['infos']['class']}'s Perks")]
            action_row = create_actionrow(*buttons)
            msg = await ctx.send(embed=hero_embed, components=[action_row])

        while True:
            try:
                button_ctx: ComponentContext = await wait_for_component(self.client, components=action_row, timeout=60.0, check=lambda x: x.author_id == ctx.author.id)
                if button_ctx.component['label'] == f"{obj}'s Perks":
                    await button_ctx.edit_origin(embed=hero_embed)
                elif button_ctx.component['label'] == f"{data['infos']['class']}'s Perks":
                    class_embed, des = self.get_class_perk(data['infos']['class'], clr)
                    await button_ctx.edit_origin(embed=class_embed)
            except asyncio.TimeoutError:
                buttons = []
                for row in msg.components:
                    for button in row['components']:
                        button['disabled'] = True
                        buttons.append(button)
                action_row = create_actionrow(*buttons)
                await msg.edit(content='Timeout! Please try again.', components=[action_row])
                break

    def get_class_perk(self, cls, clr):
        des = '**T1 Perks**\n'
        with open(f'./data/kr/table-data/classes/General.json') as f:
            t1 = json.load(f)['perks']['t1']
        for perk in t1:
            des+='**'+perk+'**\n'+t1[perk]+'\n'
        des+='\n**T2 Perks**\n'
        with open(f'./data/kr/table-data/classes/{cls}.json') as f:
            t2 = json.load(f)['perks']['t2']
        for perk in t2:
            des+='**'+perk+'**\n'+t2[perk]+'\n' 
        embed = discord.Embed(
            title=cls + ' Perks',
            description=des,
            colour=clr,
        )
        return embed, des

    def get_uw(self, obj, data, stars:int=None):
        clr = self.get_color(data['infos']['class'].lower())
        des = ''
        des = data['uw']['name']+'\n\n'+data['uw']['description']+'\n\n'
        if stars is not None:
            des = '☆☆☆☆☆'.replace('☆', '★', stars)+'\n'+des
            for value in data['uw']['value']:
                des = des.replace(f'({value})', data['uw']['value'][value][str(stars)], 1)
        else:
            for value in data['uw']['value']:
                des+='('+value+'): '
                for vl in data['uw']['value'][value]:
                    des+=data['uw']['value'][value][vl]+', '
                des=des[:-2]+'\n'
        embed = discord.Embed(
            title=obj + ' UW',
            description=des,
            colour=clr,
        )
        name = f'{obj}_uw.png'
        if ' ' in name:
            name = name.replace(' ', '_')
        file = discord.File(data['uw']['thumbnail'], filename=name)
        embed.set_thumbnail(url=f'attachment://{name}')
        return embed, file

    def get_sw(self, obj, data):
        clr = self.get_color(data['infos']['class'].lower())
        des = ''
        des = '**Requirement**: '+data['sw']['requirement']+'\n\n'+data['sw']['description']
        for adv in data['sw']['advancement']:
            des+='\n\n**Advancement '+adv+'**\n'+data['sw']['advancement'][adv]
        embed = discord.Embed(
            title=obj + ' SW',
            description=des,
            colour=clr,
        )
        embed.set_footer(text=f"Cooldown: {data['sw']['cooldown']} | Uses: {data['sw']['uses']}")
        file = None
        try:
            name = f'{obj}_sw.png'
            if ' ' in name:
                name = name.replace(' ', '_')
            file = discord.File(data['sw']['thumbnail'], filename=name)
            embed.set_thumbnail(url=f'attachment://{name}')
        except:
            pass
        return embed, file

    def get_sa_vs(self, obj, data, cate):
        clr = self.get_color(data['infos']['class'].lower())
        embed = discord.Embed(
            title=obj + ' ' + cate.title(),
            colour=clr,
        )
        name = f'{obj}_{cate}.png'
        if ' ' in name:
            name = name.replace(' ', '_')
        file = discord.File(data[cate], filename=name)
        embed.set_image(url=f'attachment://{name}')
        return embed, file
    
    async def get_costumes(self, obj, data, ctx):
        if self.check(ctx.guild, ctx.channel) == True:
            await ctx.send(content="This command can't be used here...", hidden=True)
            return
        clr = self.get_color(data['infos']['class'].lower())
        ls = []
        ls_ = []
        num = 0
        for costumes_ in os.listdir(data['costumes']):
            ls.append(costumes_)
        for cos_ in sorted(ls):
            if '%' in cos_:
                cos_ = cos_.replace('%', '?')
            ls_.append(cos_[:-4])
            num+=1

        def embed_(cos):
            embed = discord.Embed(title=obj + ' - ' + cos,
                                colour=clr)
            name = f'{obj}_{cos}.png'
            if ' ' in name:
                name = name.replace(' ', '_')
            if '?' in name:
                name = name.replace('?', '')
            if '(' in name or ')' in name:
                name = (name.replace('(', '_')).replace(')', '_')
            if '?' in cos:
                cos = cos.replace('?', "%")
            file = discord.File(data['costumes']+f'/{cos}.png', filename=name)
            embed.set_image(url=f'attachment://{name}')
            return embed, file, cos

        buttons = []
        for i in range(num):
            buttons.append(create_button(style=ButtonStyle.blue, label=ls_[i]))
        action_row = spread_to_rows(*buttons, max_in_row=5)

        embed = discord.Embed(title=f'{obj} Costumes', 
                                colour=clr)
        msg = await ctx.send(embed=embed, components=action_row)

        while True:
            try:
                button_ctx: ComponentContext = await wait_for_component(self.client, components=action_row, timeout=60.0, check=lambda x: x.author_id == ctx.author.id)
                embed, file, cos = embed_(button_ctx.component['label'])
                _embed_ = await self.embed_file(self.client, embed, file)
                await button_ctx.edit_origin(embed=_embed_)
            except asyncio.TimeoutError:
                buttons = []
                for row in msg.components:
                    for button in row['components']:
                        button['disabled'] = True
                        buttons.append(button)
                action_row = spread_to_rows(*buttons, max_in_row=5)
                await msg.edit(content='Timeout! Please try again.', components=action_row)
                break

    async def get_uts(self, obj, data, num:int=None, ctx=None, stars:int=None):
        clr = self.get_color(data['infos']['class'].lower())
        des = ''
        if stars is not None:
            des = '☆☆☆☆☆'.replace('☆', '★', stars)+'\n'
        if num is None and ctx is not None:
            for ut in data['uts']:
                des+='**UT'+ut+' (Skill '+ut+')**: '+data['uts'][ut]['name']+'\n'+data['uts'][ut]['description']+'\n\n'
                if stars is not None:
                    for value in data['uts'][ut]['value']:
                        des = des.replace(f'({value})', data['uts'][ut]['value'][value][str(stars)], 1)
                else:
                    for value in data['uts'][ut]['value']:
                        des+='('+value+'): '
                        for vl in data['uts'][ut]['value'][value]:
                            des+=data['uts'][ut]['value'][value][vl]+', '
                        des=des[:-2]+'\n'
                    des+='\n'
            embed = discord.Embed(
                title=obj + ' UTs',
                description=des,
                colour=clr,
            )
            embed.set_footer(text="Read the UT name or description and CAREFULLY compare with the ingame UT.")

            if self.check(ctx.guild, ctx.channel) == True:
                await ctx.send(embed=embed, hidden=True)
                return
            else:
                buttons = [create_button(style=ButtonStyle.blue, label='UT1'),
                        create_button(style=ButtonStyle.blue, label='UT2'),
                        create_button(style=ButtonStyle.blue, label='UT3'),
                        create_button(style=ButtonStyle.blue, label='UT4'),
                        create_button(style=ButtonStyle.blue, label='UTs')]
                action_row = create_actionrow(*buttons)
                msg = await ctx.send(embed=embed, components=[action_row])

            while True:
                try:
                    button_ctx: ComponentContext = await wait_for_component(self.client, components=action_row, timeout=60.0, check=lambda x: x.author_id == ctx.author.id)
                    label = (button_ctx.component['label'])
                    async def edit_(num):
                        embed, file = await self.get_uts(obj, data, num, stars=stars)
                        _embed_ = await self.embed_file(self.client, embed, file)
                        await button_ctx.edit_origin(embed=_embed_)
                    if label == 'UT1':
                        await edit_(1)
                    elif label == 'UT2':
                        await edit_(2)
                    elif label == 'UT3':
                        await edit_(3)
                    elif label == 'UT4':
                        await edit_(4)
                    elif label == 'UTs':
                        embed = await self.get_uts(obj, data, 5, stars=stars)
                        await button_ctx.edit_origin(embed=embed)
                except asyncio.TimeoutError:
                    buttons = []
                    for row in msg.components:
                        for button in row['components']:
                            button['disabled'] = True
                            buttons.append(button)
                    action_row = create_actionrow(*buttons)
                    await msg.edit(content='Timeout! Please try again.', components=[action_row])
                    break

        elif num == 5:
            for ut in data['uts']:
                des+='**UT'+ut+' (Skill '+ut+')**: '+data['uts'][ut]['name']+'\n'+data['uts'][ut]['description']+'\n\n'
                if stars is not None:
                    for value in data['uts'][ut]['value']:
                        des = des.replace(f'({value})', data['uts'][ut]['value'][value][str(stars)], 1)
                else:
                    for value in data['uts'][ut]['value']:
                        des+='('+value+'): '
                        for vl in data['uts'][ut]['value'][value]:
                            des+=data['uts'][ut]['value'][value][vl]+', '
                        des=des[:-2]+'\n'
                    des+='\n'
            embed = discord.Embed(
                title=obj + ' UTs',
                description=des,
                colour=clr,
            )
            embed.set_footer(text="Read the UT name or description and CAREFULLY compare with the ingame UT.")
            return embed

        else:
            des += '**UT'+str(num)+' (Skill '+str(num)+')**: '+data['uts'][str(num)]['name']+'\n'+data['uts'][str(num)]['description']+'\n\n'
            if stars is not None:
                for value in data['uts'][str(num)]['value']:
                    des = des.replace(f'({value})', data['uts'][str(num)]['value'][value][str(stars)], 1)
            else:
                for value in data['uts'][str(num)]['value']:
                    des+='('+value+'): '
                    for vl in data['uts'][str(num)]['value'][value]:
                        des+=data['uts'][str(num)]['value'][value][vl]+', '
                    des=des[:-2]+'\n'
            embed = discord.Embed(
                title=obj + ' UT' + str(num),
                description=des,
                colour=clr,
            )
            name = f'{obj}_ut{str(num)}.png'
            if ' ' in name:
                name = name.replace(' ', '_')
            file = discord.File(data['uts'][str(num)]['thumbnail'], filename=name)
            embed.set_thumbnail(url=f'attachment://{name}')
            embed.set_footer(text="Read the UT name, description or thumbnail and CAREFULLY compare with the ingame UT.")
            return embed, file



class TM_Gear(commands.Cog):
    def __init__(self, client):
        self.client = client
        self.check = check_permisison.view_channels


    @cog_ext.cog_subcommand(
                    base='technomagic',
                    name='gear',
                    description='Give 4 pieces of Technoagic Gear effect',
                    guild_ids=config.guild_ids,
                    options=[
                        create_option(
                            name="boss",
                            description="Input a boss name",
                            option_type=3,
                            required=True,
                            choices=[
                                create_choice(name="Galgoria (Perseverance)", value="Galgoria Gear"),
                                create_choice(name="Siegfried (Hope)", value="Siegfried Gear"),
                                create_choice(name="Ascalon (Authority)", value="Ascalon Gear"),
                            ]
                        ),
                        create_option(
                            name="class_",
                            description="Input class of hero",
                            option_type=3,
                            required=False,
                            choices=[
                                create_choice(name="Knight", value="Knight Gear"),
                                create_choice(name="Warrior", value="Warrior Gear"),
                                create_choice(name="Assassin", value="Assassin Gear"),
                                create_choice(name="Archer", value="Archer Gear"),
                                create_choice(name="Mechanic", value="Mechanic Gear"),
                                create_choice(name="Wizard", value="Wizard Gear"),
                                create_choice(name="Priest", value="Priest Gear"),
                            ]
                        )
                    ])
    async def tm_gear_(self, ctx: SlashContext, boss:str=None, class_:str=None):
        type = boss
        with open('./data/kr/table-data/technomagic_gear.json') as f:
            re = json.load(f)
        boss_type = []
        classes = ['<:knight:753231911861878864> `Knight`', '<:warrior:753231911991640074> `Warrior`', '<:assassin:753231911845101608> `Assassin`',
            '<:archer:753231911639449602> `Archer`', '<:mechanic:753231911882719313> `Mechanic`', '<:wizard:753231911857553490> `Wizard`', '<:priest:753231911857422417> `Priest`']
        des = ''
        for i in re:
            boss_type.append(i)
        type_ = process.extractOne(type, boss_type)
        tit = type_[0]
        clr = re[type_[0]]['colour']
        typed = re[type_[0]]['classes']
        if type is not None and class_ is None:
            count = 0
            for cls in typed:
                des += classes[count]+': '+re[type_[0]]['classes'][cls]+'\n'
                count+=1
        else:
            classes_ = []
            for cls in typed:
                classes_.append(cls)
            cls = process.extractOne(class_, classes_)
            matched = process.extractOne(cls[0], classes)
            des = matched[0]+': '+re[type_[0]]['classes'][cls[0]]
        embed = discord.Embed(title=tit, description=des, colour=discord.Colour.from_rgb(clr[0], clr[1], clr[2]))
        if self.check(ctx.guild, ctx.channel) == True:
            msg = await ctx.send(embed=embed, hidden=True)
        else:
            msg = await ctx.send(embed=embed)


def setup(client):
    client.add_cog(Heroes(client))
    client.add_cog(TM_Gear(client))
