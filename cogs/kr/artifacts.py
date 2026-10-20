import discord
import json
from fuzzywuzzy import process
from discord.ext import commands

from config import config
from ..utils.menus import ChoiceView, asset, send_result
from ..utils.paginator import Paginator
from ..utils.routes import RouteCog, add_routes


class Artifact(RouteCog):
    def __init__(self, client):
        self.client = client

    @commands.hybrid_command(name="atf", aliases=["artifact", "artifacts", "arti", "art"], description="Look up an artifact")
    async def artifact(self, ctx, *, name: str = None):
        if name is None:
            await ctx.send("Use `artifact <name>`, `artifact search <name>`, or `artifact all`.")
        elif name.lower() in ("all", "list"):
            await self.show_all(ctx)
        elif name.lower().startswith("search "):
            await self.search(ctx, name[7:])
        else:
            result = self.get_artifact(name)
            if isinstance(result[1], list):
                await self.show_choices(ctx, result[1], result[0])
            else:
                await send_result(ctx, result)

    async def show_choices(self, ctx, names, embed):
        view = ChoiceView(ctx.author.id, [(name, name) for name in dict.fromkeys(names)], self.get_artifact, placeholder="Choose an artifact")
        await send_result(ctx, embed, view=view)

    async def search(self, ctx, name):
        data, names, all_names, aliases = self.get_all_artifacts()
        matches = process.extract(name, names, limit=25)
        await self.show_choices(ctx, [match[0] for match in matches], discord.Embed(title=f"Results for {name}", colour=config.embed_color))

    @commands.hybrid_command(description="Search artifacts")
    async def artifact_search(self, ctx, *, name: str):
        await self.search(ctx, name)

    async def show_all(self, ctx):
        data, names, all_names, aliases = self.get_all_artifacts()
        pages = [discord.Embed(title="Artifacts", description="\n".join(names[i:i+30]), colour=config.embed_color) for i in range(0, len(names), 30)]
        await Paginator(self.client).pag(ctx, pages)

    @commands.hybrid_command(description="List all artifacts")
    async def artifact_all(self, ctx):
        await self.show_all(ctx)

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
            file = asset(atf[atf_name]["thumbnail"], filename=name)
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

async def setup(bot):
    cog = Artifact(bot)
    await bot.add_cog(cog)
    add_routes(bot, cog, {"artifact name": "atf", "artifact search": "artifact_search", "artifact all": "artifact_all"})
