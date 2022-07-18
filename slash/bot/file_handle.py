import discord, os, json
from discord.ext import commands

from config import config

client = discord.Client()

class File(commands.Cog):

    def __init__(self, client):
        self.client = client
        self.cogs = ['bot', 'kr']

    @commands.command(aliases=['slash-load'])
    @commands.is_owner() # load slash file/extension
    async def slash_load(self, ctx, ext=None):
        if ext is None:
            embed = discord.Embed(
                title='Load Command (Bot owner)',
                description=f'Syntax:\n`load <extension/file>`\nLoad a(n) extension/file.',
                colour=config.embed_color,
            )
            await ctx.reply(embed=embed)
        else:
            await self.get_file(ctx, ext, 'load')

    @commands.command(aliases=['slash-unload'])
    @commands.is_owner() # unload slash file/extension
    async def slash_unload(self, ctx, ext=None):
        if ext is None:
            embed = discord.Embed(
                title='Unload Command (Bot owner)',
                description=f'Syntax:\n`unload <extension/file>`\nUnload a(n) extension/file.',
                colour=config.embed_color,
            )
            await ctx.reply(embed=embed)
        else:
            await self.get_file(ctx, ext, 'unload')

    @commands.command(aliases=['slash-reload'])
    @commands.is_owner() # reload slash file/extension
    async def slash_reload(self, ctx, ext=None):
        if ext is None:
            embed = discord.Embed(
                title='Reload Command (Bot owner)',
                description=f'Syntax:\n`reload <extension/file>`\nReload a(n) extension/file.',
                colour=config.embed_color,
            )
            await ctx.reply(embed=embed)
        else:
            await self.get_file(ctx, ext, 'reload')

    async def get_file(self, ctx, extension, action): # get file
        files = 0
        for folder in self.cogs: # first loop to get all files
            for filename in os.listdir(f'./slash/{folder}'):
                if filename.endswith('.py'):
                    files += 1            
        files_ = 0
        for folder in self.cogs: # second loop to find files
            for filename in os.listdir(f'./slash/{folder}'):
                if filename.endswith('.py'):
                    if '/' in folder:
                        folder = folder.replace('/', '.')
                    if filename[:-3] == extension:
                        try:
                            if action == 'load':
                                self.client.load_extension(f'slash.{folder}.{filename[:-3]}')
                                await ctx.reply(f'Loaded `{extension}.py`')
                            elif action == 'unload':
                                self.client.unload_extension(f'slash.{folder}.{filename[:-3]}')
                                await ctx.reply(f'Unloaded `{extension}.py`')
                            else:
                                self.client.reload_extension(f'slash.{folder}.{filename[:-3]}')
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