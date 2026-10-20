import discord, random, re, shlex
from discord.ext import commands

from config import config



class Stuffs(commands.Cog):
    def __init__(self, client):
        self.client = client

    @commands.hybrid_command(description="Get King's Raid emulator LoH macros")
    async def macro(self, ctx: commands.Context):
        embed = discord.Embed(
            title="King's Raid Emulator LoH Macro",
            description=("Nox App Player (04.04.2020)\nhttps://www.reddit.com/r/Kings_Raid/comments/fumrn9/new_loh_macro_for_nox_app_player_04042020/\n\n"+
                        "MEmu App Player (01.04.2020)\nhttps://www.reddit.com/r/Kings_Raid/comments/ft4z91/new_loh_macro_for_memu_play_01042020/\n\n"+
                        "LDPlayer (31.03.2020)\nhttps://www.reddit.com/r/Kings_Raid/comments/fsje29/new_loh_macro_for_ldplayer_31032020/\n\n"+
                        "LDPlayer auto dailies (by me)\nhttps://github.com/faber6/kings-raid-daily"),
            colour=config.embed_color,
        )
        await ctx.send(embed=embed)

    @commands.hybrid_command(description="Show support email addresses")
    async def mail(self, ctx):
        embed = discord.Embed(
            title="Vespa Mail",
            description="EN: cs_en@vespainc.oqupie.com\nJP: cs_jp@vespainc.oqupie.com\nTW: cs_tw@vespainc.oqupie.com\nKR: cs_kr@vespainc.oqupie.com",
            colour=config.embed_color,
        )
        await ctx.reply(embed=embed)

    @commands.hybrid_command(name="choose", aliases=["random", "pick"], description="Choose from words, quoted phrases, or a list separated by pipes")
    async def random(self, ctx, *, choices: str = None):
        if not choices:
            await ctx.send('Usage: `choose apple orange` or `choose first option | second option`.')
            return
        for opening, closing in (("(", ")"), ("[", "]"), ("{", "}")):
            if choices.startswith(opening) and choices.endswith(closing):
                choices = choices[1:-1].replace(closing + " " + opening, " | ")
                break
        separated = re.split(r"\s+[|/&-]\s+|\s+or\s+|[,;]\s*", choices)
        try:
            options = [s.strip() for s in separated if s.strip()] if len(separated) > 1 else shlex.split(choices)
        except ValueError:
            raise commands.BadArgument("Please close quoted choices.")
        if not options:
            raise commands.BadArgument("Provide at least one choice.")
        await ctx.send("I pick `" + random.choice(options).replace("`", "") + "`.")

    @commands.hybrid_command(name="timezone", aliases=["tz", "time_zone"], description="Show game server time zones") # timezone command
    async def tz(self, ctx):
        embed = discord.Embed(title="Servers time zone", colour=config.embed_color,
        description=("Asia - UTC+7 (Asia/Ho_Chi_Minh)\nEurope - UTC+2 (Europe/Bucharest)\nKorea - UTC+9 (Asia/Seoul)\n"+
                    "Ameria - UTC-4 (America/Anguilla)\nJapan - UTC+9 (Asia/Tokyo)\nTaiwan, HongKong, Macao - UTC+8 (Asia/Taipei)"))
        await ctx.reply(embed=embed)

async def setup(client):
    await client.add_cog(Stuffs(client))
