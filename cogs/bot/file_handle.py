import discord, os, json
from discord.ext import commands

from config import config

client = discord.Client()

class File(commands.Cog):

    def __init__(self, client):
        self.client = client
        self.cogs = ['bot', 'kr']

    @commands.command() # load file/extensions
    @commands.is_owner()
    async def load(self, ctx, ext=None):
        if ext is None:
            embed = discord.Embed(
                title='Load Command (Bot owner)',
                description=f'Syntax:\n`load <extension/file>`\nLoad a(n) extension/file.',
                colour=config.embed_color,
            )
            await ctx.reply(embed=embed)
        else:
            await self.get_file(ctx, ext, 'load')

    @commands.command() # unload file/extensions
    @commands.is_owner()
    async def unload(self, ctx, ext=None):
        if ext is None:
            embed = discord.Embed(
                title='Unload Command (Bot owner)',
                description=f'Syntax:\n`unload <extension/file>`\nUnload a(n) extension/file.',
                colour=config.embed_color,
            )
            await ctx.reply(embed=embed)
        else:
            await self.get_file(ctx, ext, 'unload')

    @commands.command() # reload file/extensions
    @commands.is_owner()
    async def reload(self, ctx, ext=None):
        if ext is None:
            embed = discord.Embed(
                title='Reload Command (Bot owner)',
                description=f'Syntax:\n`reload <extension/file>`\nReload a(n) extension/file.',
                colour=config.embed_color,
            )
            await ctx.reply(embed=embed)
        else:
            await self.get_file(ctx, ext, 'reload')

    @commands.command() # remove command
    @commands.is_owner()
    async def remove(self, ctx, name=None):
        if name is None:
            embed = discord.Embed(
                title='Remove Command (Bot owner)',
                description=f'Syntax:\n`remove <command>`\nRemove a command.',
                colour=config.embed_color,
            )
            await ctx.reply(embed=embed)
        else:
            self.client.remove_command(name)
            await ctx.reply(f'Removed `{name}` command')

    async def get_file(self, ctx, extension, action): # get file
        files = 0
        for folder in self.cogs: # first loop to get all files
            for filename in os.listdir(f'./cogs/{folder}'):
                if filename.endswith('.py'):
                    files += 1            
        files_ = 0
        for folder in self.cogs: # second loop to find files
            for filename in os.listdir(f'./cogs/{folder}'):
                if filename.endswith('.py'):
                    if '/' in folder:
                        folder = folder.replace('/', '.')
                    if filename[:-3] == extension:
                        try:
                            if action == 'load':
                                self.client.load_extension(f'cogs.{folder}.{filename[:-3]}')
                                await ctx.reply(f'Loaded `{extension}.py`')
                            elif action == 'unload':
                                self.client.unload_extension(f'cogs.{folder}.{filename[:-3]}')
                                await ctx.reply(f'Unloaded `{extension}.py`')
                            else:
                                self.client.reload_extension(f'cogs.{folder}.{filename[:-3]}')
                                await ctx.reply(f'Reloaded `{extension}.py`')
                        except Exception as e:
                            await ctx.reply(f'Failed to load {filename}. Exception:\n```{e}```')
                            pass
                    else:
                        files_ += 1
        if files == files_:
            await ctx.reply(f'Extension `{extension}` not found.')


def setup(client):
    client.add_cog(File(client))