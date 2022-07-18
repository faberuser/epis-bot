import discord, json, re, asyncio
from fuzzywuzzy import process
from discord.ext import commands

from discord_slash import cog_ext, SlashContext
from discord_slash.utils.manage_commands import create_option
from discord_slash.utils.manage_components import create_select_option, create_select, create_actionrow, wait_for_component

from ..utils import paginator, check_permisison, embed_file
from config import config

client = discord.Client()


class Artifact(commands.Cog):

    def __init__(self, client):
        self.client = client
        self.paginator = paginator.Paginator(self.client).paginator
        self.check = check_permisison.view_channels
        self.embed_file = embed_file.embed_file


    @cog_ext.cog_subcommand(
                    base="artifact",
                    name="name",
                    description="Give Artifact's Infomations",
                    guild_ids=config.guild_ids,
                    options=[
                        create_option(
                            name="name",
                            description="Input a name of artifact",
                            option_type=3,
                            required=True
                        )
                    ]) # slash artifact command
    async def artifact_(self, ctx: SlashContext, *, name:str = None):
        await self.artifact_s(ctx, name)

    @cog_ext.cog_slash(
                    name="atf",
                    description="An aliase of artifact name",
                    guild_ids=config.guild_ids,
                    options=[
                        create_option(
                            name="name",
                            description="Input a name of artifact",
                            option_type=3,
                            required=True
                        )
                    ]) # slash artifact command
    async def artifact_(self, ctx: SlashContext, *, name:str = None):
        await self.artifact_s(ctx, name)

    async def artifact_s(self, ctx, name):
        artifact = name
        name = None
        if self.check(ctx.guild, ctx.channel) == True:
            await ctx.send(content="This command can't be used here...", hidden=True)
            return
        try:
            embed, file = self.get_artifact(artifact)
            if self.check(ctx.guild, ctx.channel) == True:
                await ctx.send(embed=embed, file=file, hidden=True)
            else:
                await ctx.send(embed=embed, file=file)
        except:
            try:
                embed, lst = self.get_artifact(artifact)
                with open('./data/emojis.json') as f:
                    re_ = json.load(f)['artifacts']
                menus = []
                for atf_ in lst:
                    splited = re.split('(\d+)', re_[atf_])
                    emoji_ = self.client.get_emoji(int(splited[1]))
                    menus.append(create_select_option(emoji=emoji_, label=atf_, value=atf_))
                option_menus = create_select(options=menus, placeholder='Choose your artifact', max_values=1)
                action_row = create_actionrow(option_menus)
                if self.check(ctx.guild, ctx.channel) == True:
                    msg = await ctx.send(embed=embed, components=[action_row], hidden=True)
                else:
                    msg = await ctx.send(embed=embed, components=[action_row])
                while True:
                    try:
                        menus: ComponentContext = await wait_for_component(self.client, components=action_row, timeout=120.0, check=lambda x: x.author_id == ctx.author.id)
                        embed_, file = self.get_artifact(menus.selected_options[0])
                        embed = await self.embed_file(self.client, embed_, file)
                        await menus.edit_origin(embed=embed)
                    except asyncio.TimeoutError:
                        await msg.edit(components=None)
                        break
            except:
                content = self.get_artifact(artifact)
                await ctx.send(content=content, hidden=True)


    @cog_ext.cog_subcommand(
                    base="artifact",
                    name="search",
                    description="Search for Artifacts",
                    guild_ids=config.guild_ids,
                    options=[
                        create_option(
                            name="name",
                            description="Input a name for searching",
                            option_type=3,
                            required=True
                        )
                    ])
    async def artifact_search(self, ctx: SlashContext, *, name:str):
        artifact = name
        name = None
        atf, ls_base, ls, aliases = self.get_all_artifacts()
        input_ = artifact
        arti = input_.lower()        
        exts = process.extract(arti, ls_base, limit=25)
        lst = []
        for item in exts:
            lst.append(item[0])
        with open('./data/emojis.json') as f:
            re_ = json.load(f)['artifacts']
        menus = []
        for atf_ in lst:
            splited = re.split('(\d+)', re_[atf_])
            emoji_ = self.client.get_emoji(int(splited[1]))
            af = atf_
            if len(atf_) >= 25:
                atf_ = atf_[:25]
            menus.append(create_select_option(emoji=emoji_, label=atf_, value=af, description=af))
        option_menus = create_select(options=menus, placeholder='Choose your artifact', max_values=1)
        action_row = create_actionrow(option_menus)

        embed = discord.Embed(
            title=f"Showing results for `{input_}`:",
            colour=config.embed_color,
        )
        if self.check(ctx.guild, ctx.channel) == True:
            msg = await ctx.send(embed=embed, components=[action_row], hidden=True)
        else:
            msg = await ctx.send(embed=embed, components=[action_row])
        while True:
            try:
                menus: ComponentContext = await wait_for_component(self.client, components=action_row, timeout=120.0, check=lambda x: x.author_id == ctx.author.id)
                embed_, file = self.get_artifact(menus.selected_options[0])
                embed = await self.embed_file(self.client, embed_, file)
                await menus.edit_origin(embed=embed)
            except asyncio.TimeoutError:
                await msg.edit(components=None)
                break


    @cog_ext.cog_subcommand(
                    base="artifact",
                    name="all",
                    description="Give all Artifacts",
                    guild_ids=config.guild_ids)
    async def artifact_all(self, ctx: SlashContext):
        if self.check(ctx.guild, ctx.channel) == True:
            await ctx.send(content="This command can't be used here...", hidden=True)
            return
        atf, ls_base, ls, aliases = self.get_all_artifacts()
        des = ''
        with open('./data/emojis.json') as f:
            re = json.load(f)
        for emojis in re['artifacts']:
            des+=re['artifacts'][emojis]+' '
        if len(des) > 2048:
            num = 2048
            for i in range(100):
                des1 = des[:num]
                if des1[-1] != '<':
                    num-=1
                else:
                    des1 = des1[:-1]
                    break
            
            num2 = len(des) - len(des1)
            for i in range(100):
                des2 = des[num2:]
                if des2[1] != '<':
                    num2-=1
                else:
                    break

            embed1 = discord.Embed(
                title='Artifacts (Page 1)',
                description=des1,
                colour=config.embed_color,
            )
            embed1.set_footer(text='Page 1/2')

            embed2 = discord.Embed(
                title='Artifacts (Page 2)',
                description=des2,
                colour=config.embed_color,
            )
            embed2.set_footer(text='Page 2/2')

        await self.paginator(ctx, [embed1, embed2])


    def get_all_artifacts(self):
        with open("./data/kr/table-data/artifacts.json") as f:
            atf = json.load(f)
        ls_base = []
        ls = []
        aliases = {}
        for name in atf:
            ls.append(name)
            ls_base.append(name)
            if atf[name]['aliases'] is not None:
                for aliases_ in atf[name]['aliases']:
                    ls.append(aliases_)
                    aliases[aliases_] = name
        return atf, ls_base, ls, aliases


    def get_artifact(self, artifact:str):
        atf, ls_base, ls, aliases = self.get_all_artifacts()
        arti = artifact.lower()
        ext = process.extractOne(arti, ls)
        if ext[-1] >= 60:
            atf_name = ext[0]
            try:
                atf[atf_name]['description']
            except:
                atf_name = aliases[atf_name]
            des = atf[atf_name]['description']+'\n\n'
            for value in atf[atf_name]['value']:
                des+='('+value+'): '+atf[atf_name]['value'][value]+'\n'
            embed = discord.Embed(
                title=atf_name,
                colour=config.embed_color,
                description=des,
            )
            name = atf_name+'.png'
            if ' ' in name:
                name = name.replace(' ', '_')
            if "'" in name:
                name = name.replace("'", '')
            file = discord.File(atf[atf_name]["thumbnail"], filename=name)
            embed.set_thumbnail(url=f'attachment://{name}')
            return embed, file

        else:
            lt = []
            dymn = process.extract(arti, ls_base, limit=5)
            for dym in dymn:
                lt.append(dym)
            embed = discord.Embed(
                title="Did you mean",
                colour=config.embed_color)
            lst = [lt[0][0], lt[1][0], lt[2][0], lt[3][0], lt[4][0]]
            return embed, lst


def setup(client):
    client.add_cog(Artifact(client))
