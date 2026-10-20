# epis-bot

A Discord Bot made for King's Raid mobile game

## You can get

- Heroes's information, skills, perks, books, uws, uts, sws, splashart, visual splashart, costumes.
- Artifacts's information, Bosses's information and skills.
- The newest posts from [KINGs RAID Official Community](https://kr-official.community/) up to 3 languages and tweets from [KING's RAID OFFICIAL](https://twitter.com/Play_KINGsRAID).
- King's Raid Guide from KR Encyclopedia (the bot need to be in the server).
- Caculator, Softcap and other things.

## Installations

### Requirements

- Python 3.12 (tested).
- Discord Bot's Token from [Discord Developers](https://discord.com/developers/applications).

### Installations

- Use Virtual Environment:
    - Create virtual environment `virtualenv .env`.
    - Activate:
        - Windows `.env\Scripts\activate`.
        - Linux `source .env/bin/activate`.

1. Install requirements `pip3 install -r requirements.txt`.

2. Open config/config.py and edit value behind the equal `=`.

    #### Required
    - `PREFIX` is your optional default bot prefix(es).
    - `DISCORD_TOKEN` is your bot's token from the above requirements.
    - You can pick color for `embed_color` on [discord.py](https://discordpy.readthedocs.io/en/stable/api.html?highlight=colour#discord.Colour).
      ![discord.py Colour](/readme/colour.png)
    - `guild_ids` - servers's ids.

    #

    #### Optional
    - Set `windows` to False if your system isn't Windows.
    - Set `parellel_tasks` to True if your Bot has large amount of announce channels registerd for faster post-sending to channels. Otherwise set to False is recommended, use parallel tasks in small amount of channel may decreases speed.

    #

    > #### King's Raid Encyclopedia Guides
    - `guide_id` - the server's id.
    - `categories` - ids of **CATEGORIES**
    - `kre_invite` - server invite url

    ###### Discord Bot can only access content in the server if it's already in it. If your bot is unable to join KRE, you can manually copy contents in KRE to your server then edit the values under KRE Guides section in `config/config.py`.

    #

    > #### Twitter API
    >
    > _Which get newest tweets from [KING's RAID OFFICIAL](https://twitter.com/Play_KINGsRAID), leave blank will disable this module_

    ###### You can get 4 tokens from [Twitter API](https://developer.twitter.com/en/docs/twitter-api/getting-started/getting-access-to-the-twitter-api).

    #

    > #### Custom Emojis (Heroes, Artifacts) Set up

    ###### This may take a bit more of time, just for some listing function like `heroes`, `perks <class>` or `artifact all`. You can also freely to skip this.

    ###### Upload each hero's icons `kr/assets/heroes/<hero>/ico.png` to your servers (3 if 50 emojis in each server) and each artifact's icons in `kr/assets/artifacts`. Then manually copy all these ids (right-click the emoji and `Open Link`, the id is the long int in the url), then edit each one in `data/emojis.json`.

3. Run `python main.py`.
