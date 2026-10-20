import discord
from discord.ext import commands

import settings

from ..utils.game_data import GameData, available_versions, selected_language


class Versions(commands.Cog):
    @commands.hybrid_command(
        aliases=["kr_versions", "version", "kr_version"],
        description="List available game datasets and the default version",
    )
    async def versions(self, ctx):
        default = getattr(settings, "KR_DEFAULT_VERSION", "legacy")
        language = selected_language(ctx)
        embed = discord.Embed(
            title="King's Raid data versions", colour=settings.EMBED_COLOR
        )
        for name in available_versions():
            dataset = GameData(name, language)
            embed.add_field(
                name=name + (" (default)" if name == default else ""),
                value=f"{len(dataset.entities())} heroes, {len(dataset.entities('bosses'))} bosses, {len(dataset.artifacts())} artifacts",
                inline=False,
            )
        embed.set_footer(
            text=f"Language: {language}. Use the slash version option or --version <name> / -V <name> with prefix commands."
        )
        await ctx.send(embed=embed)


async def setup(bot):
    await bot.add_cog(Versions())
