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

### Optional

# Policy URL
POLICY = "https://epis-bot-policy.netlify.app/"

# Donate URL
donate = ""

# System OS
windows = True

# Send announcements from official page
parallel_tasks = False # Set to True if the bot has large amount of channels registered, otherwise set to False is recommended

# KRE Guides
kre_guild_id = 748599474783518941 # KRE
kre_categories = [
    748635757056491649, # TABLE OF CONTENTS
    748600039542358058, # BEGINNER GUIDES
    748605214856183819, # OPTIMIZATION
    748647024060137605, # GEAR
    748605466401046659, # CONTENT GUIDES
    748599866967457873, # HERO GUIDES (A-J)
    748607570226315346, # HERO GUIDES (K-Q)
    748612701973905499, # HERO GUIDES (R-Z)
    748610529194541139 # PVP
    ]
kre_invite = 'https://discord.gg/cBeMt8jAST'

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