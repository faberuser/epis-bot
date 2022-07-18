import discord, os, logging, warnings, json
from datetime import datetime
from itertools import cycle
from discord.ext import commands, tasks

from discord_slash import SlashCommand

from config import config

TOKEN = config.DISCORD_TOKEN
PREFIX = config.PREFIX

def determine_prefix(client, message):
    with open('./data/prefixes.json', 'r') as f:
        prefixes = json.load(f)
    try:
        if str(message.guild.id) not in prefixes:
            return PREFIX
        else:
            return prefixes[str(message.guild.id)]
    except:
        return PREFIX

client = discord.Client()
client = commands.Bot(command_prefix=determine_prefix, case_insensitive=True)
slash = SlashCommand(client, sync_commands=True, sync_on_cog_reload=True, delete_from_unused_guilds=True)
client.remove_command("help")

logging.basicConfig(
    handlers=[logging.FileHandler("./data/log.log", "a", "utf-8")],
    level=logging.INFO,
    format="%(asctime)s %(message)s",
    datefmt="%m/%d/%Y %I:%M:%S %p",
)
warnings.filterwarnings("ignore")

status = cycle(
    [
        discord.Game(name=f"League of Gacha | /help"),
        discord.Game(name=f"lewd Jane | /help"),
        discord.Game(name=f"King's R*pe | /help"),
        discord.Activity(
            type=discord.ActivityType.watching,
            name=f"King's Raid girl's pantsu | /anime",
        ),
        discord.Activity(
            type=discord.ActivityType.listening,
            name=f"King's Raid girl's lewd voices | /voice",
        ),
    ]
)

cogs = ['bot', 'kr', 'tasks']
slash = ['bot', 'kr']

@client.command()
@commands.is_owner()
async def fetch(ctx, action=None):
    if action == 'commands' or action == 'command':
        commands_()
        await ctx.send('Fetched all commands.')
    elif action == 'extensions' or action == 'extension':
        extensions_()
        await ctx.send('Fetched all extensions.')
    elif action == 'file' or action == 'files':
        client.reload_extension(f'cogs.bot.file_handle')
        await ctx.send('Reloaded `file_handle.py`.')
    else:
        embed = discord.Embed(
                title='Fetch Command (Bot owner)',
                description='Syntax:\n`/fetch <command/extension/file>`\nFetch commands/extensions/files.',
                colour=discord.Colour.dark_red(),
            )
        await ctx.send(embed=embed)

@tasks.loop(minutes=1)
async def change_status():
    await client.change_presence(status=None, activity=next(status))

@change_status.before_loop
async def before_change_status():
    await client.wait_until_ready()

@client.event
async def on_ready():
    change_status.start()
    try:
        with open('./data/time', 'w') as f:
            f.write(str(datetime.utcnow()))
    except FileNotFoundError:
        with open('./data/time', 'a') as f:
            f.write(str(datetime.utcnow()))
    commands_()
    extensions_()
    print("Logged in as {0} ({0.id})".format(client.user))
    logging.info(" | Logged in as {0} ({0.id})".format(client.user))
    print("{0} is ready".format(client.user))
    logging.info(" | {0} is ready".format(client.user))

def commands_():
    open('./data/commands', 'a').close()
    for command in client.commands:
        with open('./data/commands', 'a', encoding="utf-8") as f:
            name = str(command.name)
            f.write(name + '\n')
            aliases = command.aliases
            if str(aliases) == '[]': pass
            else:
                for aliase in aliases:
                    f.write(aliase + '\n')


def extensions_():
    for folder in cogs:
        for filename in os.listdir(f'./cogs/{folder}'):
            if filename.endswith('.py'):
                if filename.startswith('chat'):
                    continue
                if '/' in folder:
                    folder = folder.replace('/', '.')
                try:
                    client.load_extension(f'cogs.{folder}.{filename[:-3]}')
                    print(f'Loaded {filename}')
                except:
                    client.reload_extension(f'cogs.{folder}.{filename[:-3]}')
                    print(f'Reloaded {filename}')
    try:
        if config.api == True:
            client.load_extension(f'cogs.bot.chat-api')
            print('Loaded chat-api.py')
        else:
            client.load_extension(f'cogs.bot.chat-base')
            print('Loaded chat-base.py')
    except Exception as e:
        print(e)

def slash_commands():
    for folder in slash:
        for filename in os.listdir(f'./slash/{folder}'):
            if filename.endswith('.py'):
                if '/' in folder:
                    folder = folder.replace('/', '.')
                try:
                    client.load_extension(f'slash.{folder}.{filename[:-3]}')
                    print(f'Loaded {filename} - slash')
                except:
                    client.reload_extension(f'slash.{folder}.{filename[:-3]}')
                    print(f'Reloaded {filename} - slash')
slash_commands()

client.run(TOKEN, reconnect=True)
