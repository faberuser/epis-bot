import asyncio

import discord
from discord.ext import commands

from config import config
from ..utils.expression import evaluate
from ..utils.menus import OwnedView, send_result


class CalculatorView(OwnedView):
    def __init__(self, author):
        super().__init__(author.id, timeout=300)
        self.author = author
        self.expression = ""
        self.display = "0"
        self.lock = asyncio.Lock()
        labels = ["Exit", "Clear", "?", ":", "7", "8", "9", "x", "4", "5", "6", "-", "1", "2", "3", "+", "000", "0", ".", "="]
        for index, label in enumerate(labels):
            button = discord.ui.Button(label=label, row=index // 4, style=discord.ButtonStyle.danger if label == "Exit" else discord.ButtonStyle.primary)
            async def callback(interaction, selected=label):
                await self.press(interaction, selected)
            button.callback = callback
            self.add_item(button)

    def embed(self):
        return discord.Embed(title=f"{self.author.display_name}'s Calculator", description=f"```{self.display[:500]}```", colour=getattr(self.author, "colour", config.embed_color))

    async def press(self, interaction, label):
        await interaction.response.defer()
        async with self.lock:
            if self.is_finished():
                return
            if label == "Exit":
                for item in self.children:
                    item.disabled = True
                self.stop()
            elif label == "Clear":
                self.expression = ""
                self.display = "0"
            elif label == "?":
                self.expression = self.expression[:-1]
                self.display = self.expression or "0"
            elif label == "=":
                try:
                    result = await evaluate(self.expression)
                    self.expression = str(result)
                    self.display = str(result)
                except (ValueError, TypeError, ArithmeticError, OverflowError, asyncio.TimeoutError):
                    self.display = "Invalid calculation"
            else:
                if label in ("+", "-", "x", ":", "."):
                    if not self.expression and label not in ("-", "."):
                        return
                    if self.expression and self.expression[-1] in "+-x:.":
                        self.expression = self.expression[:-1]
                if len(self.expression) + len(label) <= 500:
                    self.expression += label
                self.display = self.expression or "0"
            await interaction.edit_original_response(content="Exited" if self.is_finished() else None, embed=self.embed(), view=self)


class Calculator(commands.Cog):
    @commands.hybrid_command(description="Open a graphical calculator")
    async def calculator(self, ctx):
        view = CalculatorView(ctx.author)
        await send_result(ctx, view.embed(), view=view)


async def setup(bot):
    await bot.add_cog(Calculator())
