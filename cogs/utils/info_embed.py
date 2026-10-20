import discord

import settings


class Info_Embed:
    def info_embed(self, cmd: str, client_name=None):  # get help embed
        if cmd == "Heroes":
            embed = discord.Embed(
                title="Hero command(s)",
                description=(
                    "Syntax:\n`hero list`: Shows King's Raid Heroes\n"
                    + "`info <class/hero>`: Shows Hero basic information.\n`skills <class/hero>`: Shows Hero skills.\n`books <class/hero>`: Shows Hero books.\n"
                    + "`perks <class/hero>`: Shows Hero Perks/Transcend.\n`uw <class/hero/name>`: Shows Hero Unique Weapon.\n"
                    + "`ut <class/hero/name>` | `ut<number> <class/hero/name>` | `ut <number> <class/hero/name>`: Shows Hero Unique Treasures.\n"
                    + "`sw <class/hero/name>`: Shows Hero Soul Weapon/Unique Skill.\n`splashart <class/hero>`: Shows Hero Splashart/Loading Screen.\n"
                    + "`visual <class/hero>`: Shows First Hero generation Visual Splashart.\n`costume <class/hero>`: Shows Hero costumes.\n`npc`: Shows NPC Heroes effect."
                ),
                colour=settings.EMBED_COLOR,
            )
        elif cmd == "Info":
            embed = discord.Embed(
                title="Info command(s)",
                description="Syntax:\n`info <class/hero>`: Shows Hero Info.\n`info <number/name>`: Shows Boss information.",
                colour=settings.EMBED_COLOR,
            )
        elif cmd == "Skills":
            embed = discord.Embed(
                title="Skills command(s)",
                description="Syntax:\n`skills <class/hero>`: Shows Hero skills.\n`skills <number/name>`: Shows Boss skills.",
                colour=settings.EMBED_COLOR,
            )
        elif cmd == "Perks":
            embed = discord.Embed(
                title="Perks command(s)",
                description="Syntax:\n`perks <class/hero>`\n`trans <class/hero>`\nShows Hero Perks/Transcend.",
                colour=settings.EMBED_COLOR,
            )
        elif cmd == "Books":
            embed = discord.Embed(
                title="Books command(s)",
                description="Syntax:\n`books <class/hero>`: Shows Hero Books.",
                colour=settings.EMBED_COLOR,
            )
        elif cmd == "Splashart":
            embed = discord.Embed(
                title="Splashart command(s)",
                description="Syntax:\n`splashart <class/hero>`: Shows Hero Splashart/Loading Screen",
                colour=settings.EMBED_COLOR,
            )
        elif cmd == "Visual":
            embed = discord.Embed(
                title="Visual command(s)",
                description=(
                    "Syntax:\n`visual <class/hero>`: Shows first Hero generation Visual Splashart.\n\n"
                    + "*First Hero generation: Kasel, Frey, Cleo, Roi, Clause, Morrah, Maria, Selene, Lorraine*"
                ),
                colour=settings.EMBED_COLOR,
            )
        elif cmd == "Costumes":
            embed = discord.Embed(
                title="Costumes command(s)",
                description=(
                    "Syntax:\n`costume <class/hero>`\n`cos <class/hero>`\n`skin <class/hero>`\nShows Hero's costume(s).\n\n"
                    + "Use the selection menu to choose a costume and the buttons to change pages.\n"
                    + "Menus can only be controlled by the person who opened them."
                ),
                colour=settings.EMBED_COLOR,
            )
        elif cmd == "UW":
            embed = discord.Embed(
                title="UWs command(s)",
                description="Syntax:\n`uw <class/hero/name>`\nShows Hero Unique Weapon.",
                colour=settings.EMBED_COLOR,
            )
        elif cmd == "SW":
            embed = discord.Embed(
                title="SWs command(s)",
                description="Syntax:\n`sw <class/hero/name>`\n`us <class/hero/name>`\nShows Hero Soul Weapon/Unique Skill.",
                colour=settings.EMBED_COLOR,
            )
        elif cmd == "UTs":
            embed = discord.Embed(
                title="UTs command(s)",
                description="Syntax:\n`ut <class/hero/name>`\n`ut<number> <class/hero/name>`\n`ut <number> <class/hero/name>`\nShows Hero Unique Treasures.",
                colour=settings.EMBED_COLOR,
            )
        elif cmd == "UT1":
            embed = discord.Embed(
                title="UT1 command(s)",
                description="Syntax:\n`ut1 <class/hero>`\n`ut 1 <class/hero>`\nShows Hero Unique Treasure 1.",
                colour=settings.EMBED_COLOR,
            )
        elif cmd == "UT2":
            embed = discord.Embed(
                title="UT2 command(s)",
                description="Syntax:\n`ut2 <class/hero>`\n`ut 2 <class/hero>`\nShows Hero Unique Treasure 2.",
                colour=settings.EMBED_COLOR,
            )
        elif cmd == "UT3":
            embed = discord.Embed(
                title="UT3 command(s)",
                description="Syntax:\n`ut3 <class/hero>`\n`ut 3 <class/hero>`\nShows Hero Unique Treasure 3.",
                colour=settings.EMBED_COLOR,
            )
        elif cmd == "UT4":
            embed = discord.Embed(
                title="UT4 command(s)",
                description="Syntax:\n`ut4 <class/hero>`\n`ut 4 <class/hero>`\nShows Hero Unique Treasure 4.",
                colour=settings.EMBED_COLOR,
            )
        elif cmd == "Bosses":
            embed = discord.Embed(
                title="Boss command(s)",
                description=(
                    "Syntax:\n`boss`, `boss list`, or `boss all`: Lists bosses.\n"
                    "`boss <name/alias>`: Shows information using the shared info lookup (e.g. `boss wb1`).\n"
                    "`info <name/alias>`: Shows Boss information.\n`skills <name/alias>`: Shows Boss skills.\n"
                    "Use `--version <name>` or `-V <name>` with prefix commands or the slash `version` option to choose a dataset.\n\n"
                    + "Currently supported Boss content: Guild Raid / Guild Conquest / World Boss / Trial of God King / Shakmeh / Technomagic."
                ),
                colour=settings.EMBED_COLOR,
            )
        elif cmd == "Artifacts":
            embed = discord.Embed(
                title="Artifact command(s)",
                description=(
                    "Syntax:\n`atf <name>`\n`artifact <name>`\nShows Artifact information.\n"
                    + "\n`atf search <number:default=10> <name>`\n`artifact search <number:default=10> <name>`\nSearch Artifacts.\n"
                    + "\n`atf <all/list>`\n`artifact <all/list>`\nShows all Artifacts."
                ),
                colour=settings.EMBED_COLOR,
            )
        elif cmd in ("Announcements", "Twitter", "Steam"):
            embed = discord.Embed(
                title=f"{cmd} commands",
                description=(
                    "Use your configured prefix or slash commands.\n"
                    "Manage Channels is required to turn subscriptions on or off.\n"
                    "The bot needs View Channel, Send Messages, and Embed Links."
                ),
                colour=settings.EMBED_COLOR,
            )
            if cmd in ("Announcements", "Twitter"):
                embed.add_field(
                    name="Twitter / X",
                    value="`twitter on/off/status`: Follow [@kingsraid_msg](https://x.com/kingsraid_msg) using the X API. Requires BEARER_TOKEN with user lookup and timeline access.",
                    inline=False,
                )
            if cmd in ("Announcements", "Steam"):
                embed.add_field(
                    name="Steam",
                    value="`steam on/off/status`: Follow [KING's RAID RE:VERSE](https://store.steampowered.com/app/3689540/). No Steam key required.",
                    inline=False,
                )
        elif cmd == "Math":
            embed = discord.Embed(
                title="Math command(s)",
                description="Syntax:\n`calc <operation>`\n`math <operation>`\nCalculates an Operation.",
                colour=settings.EMBED_COLOR,
            )
        elif cmd == "Softcap":
            embed = discord.Embed(
                title="Softcap command(s)",
                description=(
                    "Syntax:\n`softcap <value>`\n`soft <value>`\n`cap <value>`\nShows a Softcap table.\n\n"
                    + "*Thanks to [Duckness](https://github.com/duckness) for this command.*"
                ),
                colour=settings.EMBED_COLOR,
            )
        else:
            raise ValueError(f"Unknown help topic: {cmd}")
        return embed
