import discord, json, asyncio, os, traceback
import re as research
from fuzzywuzzy import process
from discord.ext import commands

from ..utils import paginator, info_embed, embed_file
from config import config

client = discord.Client()


class Heroes(commands.Cog):
    def __init__(self, client):
        self.client = client
        self.menus = paginator.Paginator(self.client)
        self.defaul_embed = info_embed.Info_Embed()
        self.embed_file = embed_file.embed_file

    @commands.command(aliases=["heroes"]) # hero commands
    async def hero(self, ctx, lst=None):
        if lst is None:
            embed = self.defaul_embed.info_embed('Heroes')
            await ctx.reply(embed=embed)
        else:
            if lst.lower() == 'list':
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
                await ctx.reply(embed=embed)
            else:
                chc = await self.check_class(ctx, lst, self.get_infos)
                if chc is False:
                    re, data, boss = self.find(lst)
                    embed, file = self.get_infos(re, data, boss)
                    await ctx.reply(embed=embed, file=file)

    @commands.command() # npc efects command
    async def npc(self, ctx):
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
        await ctx.reply(embed=embed)

    @commands.command(aliases=["info", "information", "infor"]) # infos command
    async def infos(self, ctx, *, hero: str = None):
        if hero is None:
            embed = self.defaul_embed.info_embed('Infos')
            await ctx.reply(embed=embed)
        else:
            chc = await self.check_class(ctx, hero, self.get_infos)
            if chc is False:
                re, data, boss = self.find(hero)
                embed, file = self.get_infos(re, data, boss)
                await ctx.reply(embed=embed, file=file)

    @commands.command(aliases=["skill"]) # skills command
    async def skills(self, ctx, *, hero: str = None):
        if hero is None:
            embed = self.defaul_embed.info_embed('Skills')
            await ctx.reply(embed=embed)
        else:
            chc = await self.check_class(ctx, hero, self.get_skills)
            if chc is False:
                re, data, boss = self.find(hero)
                embeds = self.get_skills(re, data, boss)
                if len(embeds) > 1:
                    await self.menus.pag(message=ctx.message, embeds=embeds)
                else:
                    await ctx.reply(embed=embeds[0])

    @commands.command(aliases=["book", "upgrade"]) # books command
    async def books(self, ctx, *, hero: str = None):
        if hero is None:
            embed = self.defaul_embed.info_embed('Books')
            await ctx.reply(embed=embed)
        else:
            chc = await self.check_class(ctx, hero, self.get_books)
            if chc is False:
                re, data, boss = self.find(hero)
                embed = self.get_books(re, data)
                await ctx.reply(embed=embed)

    @commands.command(aliases=["perk", "tran", "trans", "transcend"]) # perks command
    async def perks(self, ctx, *, hero: str = None):
        if hero is None:
            embed = self.defaul_embed.info_embed('Perks')
            await ctx.reply(embed=embed)
        else:
            chc = await self.check_class(ctx, hero, self.get_perks)
            if chc is False:
                re, data, boss = self.find(hero)
                await self.get_perks(re, data, ctx)

    @commands.command(aliases=["splash", "sa", "ls", "loading", "screen"]) #  splashart command
    async def splashart(self, ctx, *, hero: str = None):
        if hero is None:
            embed = self.defaul_embed.info_embed('Splashart')
            await ctx.reply(embed=embed)
        else:
            chc = await self.check_class(ctx, hero, self.get_sa_vs)
            if chc is False:
                re, data, boss = self.find(hero)
                embed, file = self.get_sa_vs(re, data, 'splashart')
                await ctx.reply(embed=embed, file=file)

    @commands.command(aliases=["va", "vs"]) # visual splashart command
    async def visual(self, ctx, *, hero: str = None):
        if hero is None:
            embed = self.defaul_embed.info_embed('Visual')
            await ctx.reply(embed=embed)
        else:
            chc = await self.check_class(ctx, hero, self.get_sa_vs)
            if chc is False:
                re, data, boss = self.find(hero)
                embed, file = self.get_sa_vs(re, data, 'visual')
                await ctx.reply(embed=embed, file=file)

    @commands.command(aliases=["weapon"]) # uw command
    async def uw(self, ctx, *, hero: str = None):
        if hero is None:
            embed = self.defaul_embed.info_embed('UW')
            await ctx.reply(embed=embed)
        else:
            chc = await self.check_class(ctx, hero, self.get_uw)
            if chc is False:
                re, data, boss = self.find(hero)
                embed, file = self.get_uw(re, data)
                await ctx.reply(embed=embed, file=file)

    @commands.command(aliases=["us", "soul", "soulstone"]) # sw command
    async def sw(self, ctx, *, hero: str = None):
        if hero is None:
            embed = self.defaul_embed.info_embed('SW')
            await ctx.reply(embed=embed)
        else:
            chc = await self.check_class(ctx, hero, self.get_sw)
            if chc is False:
                re, data, boss = self.find(hero)
                embed, file = self.get_sw(re, data)
                await ctx.reply(embed=embed, file=file)

    @commands.command(aliases=["treasure", "treasures", "ut"]) # uts command
    async def uts(self, ctx, *, hero: str = None):
        if hero is None:
            embed = self.defaul_embed.info_embed('UTs')
            await ctx.reply(embed=embed)
        else:
            re, data, boss = self.find(hero)
            if hero.startswith('1'):
                chc = await self.check_class(ctx, hero[1:], self.get_uts, 1)
                if chc is False:
                    embed, file = await self.get_uts(re, data, 1)
                    await ctx.reply(embed=embed, file=file)
            elif hero.startswith('2'):
                chc = await self.check_class(ctx, hero[1:], self.get_uts, 2)
                if chc is False:
                    embed, file = await self.get_uts(re, data, 2)
                    await ctx.reply(embed=embed, file=file)
            elif hero.startswith('3'):
                chc = await self.check_class(ctx, hero[1:], self.get_uts, 3)
                if chc is False:
                    embed, file = await self.get_uts(re, data, 3)
                    await ctx.reply(embed=embed, file=file)
            elif hero.startswith('4'):
                chc = await self.check_class(ctx, hero[1:], self.get_uts, 4)
                if chc is False:
                    embed, file = await self.get_uts(re, data, 4)
                    await ctx.reply(embed=embed, file=file)
            else:
                chc = await self.check_class(ctx, hero, self.get_uts)
                if chc is False:
                    await self.get_uts(re, data, ctx=ctx)

    @commands.command(aliases=["treasure1"]) # ut 1 command
    async def ut1(self, ctx, *, hero: str = None):
        if hero is None:
            embed = self.defaul_embed.info_embed('UT1')
            await ctx.reply(embed=embed)
        else:
            chc = await self.check_class(ctx, hero, self.get_uts, 1)
            if chc is False:
                re, data, boss = self.find(hero)
                embed, file = await self.get_uts(re, data, 1)
                await ctx.reply(embed=embed, file=file)

    @commands.command(aliases=["treasure2"]) # ut 2 command
    async def ut2(self, ctx, *, hero: str = None):
        if hero is None:
            embed = self.defaul_embed.info_embed('UT2')
            await ctx.reply(embed=embed)
        else:
            chc = await self.check_class(ctx, hero, self.get_uts, 2)
            if chc is False:
                re, data, boss = self.find(hero)
                embed, file = await self.get_uts(re, data, 2)
                await ctx.reply(embed=embed, file=file)

    @commands.command(aliases=["treasure3"]) # ut 3 command
    async def ut3(self, ctx, *, hero: str = None):
        if hero is None:
            embed = self.defaul_embed.info_embed('UT3')
            await ctx.reply(embed=embed)
        else:
            chc = await self.check_class(ctx, hero, self.get_uts, 3)
            if chc is False:
                re, data, boss = self.find(hero)
                embed, file = await self.get_uts(re, data, 3)
                await ctx.reply(embed=embed, file=file)

    @commands.command(aliases=["treasure4"]) # ut 4 command
    async def ut4(self, ctx, *, hero: str = None):
        if hero is None:
            embed = self.defaul_embed.info_embed('UT4')
            await ctx.reply(embed=embed)
        else:
            chc = await self.check_class(ctx, hero, self.get_uts, 4)
            if chc is False:
                re, data, boss = self.find(hero)
                embed, file = await self.get_uts(re, data, 4)
                await ctx.reply(embed=embed, file=file)

    @commands.command(aliases=["costumes", "cos", "skin", "skins"]) # costumes command
    async def costume(self, ctx, *, hero: str = None):
        if hero is None:
            embed = self.defaul_embed.info_embed('Costumes')
            await ctx.reply(embed=embed)
        else:
            chc = await self.check_class(ctx, hero, self.get_costumes)
            if chc is False:
                re, data, boss = self.find(hero)
                await self.get_costumes(re, data, ctx)

    @commands.command(aliases=["bosses", "gr", "gc", "wb", "trial", "shakmeh"]) # boss command
    async def boss(self, ctx):
        embed = self.defaul_embed.info_embed('Bosses')
        await ctx.reply(embed=embed)

    async def check_class(self, ctx, input_: str, func, num: int = None): # check provided hero's class
        async def do(class_, emoji):
            clr = self.get_color(class_.lower())
            des = ''
            if func == self.get_perks:
                embed, des_ = self.get_class_perk(class_, clr)
                des = des_+'\n'
            list_ = []
            with open('./data/emojis.json') as e:
                emojis = json.load(e)
            for obj in os.listdir('./data/kr/table-data/heroes'):
                with open(f'./data/kr/table-data/heroes/{obj}') as f:
                    re = json.load(f)
                if re['infos']['class'] == class_:
                    emj = emojis['heroes'][obj[:-5]]
                    list_.append(emj)
                    des += f"{emj} "
            embed = discord.Embed(title=f'{emoji} {class_} Heroes',
                                description=des,
                                colour=clr)
            msg = await ctx.reply(embed=embed)
            for emoji_ in list_:
                await msg.add_reaction(emoji_)

            def check(reaction, user):
                if msg.channel.type == discord.ChannelType.private:
                    return reaction.emoji in list_
                return user == ctx.author and str(reaction.emoji) in list_
            try:
                reaction, user = await self.client.wait_for(
                    "reaction_add", timeout=30.0, check=check
                    )
                for emoji_ in list_:
                    if str(reaction.emoji) in emoji_:
                        re, data, boss = self.find(emoji_)
                        await self.clear_reactions(msg)
                        if func == self.get_costumes:
                            await msg.delete()
                            await func(re, data, ctx)
                        elif func == self.get_uts:
                            if num is None:
                                await msg.delete()
                                await func(re, data, ctx=ctx)
                            else:
                                embed = await self.get_uts(re, data, num)
                                await msg.edit(embed=embed)
                        elif func == self.get_perks:
                            await msg.delete()
                            await func(re, data, ctx)
                        else:
                            if boss is not None:
                                embed = func(re, data, boss)
                            else:
                                embed = func(re, data)
                            await msg.edit(embed=embed)
            except asyncio.TimeoutError:
                await self.clear_reactions(msg)
                await msg.edit(content="Timeout! Please try again.")

        if input_.lower().startswith('archer'):
            await do('Archer', '<:archer:753231911639449602>')
        elif input_.lower().startswith('assassin'):
            await do('Assassin', '<:assassin:753231911845101608>')
        elif input_.lower().startswith('knight'):
            await do('Knight', '<:knight:753231911861878864>')
        elif input_.lower().startswith('mechanic'):
            await do('Mechanic', '<:mechanic:753231911882719313>')
        elif input_.lower().startswith('priest'):
            await do('Priest', '<:priest:753231911857422417>')
        elif input_.lower().startswith('warrior'):
            await do('Warrior', '<:warrior:753231911991640074>')
        elif input_.lower().startswith('wizard'):
            await do('Wizard', '<:wizard:753231911857553490>')

        else:
            return False

    def find(self, input_:str): # find hero or boss in data
        objs = []
        aliases = {}
        paths = ['./data/kr/table-data/heroes', './data/kr/table-data/bosses']
        for path in paths:
            for obj in os.listdir(path):
                objs.append(str(obj[:-5]))
                with open(f'{path}/{obj}') as f:
                    re_ = json.load(f)
                    if re_['aliases'] is not None:
                        for aliases_ in re_['aliases']:
                            objs.append(aliases_)
                            aliases[aliases_] = obj[:-5]
        re = process.extractOne(input_, objs)
        re_ = re[0]
        boss = None
        try:
            with open(f'./data/kr/table-data/heroes/{re[0]}.json') as f:
                data = json.load(f)
        except FileNotFoundError:
            try:
                with open(f'./data/kr/table-data/heroes/{aliases[re[0]]}.json') as f:
                    data = json.load(f)
                    re_ = aliases[re[0]]
            except:
                try:
                    with open(f'./data/kr/table-data/bosses/{re[0]}.json') as f:
                        data = json.load(f)
                        boss = True
                except:
                    with open(f'./data/kr/table-data/bosses/{aliases[re[0]]}.json') as f:
                        data = json.load(f)
                        re_ = aliases[re[0]]
                        boss = True
        except:
            pass
        return re_, data, boss

    def get_color(self, cls): #  get class's color
        if cls == 'wizard':
            clr = discord.Colour.from_rgb(123, 0, 0)
        elif cls == 'warrior':
            clr = discord.Colour.from_rgb(123, 60, 0)
        elif cls == 'knight':
            clr = discord.Colour.from_rgb(26, 63, 112)
        elif cls == 'assassin':
            clr = discord.Colour.from_rgb(118, 0, 102)
        elif cls == 'archer':
            clr = discord.Colour.from_rgb(51, 116, 0)
        elif cls == 'mechanic':
            clr = discord.Colour.from_rgb(0, 20, 122)
        elif cls == 'priest':
            clr = discord.Colour.from_rgb(0, 101, 115)

        elif cls == 'tyrfas':
            clr = discord.Colour.from_rgb(105, 145, 170)
        elif cls == 'lakreil':
            clr = discord.Colour.from_rgb(199, 170, 126)
        elif cls == 'velkazar':
            clr = discord.Colour.from_rgb(194, 70, 70)
            
        elif cls == 'xakios':
            clr = discord.Colour.from_rgb(71, 181, 83)
        elif cls == 'nordik':
            clr = discord.Colour.from_rgb(27, 24, 92)
        elif cls == 'nubis':
            clr = discord.Colour.from_rgb(180, 122, 71)
        elif cls == 'gushak':
            clr = discord.Colour.from_rgb(157, 65, 54)
        elif cls == 'maviel':
            clr = discord.Colour.from_rgb(60, 4, 9)
        elif cls == 'manticore':
            clr = discord.Colour.from_rgb(139, 71, 13)

        elif cls == 'mountain fortress':
            clr = discord.Colour.from_rgb(182, 150, 113)
        elif cls == 'protianus' or cls == 'event protianus':
            clr = discord.Colour.from_rgb(69, 103, 179)
        elif cls == 'xanadus':
            clr = discord.Colour.from_rgb(75, 36, 100)

        elif cls == 'imet':
            clr = discord.Colour.from_rgb(250, 66, 44)
        elif cls == 'musama':
            clr = discord.Colour.from_rgb(185, 60, 150)
        elif cls == 'sekmaha':
            clr = discord.Colour.from_rgb(5, 164, 251)

        elif cls == 'devourer shakmeh':
            clr = discord.Colour.from_rgb(0, 0, 0)
        elif cls == 'otherworldly shakmeh':
            clr = discord.Colour.from_rgb(26, 53, 215)

        elif cls == 'galgoria' or cls == 'siegfried' or cls == 'ascalon':
            clr = discord.Colour.from_rgb(200,181,164)

        elif cls == 'tersio' or cls == 'apocalypsion':
            clr = discord.Colour.from_rgb(80,72,109)

        else:
            clr = config.embed_color
        return clr

    def get_infos(self, obj, data, boss=None): # get infos
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

    def get_skills(self, obj, data, boss=None): # get skills
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

    def get_books(self, obj, data): # get books
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

    async def get_perks(self, obj, data, ctx): # get perks
        clr = self.get_color(data['infos']['class'].lower())
        des = ''
        des = '**T3 Perks**\n'
        for skill in data['perks']['t3']:
            des+='**Skill '+skill+'**\n'
            for perk in data['perks']['t3'][skill]:
                des+='['+perk.upper()+'] '+data['perks']['t3'][skill][perk]['effect']+'\n'
        des+='\n**T5 Perks**\n'
        for perk in data['perks']['t5']:
            des+='['+perk.upper()+'] '+data['perks']['t5'][perk]['effect']+'\n'
        embed = discord.Embed(
            title=obj + ' Perks',
            description=des,
            colour=clr,
        )
        embed.set_footer(text="React to the below emoji to show Class's Perks.")
        msg = await ctx.reply(embed=embed)
        with open('./data/emojis.json') as f:
            p_emoji = json.load(f)['alphabets']['P']
        await msg.add_reaction(p_emoji)
        def check(reaction, user):
            if msg.channel.type == discord.ChannelType.private:
                return reaction.emoji in p_emoji
            return user == ctx.author and reaction.emoji in p_emoji
        try:
            reaction, user = await self.client.wait_for("reaction_add", timeout=30.0, check=check)
            if str(reaction.emoji) in p_emoji:
                embed, des = self.get_class_perk(data['infos']['class'], clr)
                await msg.edit(embed=embed)
                await self.clear_reactions(msg)
        except asyncio.TimeoutError:
            embed.set_footer()
            await msg.edit(embed=embed)
            await self.clear_reactions(msg)

    def get_class_perk(self, cls, clr): # get class's perk
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

    def get_uw(self, obj, data): #  get uw
        clr = self.get_color(data['infos']['class'].lower())
        des = ''
        des = data['uw']['name']+'\n\n'+data['uw']['description']+'\n\n'
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

    def get_sw(self, obj, data): # get sw
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

    def get_sa_vs(self, obj, data, cate): # get splashart and visual splashart
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
    
    async def get_costumes(self, obj, data, ctx): # get costumes
        clr = self.get_color(data['infos']['class'].lower())
        des = ''
        rep = "\U0001F501"
        numbers = []
        with open('./data/emojis.json', 'r') as f:
            emj = json.load(f)
        for number in emj['numbers']:
            numbers.append(emj['numbers'][number])
        for alphabet in emj['alphabets']:
            numbers.append(emj['alphabets'][alphabet])
        msg_ = ''
        ls = []
        num = 0
        for costumes_ in os.listdir(data['costumes']):
            ls.append(costumes_)
        for cos_ in sorted(ls):
            msg_+=numbers[num]+'. '
            if '%' in cos_:
                cos_ = cos_.replace('%', '?')
            msg_+=cos_[:-4]+'\n'
            num+=1

        embed = discord.Embed(title=f'{obj} Costumes', 
                                description=msg_,
                                colour=clr)
        msg = await ctx.reply(embed=embed)
        range_ = len(ls)
        for i in range(range_):
            await msg.add_reaction(numbers[i])

        def check(reaction, user):
            if msg.channel.type == discord.ChannelType.private:
                return reaction.emoji in numbers
            return user == ctx.author and reaction.emoji in numbers
        def check_(reaction, user):
            if msg.channel.type == discord.ChannelType.private:
                return reaction.emoji in rep
            return user == ctx.author and reaction.emoji in rep
        def get(num):
            for item in msg.embeds[0].description.split("\n"):
                if num in item:
                    re = item.strip()
                    return re
        def embed_(cos):
            nmd = research.search(f"(.*?) ", cos).group(1)
            cos = cos.replace(nmd+' ', '')
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
            embed.set_footer(text="Hit the below emoji in 10 sec if the image is not loaded properly.")
            return embed, file, cos

        try:
            reaction, user = await self.client.wait_for("reaction_add", timeout=30.0, check=check)
            for number in numbers:
                if str(reaction.emoji) in number:
                    re = get(number)
                    break
            embed, file, cos = embed_(re)
            _embed_ = await self.embed_file(self.client, embed, file)
            async def exrep(msg, embed, pms:bool):
                try:
                    reaction_, user_ = await self.client.wait_for("reaction_add", timeout=10.0, check=check_)
                    if str(reaction_.emoji) in rep:
                        file = discord.File(data['costumes']+f'/{cos}.png')
                        await ctx.reply(f"**{msg.embeds[0].title}**", file=file)
                        await msg.delete()
                except asyncio.TimeoutError:
                    embed.set_footer()
                    if pms is True:
                        await msg.edit(content=None, embed=embed)
                    else:
                        await ctx.send(embed=embed)
                        await msg.delete()
                    await self.clear_reactions(msg)
            try:
                await msg.clear_reactions()
                await msg.edit(content=None, embed=_embed_)
                await msg.add_reaction(rep)
                await exrep(msg, _embed_, True)
            except:
                await msg.delete()
                rep_msg = await ctx.send(embed=_embed_)
                await rep_msg.add_reaction(rep)
                await exrep(rep_msg, _embed_, False)
        except asyncio.TimeoutError:
            await msg.edit(content="Timeout! Please try again.")
            await self.clear_reactions(msg)

    async def get_uts(self, obj, data, num:int=None, ctx=None): # get uts
        clr = self.get_color(data['infos']['class'].lower())
        des = ''
        des = ''
        if num is None:
            for ut in data['uts']:
                des+='**UT'+ut+' (Skill '+ut+')**: '+data['uts'][ut]['name']+'\n'+data['uts'][ut]['description']+'\n\n'
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
            msg = await ctx.reply(embed=embed)

            one = "\u0031\u20e3"
            two = "\u0032\u20e3"
            three = "\u0033\u20e3"
            four = "\u0034\u20e3"
            nums = [one, two, three, four]
            for num in nums:
                await msg.add_reaction(num)
            
            def check(reaction, user):
                if msg.channel.type == discord.ChannelType.private:
                    return reaction.emoji in nums
                return user == ctx.author and reaction.emoji in nums
            try:
                reaction, user = await self.client.wait_for("reaction_add", timeout=30.0, check=check)
                actions = [(obj, data, 1), (obj, data, 2), (obj, data, 3), (obj, data, 4)]
                count = 0
                for num in nums:
                    act = actions[count]
                    if str(reaction.emoji) in num:
                        embed, file = await self.get_uts(act[0], act[1], act[2])
                        _embed_ = await self.embed_file(self.client, embed, file)
                        try:
                            await self.clear_reactions(msg)
                            await msg.edit(embed=_embed_)
                        except:
                            await msg.delete()
                            await ctx.send(embed=_embed_)
                        break
                    else:
                        count += 1
            except asyncio.TimeoutError:
                await self.clear_reactions(msg)
        else:
            des = '**UT'+str(num)+' (Skill '+str(num)+')**: '+data['uts'][str(num)]['name']+'\n'+data['uts'][str(num)]['description']+'\n\n'
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

    async def clear_reactions(self, msg):
        try:
            await msg.clear_reactions()
        except:
            pass

class TM_Gear(commands.Cog):
    def __init__(self, client):
        self.client = client

    @commands.command(aliases=['tm', 'technomagic', 'tmgear', 'technomagicgear', 'technomagic_gear']) # technomagic gear command
    async def tm_gear(self, ctx, type:str=None, class_:str=None):
        if type is None and class_ is None:
            embed = discord.Embed(title="Technomagic Gear Command",
                                colour=config.embed_color,
                                description="Syntax:\n`tm <boss/gear> <hero_class/leave_blank>`\nShows 4 pieces of Technomagic Gear effect.")
            await ctx.reply(embed=embed)
        else:
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
            await ctx.reply(embed=embed)

def setup(client):
    client.add_cog(Heroes(client))
    client.add_cog(TM_Gear(client))
