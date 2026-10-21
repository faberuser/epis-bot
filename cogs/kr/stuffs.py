import random
import re
import shlex

from discord.ext import commands


class Stuffs(commands.Cog):
    def __init__(self, client):
        self.client = client

    @commands.hybrid_command(
        name="choose",
        aliases=["random", "pick"],
        description="Choose from words, quoted phrases, or a list separated by pipes",
    )
    async def random(self, ctx, *, choices: str | None = None):
        if not choices:
            await ctx.send(
                "Usage: `choose apple orange` or `choose first option | second option`."
            )
            return
        for opening, closing in (("(", ")"), ("[", "]"), ("{", "}")):
            if choices.startswith(opening) and choices.endswith(closing):
                choices = choices[1:-1].replace(closing + " " + opening, " | ")
                break
        separated = re.split(r"\s+[|/&-]\s+|\s+or\s+|[,;]\s*", choices)
        try:
            options = (
                [s.strip() for s in separated if s.strip()]
                if len(separated) > 1
                else shlex.split(choices)
            )
        except ValueError:
            raise commands.BadArgument("Please close quoted choices.")
        if not options:
            raise commands.BadArgument("Provide at least one choice.")
        await ctx.send("I pick `" + random.choice(options).replace("`", "") + "`.")


async def setup(client):
    await client.add_cog(Stuffs(client))
