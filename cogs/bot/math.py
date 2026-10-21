# Source code from https://github.com/duckness/NotCleo

import asyncio
import logging
import math

import discord
from beautifultable import BeautifulTable, enums
from discord import app_commands
from discord.ext import commands
from py_expression_eval import Parser

import settings

from ..utils import info_embed
from ..utils.expression import evaluate, parse_expression
from ..utils.game_data import GameData, selected_data, stamp, version_autocomplete


class Math(commands.Cog):
    def __init__(self, client):
        self.client = client
        self.parser = Parser()
        self.info_embed_ = info_embed.Info_Embed()

    async def a_parse(self, expression):
        return await evaluate(expression)

    def parse(self, expression):
        return parse_expression(expression)

    def actualStat(self, statType, istat):
        actual = 0
        if istat == 0:
            actual = 0
        elif istat > statType["X1"]:
            actual = self.attenuateInv(
                istat, statType["MaxK"], statType["A1"], statType["B1"]
            )
        elif istat > statType["X2"]:
            actual = math.floor((istat * statType["A2"]) / 1000) + statType["B2"]
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

    def sc_table(self, val, softcaps=None):
        softcaps = softcaps if softcaps is not None else GameData().softcaps()
        table = BeautifulTable()
        table.columns.header = ["Stat", "Softcap", "Value"]
        table.columns.alignment["Stat"] = enums.Alignment.ALIGN_LEFT
        table.columns.alignment["Softcap"] = enums.Alignment.ALIGN_RIGHT
        table.columns.alignment["Value"] = enums.Alignment.ALIGN_RIGHT
        table.set_style(enums.Style.STYLE_BOX)

        table.rows.append(
            [
                "ACC",
                str(softcaps["acc"]["X2"]),
                self.actualStat(softcaps["acc"], val),
            ]
        )
        table.rows.append(
            [
                "Crit",
                str(softcaps["crit"]["X2"]),
                self.actualStat(softcaps["crit"], val),
            ]
        )
        table.rows.append(
            [
                "Attack Spd",
                str(softcaps["aspd"]["X2"]),
                self.actualStat(softcaps["aspd"], val),
            ]
        )
        table.rows.append(
            [
                "Lifesteal",
                str(softcaps["dodge"]["X2"]),
                self.actualStat(softcaps["dodge"], val),
            ]
        )
        table.rows.append(
            [
                "Penetration",
                str(softcaps["pen"]["X2"]),
                self.actualStat(softcaps["pen"], val),
            ]
        )
        table.rows.append(
            [
                "Block DEF",
                str(softcaps["blockdef"]["X2"]),
                self.actualStat(softcaps["blockdef"], val),
            ]
        )
        table.rows.append(
            [
                "CC Resist",
                str(softcaps["ccresist"]["X2"]),
                self.actualStat(softcaps["ccresist"], val),
            ]
        )
        table.rows.append(
            [
                "Dodge",
                str(softcaps["dodge"]["X2"]),
                self.actualStat(softcaps["dodge"], val),
            ]
        )
        table.rows.append(
            [
                "Block",
                str(softcaps["dodge"]["X2"]),
                self.actualStat(softcaps["dodge"], val),
            ]
        )
        table.rows.append(
            [
                "Tough",
                str(softcaps["pen"]["X2"]),
                self.actualStat(softcaps["pen"], val),
            ]
        )
        table.rows.append(
            [
                "Crit Resist",
                str(softcaps["critresist"]["X2"]),
                self.actualStat(softcaps["critresist"], val),
            ]
        )
        table.rows.append(
            [
                "CC ACC",
                str(softcaps["ccacc"]["X2"]),
                self.actualStat(softcaps["ccacc"], val),
            ]
        )
        table.rows.append(
            [
                "Mp/Atk",
                str(softcaps["mpatk"]["X2"]),
                self.actualStat(softcaps["mpatk"], val),
            ]
        )

        return "```\n" + str(table) + "\n```"

    @commands.hybrid_command(  # calculate command
        name="calc",
        aliases=["calculate", "math", "calculation", "calculations"],
        description="Calculate an expression",
    )
    async def calculate(self, ctx, *, operation: str | None = None):
        expression = operation
        if expression is None:
            embed = self.info_embed_.info_embed("Math")
            await ctx.reply(embed=embed)

        else:
            try:
                exp = expression.replace("`", "")
                if "x" in exp:
                    exp = exp.replace("x", "*")
                if ":" in exp:
                    exp = exp.replace(":", "/")
                result = await asyncio.wait_for(self.a_parse(exp), timeout=1)
                embed = discord.Embed(
                    title=f"Result: **{result}**", colour=settings.EMBED_COLOR
                )
                if len(str(round(result))) > 3:
                    embed.set_footer(text=f"Better form: {result:,}")
                await ctx.reply(embed=embed)
            except Exception:
                logging.getLogger(__name__).debug(
                    "Expression could not be evaluated", exc_info=True
                )
                await ctx.reply(
                    "I can't calculate that... <:broken:652813264778166278>"
                )

    @commands.hybrid_command(  # softcap command
        aliases=["soft", "softs", "cap", "caps", "softcaps", "stat", "stats"],
        description="Show a softcap table",
    )
    @app_commands.autocomplete(version=version_autocomplete)
    async def softcap(
        self, ctx, value: int | None = None, *, version: str | None = None
    ):
        dataset = selected_data(ctx, version)
        val = value
        if val is None:
            embed = self.info_embed_.info_embed("Softcap")

            await ctx.reply(embed=stamp(embed, dataset))

        else:
            embed = discord.Embed(
                title=f"Stat value: {val}",
                description=self.sc_table(int(val), dataset.softcaps()),
                colour=settings.EMBED_COLOR,
            )
            await ctx.reply(embed=stamp(embed, dataset))

    @softcap.error
    async def softcap_error(self, ctx, error):
        if isinstance(error, commands.errors.BadArgument):
            await ctx.reply(
                "Error, value must be an interger. <:broken:652813264778166278>"
            )


async def setup(client):
    await client.add_cog(Math(client))
