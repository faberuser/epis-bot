import discord, json
from fuzzywuzzy import process
from discord.ext import commands

from ..utils import info_embed, paginator
from config import config

client = discord.Client()


class Artifact(commands.Cog):

    def __init__(self, client):
        self.client = client
        self.info_embed_ = info_embed.Info_Embed()
        self.menus = paginator.Paginator(self.client)

    @commands.command(aliases=["atf", "artifacts", "arti", "art"]) # artifact command
    async def artifact(self, ctx, *, artifact:str = None):
        if artifact is None:
            embed = self.info_embed_.info_embed('Artifacts')
            await ctx.reply(embed=embed)

        else:
            with open("./data/kr/table-data/artifacts.json") as f:
                atf = json.load(f)
            ls = []
            aliases = {}
            for name in atf:
                ls.append(name)
                if atf[name]['aliases'] is not None:
                    for aliases_ in atf[name]['aliases']:
                        ls.append(aliases_)
                        aliases[aliases_] = name

            if artifact.lower().startswith('search'): # search for artifact in data
                input_ = artifact.replace('search ', '')
                arti = input_.lower()
                limit_ = limit__ = 10
                msgs = arti.split()
                if msgs[0].isnumeric():
                    limit_ = limit__ = int(msgs[0])
                    input_ = input_.replace(msgs[0], '')
                    if input_.startswith(' '):
                        input_ = input_[1:]
                    if limit_ > 50:
                        limit_ = 50
                        limit__ = 'max: 50'
                    elif limit_ < 10:
                        limit_ = 10
                        limit__ = 'min: 10'
                exts = process.extract(arti, ls, limit=limit_)
                embed = discord.Embed(
                    title=f"Showing ({limit__}) results for `{input_}`:",
                    colour=config.embed_color,
                    description='',
                )
                for item in exts:
                    item_ = item[0]
                    try:
                        item_ = aliases[item_]
                    except:
                        pass
                    embed.description += item_+'\n'
                await ctx.reply(embed=embed)

            if artifact.lower().startswith('list') or artifact.lower().startswith('all'): # list all artifacts in data
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

                await self.menus.pag(message=ctx.message, embeds=[embed1, embed2])

            else: # get & send artifact's data
                arti = artifact.lower()
                ext = process.extractOne(arti, ls)
                if ext[-1] >= 50:
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
                    await ctx.reply(embed=embed, file=file)

                elif 40 <= ext[-1] < 50:
                    lt = []
                    dymn = process.extract(arti, ls, limit=5)
                    for dym in dymn:
                        lt.append(dym)
                    embed = discord.Embed(
                        title="Did you mean",
                        colour=config.embed_color,
                        description=f"{lt[0][0]}\n{lt[1][0]}\n{lt[2][0]}\n{lt[3][0]}\n{lt[4][0]}",
                    )
                    await ctx.reply(embed=embed)
                else:
                    await ctx.reply(f"Sorry, I can't find `{artifact}`. <:broken:652813264778166278>")


def setup(client):
    client.add_cog(Artifact(client))
