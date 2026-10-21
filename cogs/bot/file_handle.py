import os

import discord
from discord.ext import commands

import settings


class File(commands.Cog):
    def __init__(self, client):
        self.client = client
        self.cogs = ["bot", "kr", "tasks"]

    @commands.command(aliases=["slash_load", "slash-load"])  # load file/extensions
    @commands.is_owner()
    async def load(self, ctx, ext=None):
        if ext is None:
            embed = discord.Embed(
                title="Load Command (Bot owner)",
                description="Syntax:\n`load <extension/file>`\nLoad a(n) extension/file.",
                colour=settings.EMBED_COLOR,
            )
            await ctx.reply(embed=embed)
        else:
            await self.get_file(ctx, ext, "load")

    @commands.command(
        aliases=["slash_unload", "slash-unload"]
    )  # unload file/extensions
    @commands.is_owner()
    async def unload(self, ctx, ext=None):
        if ext is None:
            embed = discord.Embed(
                title="Unload Command (Bot owner)",
                description="Syntax:\n`unload <extension/file>`\nUnload a(n) extension/file.",
                colour=settings.EMBED_COLOR,
            )
            await ctx.reply(embed=embed)
        else:
            await self.get_file(ctx, ext, "unload")

    @commands.command(
        aliases=["slash_reload", "slash-reload"]
    )  # reload file/extensions
    @commands.is_owner()
    async def reload(self, ctx, ext=None):
        if ext is None:
            embed = discord.Embed(
                title="Reload Command (Bot owner)",
                description="Syntax:\n`reload <extension/file>`\nReload a(n) extension/file.",
                colour=settings.EMBED_COLOR,
            )
            await ctx.reply(embed=embed)
        else:
            await self.get_file(ctx, ext, "reload")

    @commands.command()  # remove command
    @commands.is_owner()
    async def remove(self, ctx, name=None):
        if name is None:
            embed = discord.Embed(
                title="Remove Command (Bot owner)",
                description="Syntax:\n`remove <command>`\nRemove a command.",
                colour=settings.EMBED_COLOR,
            )
            await ctx.reply(embed=embed)
        else:
            self.client.remove_command(name)
            await ctx.reply(f"Removed `{name}` command")

    async def get_file(self, ctx, extension, action):  # get file
        files = 0
        for folder in self.cogs:  # first loop to get all files
            for filename in os.listdir(f"./cogs/{folder}"):
                if filename.endswith(".py"):
                    files += 1
        files_ = 0
        for folder in self.cogs:  # second loop to find files
            for filename in os.listdir(f"./cogs/{folder}"):
                if filename.endswith(".py"):
                    if "/" in folder:
                        folder = folder.replace("/", ".")
                    if filename[:-3] == extension:
                        try:
                            if action == "load":
                                await self.client.load_extension(
                                    f"cogs.{folder}.{filename[:-3]}"
                                )
                                await ctx.reply(f"Loaded `{extension}.py`")
                            elif action == "unload":
                                await self.client.unload_extension(
                                    f"cogs.{folder}.{filename[:-3]}"
                                )
                                await ctx.reply(f"Unloaded `{extension}.py`")
                            else:
                                await self.client.reload_extension(
                                    f"cogs.{folder}.{filename[:-3]}"
                                )
                                await ctx.reply(f"Reloaded `{extension}.py`")
                        except commands.ExtensionError as e:
                            await ctx.reply(
                                f"Failed to load {filename}. Exception:\n```{e}```"
                            )
                    else:
                        files_ += 1
        if files == files_:
            await ctx.reply(f"Extension `{extension}` not found.")


async def setup(client):
    await client.add_cog(File(client))
