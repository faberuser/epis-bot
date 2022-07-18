# Source code from https://github.com/duckness/NotCleo

import discord, asyncio, time, math, json, concurrent.futures
from discord.ext import commands
from typing import Any
from py_expression_eval import Parser
from beautifultable import BeautifulTable

from ..utils import info_embed
from config import config

client = discord.Client()


class Math(commands.Cog):
    def __init__(self, client):
        self.client = client
        self.parser = Parser()
        self.info_embed_ = info_embed.Info_Embed()
        with open('./data/kr/softcap.json') as f:
            sc = json.load(f)
        self.softcaps = sc

    async def a_parse(self, expression):
        loop = asyncio.get_running_loop()
        with concurrent.futures.ThreadPoolExecutor() as pool:
            result = await loop.run_in_executor(pool, self.parse, expression)
        return result

    def parse(self, expression):
        return self.parser.parse(expression).evaluate({})

    def actualStat(self, statType, istat):
        actual = 0
        if istat == 0:
            actual = 0
        elif istat > statType["X1"]:
            actual = self.attenuateInv(
                istat, statType["MaxK"], statType["A1"], statType["B1"]
            )
        elif istat > statType["X2"]:
            actual = math.floor(
                (istat * statType["A2"]) / 1000) + statType["B2"]
        elif istat < statType["X3"]:
            actual = self.attenuateInv(
                istat, statType["MinK"], statType["A3"], statType["B3"]
            )
        elif istat < statType["X4"]:
            actual = self.attenuate(
                istat, statType["MinK"], statType["A4"], statType["B4"]
            )
        else:
            actual = istat
        actual = round(actual) / 10
        return str(round(actual)) + "%"

    def attenuate(self, x, k, a, b):
        return math.floor((k * 1000000) / (a * x * x + b * x + 1000000))

    def attenuateInv(self, x, k, a, b):
        return k - math.floor((k * 1000000) / (a * x * x + b * x + 1000000))

    def sc_table(self, val):
        table = BeautifulTable()
        table.column_headers = ["Stat", "Softcap", "Value"]
        table.column_alignments["Stat"] = BeautifulTable.ALIGN_LEFT
        table.column_alignments["Softcap"] = BeautifulTable.ALIGN_RIGHT
        table.column_alignments["Value"] = BeautifulTable.ALIGN_RIGHT
        table.set_style(BeautifulTable.STYLE_BOX)

        table.append_row(
            [
                "ACC",
                str(self.softcaps["acc"]["X2"]),
                self.actualStat(self.softcaps["acc"], val),
            ]
        )
        table.append_row(
            [
                "Crit",
                str(self.softcaps["crit"]["X2"]),
                self.actualStat(self.softcaps["crit"], val),
            ]
        )
        table.append_row(
            [
                "Attack Spd",
                str(self.softcaps["aspd"]["X2"]),
                self.actualStat(self.softcaps["aspd"], val),
            ]
        )
        table.append_row(
            [
                "Lifesteal",
                str(self.softcaps["dodge"]["X2"]),
                self.actualStat(self.softcaps["dodge"], val),
            ]
        )
        table.append_row(
            [
                "Penetration",
                str(self.softcaps["pen"]["X2"]),
                self.actualStat(self.softcaps["pen"], val),
            ]
        )
        table.append_row(
            [
                "Block DEF",
                str(self.softcaps["blockdef"]["X2"]),
                self.actualStat(self.softcaps["blockdef"], val),
            ]
        )
        table.append_row(
            [
                "CC Resist",
                str(self.softcaps["ccresist"]["X2"]),
                self.actualStat(self.softcaps["ccresist"], val),
            ]
        )
        table.append_row(
            [
                "Dodge",
                str(self.softcaps["dodge"]["X2"]),
                self.actualStat(self.softcaps["dodge"], val),
            ]
        )
        table.append_row(
            [
                "Block",
                str(self.softcaps["dodge"]["X2"]),
                self.actualStat(self.softcaps["dodge"], val),
            ]
        )
        table.append_row(
            [
                "Tough",
                str(self.softcaps["pen"]["X2"]),
                self.actualStat(self.softcaps["pen"], val),
            ]
        )
        table.append_row(
            [
                "Crit Resist",
                str(self.softcaps["critresist"]["X2"]),
                self.actualStat(self.softcaps["critresist"], val),
            ]
        )
        table.append_row(
            [
                "CC ACC",
                str(self.softcaps["ccacc"]["X2"]),
                self.actualStat(self.softcaps["ccacc"], val),
            ]
        )
        table.append_row(
            [
                "Mp/Atk",
                str(self.softcaps["mpatk"]["X2"]),
                self.actualStat(self.softcaps["mpatk"], val),
            ]
        )

        return "```\n" + str(table) + "\n```"

    @commands.command( # calculate command
        aliases=["calc", "math", "calculator", "calculation", "calculations"]
    )
    async def calculate(self, ctx, *, expression=None):
        if expression is None:
            embed = self.info_embed_.info_embed('Math')
            await ctx.reply(embed=embed)

        else:
            try:
                exp = expression.replace("`", "")
                if 'x' in exp:
                    exp = exp.replace('x', '*')
                if ':' in exp:
                    exp = exp.replace(':', '/')
                result = await asyncio.wait_for(
                    self.a_parse(exp), timeout=1
                )
                embed = discord.Embed(
                    title=f"Result: **{result}**", colour=config.embed_color
                )
                if len(str(round(result))) > 3:
                    embed.set_footer(text=f'Better form: {result:,}')
                await ctx.reply(embed=embed)
            except:
                await ctx.reply("I can't calculate that... <:broken:652813264778166278>")

    @commands.command( # softcap command
        aliases=["soft", "softs", "cap", "caps", "softcaps", "stat", "stats"]
    )
    async def softcap(self, ctx, val: int = None):
        if val is None:
            embed = self.info_embed_.info_embed('Softcap')

            await ctx.reply(embed=embed)

        else:
            embed = discord.Embed(
                title=f"Stat value: {val}",
                description=self.sc_table(int(val)),
                colour=config.embed_color,
            )
            await ctx.reply(embed=embed)

    @softcap.error
    async def softcap_error(self, ctx, error):
        if isinstance(error, commands.errors.BadArgument):
            await ctx.reply(
                "Error, value must be an interger. <:broken:652813264778166278>"
            )


def setup(client):
    client.add_cog(Math(client))
