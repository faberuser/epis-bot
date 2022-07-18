from discord import Colour

### Required
PREFIX = ["/", "."]

DISCORD_TOKEN = ""

# default embed color
embed_color = Colour.dark_red()

# Your server id (for adding fanart)
admin_guild = 0

# guild_ids for faster slash command deploy (global slash command take 1 hour to deploy) / leave None to set to global
guild_ids = [0]

# put an unused channel for bot message cache (the bot can't edit message with file so we need to send a embed and get that embed to edit)
cache_channel = 0

# ------------------------------------------------------------------------------------------------------------------------------------------------------------------

### Optinal

# Policy URL
POLICY = "https://epis-bot-policy.netlify.app/"

# Donate URL
donate = ""

# System OS
windows = True

# Send announcements from official page
parallel_tasks = False # Set to True if the bot has large amount of channels registered, otherwise set to False is recommended

# Chat module
api = True # False will set to local AIML engine called programy (program-y) (use requirements-ext.txt)

# Twitter API (for tweet-checking, leave blank will disable)
BEARER_TOKEN = ""
CONSUMER_KEY = ""
CONSUMER_SECRET = ""
ACCESS_TOKEN = ""
ACCESS_TOKEN_SECRET = ""

# Profile on https://top.gg/ (for fanart vote-checking, leave blank will skip vote-checking)
DBL_TOKEN = ""
DBL_URL = ""
DBL_VOTE = ""