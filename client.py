import discord, os, logging, warnings, json
from datetime import datetime
from itertools import cycle
from discord.ext import commands, tasks
from config import config

TOKEN = config.DISCORD_TOKEN
PREFIX = config.PREFIX

def determine_prefix(client, message):
    with open('./data/prefixes.json', 'r') as f:
        prefixes = json.load(f)
    if str(message.guild.id) not in prefixes:
        return PREFIX
    else:
        return prefixes[str(message.guild.id)]

client = discord.Client()
client = commands.Bot(command_prefix=determine_prefix, case_insensitive=True)
client.remove_command("help")

logging.basicConfig(
    handlers=[logging.FileHandler("./data/log.log", "a", "utf-8")],
    level=logging.INFO,
    format="%(asctime)s %(message)s",
    datefmt="%m/%d/%Y %I:%M:%S %p",
)
warnings.filterwarnings("ignore")

cogs = ['bot', 'kr']

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

@client.event
async def on_ready():
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
    open('./data/commands', 'w').close()
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
            try:
                client.load_extension(f'cogs.bot.chat-api')
                print('Loaded chat-api.py')
            except:
                print('Missing chat-api.py module')
        else:
            try:
                client.load_extension(f'cogs.bot.chat-base')
                print('Loaded chat-base.py')
            except:
                print('Missing chat-base.py module')
    except Exception as e:
        print(e)


client.run(TOKEN, reconnect=True)
