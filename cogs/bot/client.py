import asyncio
import json
from pathlib import Path

import discord
from discord.ext import commands

import settings

from ..utils.info_embed import Info_Embed
from ..utils.paginator import Paginator

PREFIX_PATH = Path(__file__).resolve().parents[2] / "data" / "prefixes.json"


def read_prefixes() -> dict[str, list[str]]:
    try:
        return json.loads(PREFIX_PATH.read_text(encoding="utf-8"))
    except (FileNotFoundError, json.JSONDecodeError):
        return {}


def write_prefixes(prefixes: dict[str, list[str]]) -> None:
    PREFIX_PATH.parent.mkdir(parents=True, exist_ok=True)
    PREFIX_PATH.write_text(json.dumps(prefixes, indent=4), encoding="utf-8")


class Info(commands.Cog):
    def __init__(self, client):
        self.client = client

    @commands.hybrid_command(
        aliases=["h", "command", "commands", "cmd"], description="Show bot help"
    )
    async def help(self, ctx, *, morehelp: str | None = None):
        prefix = ctx.clean_prefix if ctx.interaction is None else settings.PREFIX[0]
        if morehelp:
            name = morehelp.strip()
            command = self.client.get_command(name)
            if command is None:
                parts = name.split()
                route = self.client.tree.get_command(parts[0]) if parts else None
                for part in parts[1:]:
                    route = (
                        route.get_command(part)
                        if isinstance(route, discord.app_commands.Group)
                        else None
                    )
                command = getattr(route, "wrapped", None)
            topics = {
                "heroes": "Heroes",
                "info": "Info",
                "skill": "Skills",
                "books": "Books",
                "perks": "Perks",
                "uw": "UW",
                "sw": "SW",
                "uts": "UTs",
                "ut1": "UT1",
                "ut2": "UT2",
                "ut3": "UT3",
                "ut4": "UT4",
                "splashart": "Splashart",
                "visual": "Visual",
                "cos": "Costumes",
                "boss": "Bosses",
                "atf": "Artifacts",
                "calc": "Math",
                "softcap": "Softcap",
                "twitter": "Twitter",
                "steam": "Steam",
            }
            topic = topics.get(command.name) if command else None
            if name.lower().startswith(("announce", "plug")):
                topic = "Announcements"
            if topic:
                await ctx.reply(embed=Info_Embed().info_embed(topic))
                return
            if command and command.name == "choose":
                await ctx.reply(
                    embed=discord.Embed(
                        title="Choose Command",
                        description=(
                            "Syntax:\n`choose apple orange`\n"
                            "`choose first option | second option | ...`\n"
                            '`choose "first option" "second option"`\n'
                            "Randomly picks one of the given options."
                        ),
                        colour=settings.EMBED_COLOR,
                    )
                )
                return
            if command is None or command.hidden:
                await ctx.send(
                    f"No command named `{name}` was found.",
                    allowed_mentions=discord.AllowedMentions.none(),
                )
                return
            embed = discord.Embed(
                title=f"{command.qualified_name} help",
                description=command.help
                or command.description
                or "No additional description is available.",
                colour=settings.EMBED_COLOR,
            )
            embed.add_field(
                name="Prefix usage",
                value=f"`{prefix}{command.qualified_name} {command.signature}`",
                inline=False,
            )
            if command.aliases:
                embed.add_field(
                    name="Prefix aliases",
                    value=", ".join(f"`{alias}`" for alias in command.aliases),
                    inline=False,
                )
            if isinstance(command, commands.HybridGroup):
                embed.add_field(
                    name="Subcommands",
                    value=", ".join(
                        f"`{child.name}`"
                        for child in sorted(
                            command.commands, key=lambda child: child.name
                        )
                    ),
                    inline=False,
                )
            if (
                isinstance(command, commands.HybridCommand)
                and command.app_command is not None
            ):
                embed.add_field(
                    name="Slash command",
                    value=f"`/{command.app_command.qualified_name}`",
                    inline=False,
                )
            if "version" in command.params:
                embed.add_field(
                    name="Game data version",
                    value="Use the slash `version` option or prefix `--version <name>` or `-V <name>`. Run `versions` to see available datasets.",
                    inline=False,
                )
            await ctx.send(embed=embed)
            return

        embed1 = discord.Embed(
            title=f"__Commands start with {settings.PREFIX}__",
            description=(
                "__**Hero**__\n"
                "`hero` `info` `skills` `books` `perks` `uw` `ut` `sw` `splashart` `visual` `costume` `npc`\n"
                "__**Artifact**__\n"
                "`artifact` `atf`\n"
                "__**Boss**__\n"
                "`boss` `info` `skills`\n"
                "Game data commands accept the slash `version` option or prefix `--version <name>` or `-V <name>`.\n\n"
                "__**Announcements**__ (Require `Manage Channels` to subscribe)\n"
                "`twitter <on/off/status>`: Send new tweets from [@kingsraid_msg](https://x.com/kingsraid_msg).\n"
                "`steam <on/off/status>`: Send official [KING's RAID RE:VERSE](https://store.steampowered.com/app/3689540/KINGs_RAID_REVERSE/) Steam announcements."
            ),
            colour=settings.EMBED_COLOR,
        )
        embed2 = discord.Embed(
            title=f"__Commands start with {settings.PREFIX}__",
            description=(
                "__**Math**__\n"
                "`calc <operation>`: Calculates something.\n"
                "`softcap <value>`: Shows a Softcap table.\n"
                "__**Other**__\n"
                "`guide <content>/list/search <content>`: Shows guides from KR Encyclopedia.\n"
                "`choose <first option | second option | ...>`: Randomly picks from the given list.\n"
                "`versions`: Lists the available game datasets.\n"
                "`language <code/reset>`: Saves your preferred game-data language.\n"
                "`prefix <prefix>`: Changes this server's prefixes (requires Manage Server).\n"
                "`help <command>`: Shows command syntax and details.\n\n"
            ),
            colour=settings.EMBED_COLOR,
        )
        for index, embed in enumerate((embed1, embed2), 1):
            embed.set_author(
                name=self.client.user.name + " Bot Help",
                icon_url=self.client.user.display_avatar.url,
            )
            embed.set_footer(
                text=f"Page {index}/2 | For more aliases/syntax type command only."
            )
        await Paginator(self.client).pag(ctx, [embed1, embed2])

    @commands.command(aliases=["owner", "botowner"])
    @commands.is_owner()
    async def admin(self, ctx):  # admin command
        embed = discord.Embed(
            title="Bot owner Commands",
            description=(
                "List of commands:\n`fetch <command/extension/file>`: Fetch commands/extensions/files.\n`load <extension/file>`: Load a(n) extension/file.\n"
                + "`unload <extension/file>`: Unload a(n) extension/file.\n`reload <extension/file>`: Reload a(n) extension/file.\n`remove <command>`: Remove a command.\n"
                + "`sync guild`: Publish commands to this test server.\n`sync global`: Publish commands globally."
            ),
            colour=settings.EMBED_COLOR,
        )
        await ctx.reply(embed=embed)

    @commands.command(aliases=["prefixes", "change_prefix", "change_prefixes"])
    @commands.guild_only()
    @commands.has_permissions(manage_guild=True)
    async def prefix(self, ctx, prefix: str | None = None):
        if prefix is None:
            defaults = ", ".join(f"`{value}`" for value in settings.PREFIX)
            await ctx.reply(
                embed=discord.Embed(
                    title="Change Prefix Command (Require Manage Server)",
                    description=f"`prefix <prefix>` toggles a prefix for this server.\n`prefix all` shows current prefixes.\nDefault prefixes: {defaults}.",
                    colour=settings.EMBED_COLOR,
                )
            )
            return
        prefixes = await asyncio.to_thread(read_prefixes)
        current = prefixes.get(str(ctx.guild.id), list(settings.PREFIX))
        if prefix in ("all", "show"):
            await ctx.reply(
                embed=discord.Embed(
                    title=f"{ctx.guild.name}'s Prefixes:",
                    description=", ".join(f"`{value}`" for value in current)
                    or "No prefixes configured.",
                    colour=settings.EMBED_COLOR,
                )
            )
            return
        if prefix in current:
            if len(current) == 1:
                await ctx.send(
                    "This is the last prefix for this server. Remove it? (Y/N)"
                )

                def check(message):
                    return (
                        bool(message.content)
                        and message.author == ctx.author
                        and message.channel == ctx.channel
                    )

                try:
                    answer = await self.client.wait_for(
                        "message", check=check, timeout=30.0
                    )
                except TimeoutError:
                    await ctx.send("Timeout! Please try again.")
                    return
                if answer.content.casefold() not in ("y", "yes"):
                    await ctx.send("Cancelled.")
                    return
            current.remove(prefix)
            response = f"Removed `{prefix}` prefix."
        else:
            current.append(prefix)
            response = f"Added `{prefix}` prefix."
        prefixes[str(ctx.guild.id)] = current
        await asyncio.to_thread(write_prefixes, prefixes)
        await ctx.send(response)

    @commands.Cog.listener()
    async def on_guild_remove(self, guild):
        prefixes = await asyncio.to_thread(read_prefixes)
        if prefixes.pop(str(guild.id), None) is not None:
            await asyncio.to_thread(write_prefixes, prefixes)


async def setup(client):
    cog = Info(client)
    await client.add_cog(cog)
