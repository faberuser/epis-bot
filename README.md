# epis-bot
A Discord Bot made for King's Raid mobile game

## You can get
* Heroes's information, skills, perks, books, uws, uts, sws, splashart, visual splashart, costumes.
* Artifacts's information, Bosses's information and skills.
* The newest posts from [KINGs RAID Official Community](https://kr-official.community/) up to 3 languages and tweets from [KING's RAID OFFICIAL](https://twitter.com/Play_KINGsRAID).
* King's Raid Guide from KR Encyclopedia (the bot need to be in the server).
* Caculator, Softcap and other things.

## Installations
### Requirements
* Python >= 3.8.x (didn't test with higher version).
* Discord Bot's Token from [Discord Developers](https://discord.com/developers/applications).

### Installations

* Use Virtual Environment:
    * Create virtual environment `virtualenv .env`.
    * Activate:
        - Windows `.env\Scripts\activate`.
        - Linux `source .env/bin/activate`.

1. Install requirements `pip3 install -r requirements.txt`.

2. Open config/config.py and edit value behind the equal `=`.
    #### Required
    * `PREFIX` is your optional default bot prefix(es).
    * `DISCORD_TOKEN` is your bot's token from the above requirements.
    * You can pick color for `embed_color` on [discord.py](https://discordpy.readthedocs.io/en/stable/api.html?highlight=colour#discord.Colour).
        ![discord.py Colour](/readme/colour.png)
    * `admin_guild` - your server's id.
    * `guild_ids` - servers's ids.
    * `cache_channel` - a throw away channel for posting cache to edit messages (Discord API's limitations).
    #
    #### Optional
    * Set `windows` to False if your system isn't Windows.
    * Set `parellel_tasks` to True if your Bot has large amount of announce channels registerd for faster post-sending to channels. Otherwise set to False is recommended, use parallel tasks in small amount of channel may decreases speed.
    #
    > #### King's Raid Encyclopedia Guides
    * `guide_id` - the server's id.
    * `categories` - ids of **CATEGORIES**
    * `kre_invite` - server invite url
    ###### Discord Bot can only access content in a server if it's already in it. If your bot is unable to join KRE, you can manually copy contents in KRE to your server then edit the values under KRE Guides section in `config/config.py`.
    #
    > #### API
    *Chat module which let you able to talk with the bot by mention it*
    ###### Set `api` to False if you wish to run the chat module on local engine.
    ##### If set to False:
    * Extract **Here** `storage.zip` (`storage` directory with 6 child directories need to be on parent directory).
    * Install requirements **again** from requirements-ext.txt `pip3 install -r requirements-ext.txt`.
    * If you're getting this error: `error: Microsoft Visual C++ 14.0 or greater is required. Get it with "Microsoft C++ Build Tools": https://visualstudio.microsoft.com/visual-cpp-build-tools/`:
        1. Download [Microsoft C++ Build Tools](https://visualstudio.microsoft.com/thank-you-downloading-visual-studio/?sku=BuildTools&rel=16).
        2. Install and make sure to tick same as the picture:
            ![Microsoft C++ Build Tools](/readme/microsoft_build_tools.png)
        3. Install requirements again from requirements-ext.txt (use `pip3 install -r requirements-ext.txt` in the previous terminal).
    * You can edit variables in config/properties.txt to give the bot default answer for some questions.
    ##### Otherwise the bot will use API from [epis-programy](https://github.com/faber6/epis-programy)
    #
    > #### Twitter API
    *Which get newest tweets from [KING's RAID OFFICIAL](https://twitter.com/Play_KINGsRAID), leave blank will disable this module*
    ###### You can get 4 tokens from [Twitter API](https://developer.twitter.com/en/docs/twitter-api/getting-started/getting-access-to-the-twitter-api).
    #
    > #### Profile on https://top.gg/
    *For fanart vote-checking, leave blank will skip vote-checking*
    ###### You can get the variables by upload your bot on [Discord Bot List](https://top.gg/) and be verificated.
    #
    > #### Custom Emojis (Heroes, Artifacts) Set up
    ###### This may take a bit more of time, just for some listing function like `heroes`, `perks <class>` or `artifact all`. You can also freely to skip this.
    ###### Upload each hero's icons `kr/assets/heroes/<hero>/ico.png` to your servers (3 if 50 emojis in each server) and each artifact's icons in `kr/assets/artifacts`. Then manually copy all these ids (right-click the emoji and `Open Link`, the id is the long int in the url), then edit each one in `data/emojis.json`.

3. Run `python main.py`.

###### *I'm no longer maintaning this project so it's data might be 