import discord, os, logging, json
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
    handlers=[logging.FileHandler("./data/tasks.log", "a", "utf-8")],
    level=logging.INFO,
    format="%(asctime)s %(message)s",
    datefmt="%m/%d/%Y %I:%M:%S %p",
)

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

cogs = ['tasks']

for folder in cogs:
    for filename in os.listdir(f'./cogs/{folder}'):
        if filename.endswith('.py'):
            if '/' in folder:
                folder = folder.replace('/', '.')
            client.load_extension(f'cogs.{folder}.{filename[:-3]}')
            print(f'Loaded {filename}')


@tasks.loop(minutes=5)
async def change_status():
    await client.change_presence(status=None, activity=next(status))


@change_status.before_loop
async def before_change_status():
    await client.wait_until_ready()


@client.event
async def on_ready():
    change_status.start()
    print("Logged in as {0} ({0.id})".format(client.user))
    print("Checking Tasks...")
    logging.info(" | Logged in as {0} ({0.id})".format(client.user))
    logging.info(" | Checking Tasks...")


@client.event
async def on_command_error(ctx, error):
    if isinstance(error, commands.CommandNotFound):
        pass


client.run(TOKEN, reconnect=True, bot=True)
