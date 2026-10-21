"""User-selected language for game-data commands."""

import discord
from discord import app_commands
from discord.ext import commands

import settings

from ..utils.game_data import available_languages, selected_language
from ..utils.user_preferences import preferences

LANGUAGE_NAMES = {
    "de": "German",
    "en": "English",
    "fr": "French",
    "ja": "Japanese",
    "ko": "Korean",
    "ru": "Russian",
    "zh-Hans": "Simplified Chinese",
    "zh-Hant": "Traditional Chinese",
}


async def language_autocomplete(interaction, current):
    choices = [
        (code, f"{code} — {LANGUAGE_NAMES.get(code, code)}")
        for code in available_languages()
    ]
    choices.append(("reset", "reset — Use the bot default"))
    return [
        app_commands.Choice(name=label, value=code)
        for code, label in choices
        if current.casefold() in label.casefold()
    ][:25]


class Language(commands.Cog):
    @commands.hybrid_command(
        aliases=["lang"], description="View or save your preferred game-data language"
    )
    @app_commands.autocomplete(code=language_autocomplete)
    async def language(self, ctx, code: str | None = None):
        if code is None:
            language = selected_language(ctx)
            embed = discord.Embed(
                title="Your game-data language",
                description=f"`{language}` — {LANGUAGE_NAMES.get(language, language)}\nUse `language <code>` to change it or `language reset` to use the bot default.",
                colour=settings.EMBED_COLOR,
            )
            embed.add_field(
                name="Available languages",
                value="\n".join(
                    f"`{value}` — {LANGUAGE_NAMES.get(value, value)}"
                    for value in available_languages()
                ),
            )
            await ctx.send(embed=embed)
            return
        if code.casefold() in ("reset", "default"):
            preferences.set_language(ctx.author.id, None)
            await ctx.send(
                f"Your game-data language now follows the bot default: `{settings.KR_LANGUAGE}`."
            )
            return
        languages = {value.casefold(): value for value in available_languages()}
        language = languages.get(code.casefold())
        if language is None:
            raise commands.BadArgument(
                "Unknown language. Choose: "
                + ", ".join(languages.values())
                + ", or reset."
            )
        preferences.set_language(ctx.author.id, language)
        await ctx.send(
            f"Your default game-data language is now `{language}` — {LANGUAGE_NAMES.get(language, language)}."
        )


async def setup(bot):
    await bot.add_cog(Language())
