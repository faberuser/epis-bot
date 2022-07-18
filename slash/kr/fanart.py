import discord, random, json, os, asyncio, traceback
from discord.ext import commands
from fuzzywuzzy import process

from discord_slash.utils.manage_components import create_actionrow, create_button, wait_for_component
from discord_slash.utils.manage_commands import create_option, create_choice
from discord_slash.model import ButtonStyle
from discord_slash import cog_ext, SlashContext

from ..utils import dbl, check_permisison
from config import config

from ..bot import sauce

client = discord.Client()

class Fanart(commands.Cog):
    def __init__(self, client):
        self.client = client
        self.vote = dbl.Vote(self.client)
        self.check = check_permisison.view_channels
        self.file_type = ''
        #if config.windows == True:
            #self.file_type = '.txt'
        self.husbando = ['husbando', '_husbando']
        self.waifu = ['waifu', '_waifu']
        for file in os.listdir('./data/kr/table-data/heroes'):
            with open(f'./data/kr/table-data/heroes/{file}') as f:
                re = json.load(f)
            if re['infos']['gender'] == 'Female':
                self.waifu.append(file[:-5].lower().replace(' ', '-'))
            elif re['infos']['gender'] == 'Male':
                self.husbando.append(file[:-5].lower().replace(' ', '-'))
            else:
                if re['gender'] == "Female":
                    self.waifu.append(file[:-5].lower().replace(' ', '-'))
                elif re['gender'] == "Male":
                    self.husbando.append(file[:-5].lower().replace(' ', '-'))


    @cog_ext.cog_subcommand(
                    base='fanart',
                    name='honey',
                    description="Give a King's Raid honey fanart",
                    guild_ids=config.guild_ids,
                    options=[
                        create_option(name='gender', description='Input honey gender', option_type=3, required=True,
                        choices=[
                            create_choice(name='husbando', value='Husbando fanart'),
                            create_choice(name='waifu', value='Waifu fanart')
                        ])
                    ]) # slash fanart command
    async def fanart_honey(self, ctx: SlashContext, *, gender:str=None):
        await self.execute(ctx, gender)


    @cog_ext.cog_subcommand(
                    base='fanart',
                    name='hero',
                    description="Give a King's Raid hero fanart",
                    guild_ids=config.guild_ids,
                    options=[
                        create_option(name='hero', description='Input a hero', option_type=3, required=True)
                    ]) # slash fanart command
    async def fanart_hero(self, ctx: SlashContext, *, hero:str=None):
        await self.execute(ctx, hero)


    async def execute(self, ctx, input_:str):
        if self.check(ctx.guild, ctx.channel) == True:
            await ctx.send(content="This command can't be used here...", hidden=True)
            return
        check = await self.vote.vote(ctx)
        if check is False:
            return
        else:
            pass
        ls = []
        for hero in self.husbando:
            ls.append(hero)
        for hero in self.waifu:
            ls.append(hero)
        re = process.extractOne(input_.lower(), ls)
        if re[1] >= 50:
            embed = self.embed_(ctx, re[0])
            button = [create_button(style=ButtonStyle.blue, label='Random'), create_button(style=ButtonStyle.green, label='Sauce')]
            action_row = create_actionrow(*button)
            try:
                msg = await ctx.send(embed=embed, components=[action_row])
                ssauce, search_embed = False, None
                while True:
                    try:
                        button_ctx: ComponentContext = await wait_for_component(self.client, components=action_row, timeout=10.0, check=lambda x: x.author_id == ctx.author.id)
                        if button_ctx.component['label'] == 'Random':
                            embed = self.embed_(ctx, re[0])
                            await button_ctx.edit_origin(embed=embed)
                        elif button_ctx.component['label'] == 'Sauce':
                            search_embed = sauce.Sauce(self.client).searching_embed(embed)
                            await button_ctx.edit_origin(embed=search_embed)
                            ssauce = True
                            break
                    except asyncio.TimeoutError:
                        buttons = []
                        for row in msg.components:
                            for button in row['components']:
                                button['disabled'] = True
                                buttons.append(button)
                        action_row = create_actionrow(*buttons)
                        await msg.edit(content='Timeout! Please try again.', components=[action_row])
                        break
                if ssauce == True:
                    buttons = []
                    for row in msg.components:
                        for button in row['components']:
                            button['disabled'] = True
                            buttons.append(button)
                    action_row = create_actionrow(*buttons)
                    await msg.edit(components=[action_row])
                    sauce_embed = await sauce.Sauce(self.client).sauce_embed(search_embed)
                    await msg.edit(embed=sauce_embed)
            except:
                await ctx.send(content=embed)
        else:
            await ctx.send(f"Sorry, i can't find `{input_}`. <:broken:652813264778166278>")


    def embed_(self, ctx, input_: str):
        def get_color(cls_):
            if cls_ == 'wizard':
                clr = discord.Colour.from_rgb(123, 0, 0)
            elif cls_ == 'warrior':
                clr = discord.Colour.from_rgb(123, 60, 0)
            elif cls_ == 'knight':
                clr = discord.Colour.from_rgb(26, 63, 112)
            elif cls_ == 'assassin':
                clr = discord.Colour.from_rgb(118, 0, 102)
            elif cls_ == 'archer':
                clr = discord.Colour.from_rgb(51, 116, 0)
            elif cls_ == 'mechanic':
                clr = discord.Colour.from_rgb(0, 20, 122)
            elif cls_ == 'priest':
                clr = discord.Colour.from_rgb(0, 101, 115)
            else:
                clr = discord.Colour.darker_gray()
            return clr
        input__ = input_.replace('-', ' ')
        if input_ == 'waifu' or input_ == 'husbando':
            clr = config.embed_color
        else:
            with open(f'./data/kr/table-data/heroes/{input__.title()}.json') as f:
                re = json.load(f)
            cls_ = re['infos']['class']
            clr = get_color(cls_.lower())
        try:
            with open(f'./data/fanart/lists/{input_}{self.file_type}', 'r', encoding='utf-8') as f:
                re = f.readlines()
                if re == []:
                    return f"Sorry, i can't find any `{input__.title()}`'s fanart in my data. <:broken:652813264778166278>"
                pic = str(random.choice(re))
                embed = discord.Embed(title=f"{input__.title()} Fanart", colour=clr)
                embed.set_image(url=pic)
                embed.set_footer(text=f"Total {input__.title()}'s fanarts data: {len(re)}")
                return embed
        except FileNotFoundError:
            open(f'./data/fanart/lists/{input_}{self.file_type}', 'a').close()
            return f"Sorry, i can't find any `{input__.title()}`'s fanart in my data. <:broken:652813264778166278>"


def setup(client):
    client.add_cog(Fanart(client))
