import discord, os, logging, warnings, json
from discord.ext import commands

from discord_slash import SlashCommand

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
slash = SlashCommand(client, sync_commands=True, sync_on_cog_reload=True, delete_from_unused_guilds=True)
client.remove_command("help")

logging.basicConfig(
    handlers=[logging.FileHandler("./data/log.log", "a", "utf-8")],
    level=logging.INFO,
    format="%(asctime)s %(message)s",
    datefmt="%m/%d/%Y %I:%M:%S %p",
)
warnings.filterwarnings("ignore")

slash = ['bot', 'kr']

@client.event
async def on_ready():
    print("Logged in as {0} ({0.id})".format(client.user))
    logging.info(" | Logged in as {0} ({0.id})".format(client.user))
    print("{0} is ready".format(client.user))
    logging.info(" | {0} is ready".format(client.user))

@client.event
async def on_command_error(ctx, error):
    if isinstance(error, commands.CommandNotFound):
        pass

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
