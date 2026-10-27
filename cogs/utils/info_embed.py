import discord

import settings

HELP_TOPICS = {
    "Heroes": (
        "Hero command(s)",
        (
            "Syntax:\n"
            "`hero list`: Shows King's Raid Heroes\n"
            "`info <class/hero>`: Shows Hero basic information.\n"
            "`skills <class/hero>`: Shows Hero skills.\n"
            "`books <class/hero>`: Shows Hero books.\n"
            "`perks <class/hero>`: Shows Hero Perks/Transcend.\n"
            "`uw <class/hero/name>`: Shows Hero Unique Weapon.\n"
            "`ut <class/hero/name>` | `ut<number> <class/hero/name>` | `ut <number> "
            "<class/hero/name>`: Shows Hero Unique Treasures.\n"
            "`sw <class/hero/name>`: Shows Hero Soul Weapon/Unique Skill.\n"
            "`splashart <class/hero>`: Shows Hero Splashart/Loading Screen.\n"
            "`visual <class/hero>`: Shows First Hero generation Visual Splashart.\n"
            "`costume <class/hero>`: Shows Hero costumes.\n"
            "`npc`: Shows NPC Heroes effect."
        ),
    ),
    "Info": (
        "Info command(s)",
        (
            "Syntax:\n"
            "`info <class/hero>`: Shows Hero Info.\n"
            "`info <number/name>`: Shows Boss information."
        ),
    ),
    "Skills": (
        "Skills command(s)",
        (
            "Syntax:\n"
            "`skills <class/hero>`: Shows Hero skills.\n"
            "`skills <number/name>`: Shows Boss skills."
        ),
    ),
    "Perks": (
        "Perks command(s)",
        (
            "Syntax:\n"
            "`perks <class/hero>`\n"
            "`trans <class/hero>`\n"
            "Shows Hero Perks/Transcend."
        ),
    ),
    "Books": ("Books command(s)", "Syntax:\n`books <class/hero>`: Shows Hero Books."),
    "Splashart": (
        "Splashart command(s)",
        "Syntax:\n`splashart <class/hero>`: Shows Hero Splashart/Loading Screen",
    ),
    "Visual": (
        "Visual command(s)",
        (
            "Syntax:\n"
            "`visual <class/hero>`: Shows first Hero generation Visual Splashart.\n"
            "\n"
            "*First Hero generation: Kasel, Frey, Cleo, Roi, Clause, Morrah, Maria, "
            "Selene, Lorraine*"
        ),
    ),
    "Costumes": (
        "Costumes command(s)",
        (
            "Syntax:\n"
            "`costume <class/hero>`\n"
            "`cos <class/hero>`\n"
            "`skin <class/hero>`\n"
            "Shows Hero's costume(s).\n"
            "\n"
            "Use the selection menu to choose a costume and the buttons to change "
            "pages.\n"
            "Menus can only be controlled by the person who opened them."
        ),
    ),
    "UW": (
        "UWs command(s)",
        "Syntax:\n`uw <class/hero/name>`\nShows Hero Unique Weapon.",
    ),
    "SW": (
        "SWs command(s)",
        (
            "Syntax:\n"
            "`sw <class/hero/name>`\n"
            "`us <class/hero/name>`\n"
            "Shows Hero Soul Weapon/Unique Skill."
        ),
    ),
    "UTs": (
        "UTs command(s)",
        (
            "Syntax:\n"
            "`ut <class/hero/name>`\n"
            "`ut<number> <class/hero/name>`\n"
            "`ut <number> <class/hero/name>`\n"
            "Shows Hero Unique Treasures."
        ),
    ),
    "UT1": (
        "UT1 command(s)",
        (
            "Syntax:\n"
            "`ut1 <class/hero>`\n"
            "`ut 1 <class/hero>`\n"
            "Shows Hero Unique Treasure 1."
        ),
    ),
    "UT2": (
        "UT2 command(s)",
        (
            "Syntax:\n"
            "`ut2 <class/hero>`\n"
            "`ut 2 <class/hero>`\n"
            "Shows Hero Unique Treasure 2."
        ),
    ),
    "UT3": (
        "UT3 command(s)",
        (
            "Syntax:\n"
            "`ut3 <class/hero>`\n"
            "`ut 3 <class/hero>`\n"
            "Shows Hero Unique Treasure 3."
        ),
    ),
    "UT4": (
        "UT4 command(s)",
        (
            "Syntax:\n"
            "`ut4 <class/hero>`\n"
            "`ut 4 <class/hero>`\n"
            "Shows Hero Unique Treasure 4."
        ),
    ),
    "Bosses": (
        "Boss command(s)",
        (
            "Syntax:\n"
            "`boss`, `boss list`, or `boss all`: Lists bosses.\n"
            "`boss <name/alias>`: Shows information using the shared info lookup (e.g. "
            "`boss wb1`).\n"
            "`info <name/alias>`: Shows Boss information.\n"
            "`skills <name/alias>`: Shows Boss skills.\n"
            "Use `--version <name>` or `-V <name>` with prefix commands or the slash "
            "`version` option to choose a dataset.\n"
            "\n"
            "Currently supported Boss content: Guild Raid / Guild Conquest / World "
            "Boss / Trial of God King / Shakmeh / Technomagic."
        ),
    ),
    "Artifacts": (
        "Artifact command(s)",
        (
            "Syntax:\n"
            "`atf <name>`\n"
            "`artifact <name>`\n"
            "Shows Artifact information.\n"
            "\n"
            "`atf search <number:default=10> <name>`\n"
            "`artifact search <number:default=10> <name>`\n"
            "Search Artifacts.\n"
            "\n"
            "`atf <all/list>`\n"
            "`artifact <all/list>`\n"
            "Shows all Artifacts."
        ),
    ),
    "Math": (
        "Math command(s)",
        "Syntax:\n`calc <operation>`\n`math <operation>`\nCalculates an Operation.",
    ),
    "Softcap": (
        "Softcap command(s)",
        (
            "Syntax:\n"
            "`softcap <value>`\n"
            "`soft <value>`\n"
            "`cap <value>`\n"
            "Shows a Softcap table.\n"
            "\n"
            "*Thanks to [Duckness](https://github.com/duckness) for this command.*"
        ),
    ),
}


class Info_Embed:
    def info_embed(self, cmd: str, client_name=None):
        if cmd in HELP_TOPICS:
            title, description = HELP_TOPICS[cmd]
            return discord.Embed(
                title=title, description=description, colour=settings.EMBED_COLOR
            )
        if cmd in ("Announcements", "Twitter", "Steam", "GitHub"):
            embed = discord.Embed(
                title=f"{cmd} commands",
                description=(
                    "Use your configured prefix or slash commands.\n"
                    "Manage Channels is required to turn subscriptions on or off.\n"
                    "The bot needs View Channel, Send Messages, and Embed Links."
                ),
                colour=settings.EMBED_COLOR,
            )
            if cmd in ("Announcements", "GitHub"):
                embed.add_field(
                    name="GitHub",
                    value="`github on/off/status/latest`: Follow the configured branch and receive main-branch PR deployment summaries. `latest` shows the latest development commit. The first check skips existing history.",
                    inline=False,
                )
            if cmd in ("Announcements", "Twitter"):
                embed.add_field(
                    name="Twitter / X",
                    value="`twitter on/off/status/latest`: Follow [@kingsraid_msg](https://x.com/kingsraid_msg) using the X API. Requires BEARER_TOKEN with user lookup and timeline access.",
                    inline=False,
                )
            if cmd in ("Announcements", "Steam"):
                embed.add_field(
                    name="Steam",
                    value="`steam on/off/status/latest`: Follow [KING's RAID RE:VERSE](https://store.steampowered.com/app/3689540/). No Steam key required.",
                    inline=False,
                )
            return embed
        raise ValueError(f"Unknown help topic: {cmd}")
