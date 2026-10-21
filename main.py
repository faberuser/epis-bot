import json
import logging
import re
from itertools import cycle
from pathlib import Path

import discord
from discord.ext import commands, tasks

import settings

DATA = Path("data")
COG_FOLDERS = ("bot", "kr", "tasks")
log = logging.getLogger(__name__)


def determine_prefix(bot, message):
    if message.guild is None:
        return settings.PREFIX
    try:
        with (DATA / "prefixes.json").open(encoding="utf-8") as source:
            return json.load(source).get(str(message.guild.id), settings.PREFIX)
    except (FileNotFoundError, json.JSONDecodeError):
        return settings.PREFIX


def extension_names():
    for folder in COG_FOLDERS:
        for path in sorted(Path("cogs", folder).glob("*.py")):
            if not path.name.startswith("__"):
                yield f"cogs.{folder}.{path.stem}"


class EpisContext(commands.Context):
    data_version: str | None = None


class EpisBot(commands.Bot):
    def __init__(self):
        intents = discord.Intents.default()
        intents.message_content = True
        super().__init__(
            command_prefix=determine_prefix,
            case_insensitive=True,
            intents=intents,
            help_command=None,
        )
        self.extension_failures = []
        self.statuses = cycle(
            [
                discord.Game(name="lewd jane"),
                discord.Game(name="king's r*pe"),
                discord.Activity(
                    type=discord.ActivityType.watching,
                    name="kr girl's pantsu",
                ),
                discord.Activity(
                    type=discord.ActivityType.listening,
                    name="kr girl's lewd voices",
                ),
            ]
        )

    async def setup_hook(self):
        DATA.mkdir(exist_ok=True)
        await self.load_extensions()
        self.change_status.start()

    async def get_context(
        self, origin, /, *, cls: type[commands.Context] = EpisContext
    ):
        ctx = await super().get_context(origin, cls=cls)
        if ctx.interaction is None and ctx.command and "version" in ctx.command.params:
            arguments = ctx.view.buffer[ctx.view.index :]
            match = re.search(
                r"(?:^|\s)(?:--version|-V)(?:=|\s+)([\w-]+)(?=\s|$)", arguments
            )
            if match and isinstance(ctx, EpisContext):
                ctx.data_version = match.group(1)
                ctx.view = type(ctx.view)(
                    arguments[: match.start()] + " " + arguments[match.end() :]
                )
        if ctx.interaction is None and ctx.command and ctx.command.name == "uts":
            arguments = ctx.view.buffer[ctx.view.index :]
            match = re.match(r"\s*([1-4])(?=\s|$)", arguments)
            if match:
                # Route `ut 4 Epis` to `ut4 Epis` before parsing hero and stars.
                command = self.get_command(f"ut{match.group(1)}")
                if command is not None:
                    ctx.command = command
                    ctx.view = type(ctx.view)(arguments[match.end() :].lstrip())
        return ctx

    async def load_extensions(self):
        failures = []
        for extension in extension_names():
            try:
                if extension in self.extensions:
                    await self.reload_extension(extension)
                else:
                    await self.load_extension(extension)
                log.info("Loaded %s", extension)
            except commands.ExtensionError:
                failures.append(extension)
                log.exception("Failed to load %s", extension)
        self.extension_failures = failures
        return failures

    @tasks.loop(minutes=1)
    async def change_status(self):
        await self.change_presence(activity=next(self.statuses))

    @change_status.before_loop
    async def before_change_status(self):
        await self.wait_until_ready()

    async def on_ready(self):
        if self.user is not None:
            log.info("Logged in as %s (%s)", self.user, self.user.id)

    async def close(self):
        self.change_status.cancel()
        await super().close()


def create_bot():
    bot = EpisBot()

    @bot.command()
    @commands.is_owner()
    async def fetch(ctx, action=None):
        if action in ("extension", "extensions"):
            failures = await bot.load_extensions()
            await ctx.send(
                "Failed to load: " + ", ".join(failures)
                if failures
                else "Fetched all extensions."
            )
        elif action in ("file", "files"):
            await bot.reload_extension("cogs.bot.file_handle")
            await ctx.send("Reloaded `file_handle.py`.")
        else:
            await ctx.send("Usage: `fetch <extensions/file>`")

    @bot.command(name="sync")
    @commands.is_owner()
    async def sync_commands(ctx, scope: str = "guild"):
        """Publish the loaded application commands only when the owner asks."""
        if bot.extension_failures:
            await ctx.send(
                "Fix failed extensions before synchronizing: "
                + ", ".join(bot.extension_failures)
            )
            return
        if scope == "guild":
            if ctx.guild is None:
                await ctx.send("Run this in your test server, or use `sync global`.")
                return
            guild = discord.Object(id=ctx.guild.id)
            bot.tree.copy_global_to(guild=guild)
            synced = await bot.tree.sync(guild=guild)
        elif scope == "global":
            synced = await bot.tree.sync()
        else:
            await ctx.send("Usage: `sync guild` or `sync global`.")
            return
        await ctx.send(f"Synced {len(synced)} application commands ({scope}).")

    @bot.tree.error
    async def application_command_error(interaction, error):
        log.error(
            "Application command failed",
            exc_info=(type(error), error, error.__traceback__),
        )
        message = "This command failed. Please try again later."
        if interaction.response.is_done():
            await interaction.followup.send(message, ephemeral=True)
        else:
            await interaction.response.send_message(message, ephemeral=True)

    return bot


def main():
    if not settings.DISCORD_TOKEN:
        raise RuntimeError(
            "Set DISCORD_TOKEN in the environment or project .env file before starting the bot."
        )
    DATA.mkdir(exist_ok=True)
    logging.basicConfig(
        handlers=[
            logging.FileHandler(DATA / "log.log", "a", "utf-8"),
            logging.StreamHandler(),
        ],
        level=logging.INFO,
        format="%(asctime)s %(levelname)s %(name)s: %(message)s",
    )
    create_bot().run(settings.DISCORD_TOKEN, reconnect=True, log_handler=None)


if __name__ == "__main__":
    main()
