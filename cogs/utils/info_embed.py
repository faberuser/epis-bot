import discord
from config import config

class Info_Embed:

    def info_embed(self, cmd:str, client_name=None): # get help embed
        if cmd == 'Heroes':
            embed = discord.Embed(
                title=f"Hero command(s)",
                description=(f"Syntax:\n`hero list`: Shows King's Raid Heroes\n"+
                "`infos <class/hero>`: Shows Hero basic information.\n`skills <class/hero>`: Shows Hero skills.\n`books <class/hero>`: Shows Hero books.\n"+
                "`perks <class/hero>`: Shows Hero Perks/Transcend.\n`uw <class/hero/name>`: Shows Hero Unique Weapon.\n"+
                "`ut <class/hero/name>` | `ut<number> <class/hero/name>` | `ut <number> <class/hero/name>`: Shows Hero Unique Treasures.\n"+
                "`sw <class/hero/name>`: Shows Hero Soul Weapon/Unique Skill.\n`splashart <class/hero>`: Shows Hero Splashart/Loading Screen.\n"+
                "`visual <class/hero>`: Shows First Hero generation Visual Splashart.\n`costume <class/hero>`: Shows Hero costumes.\n`npc`: Shows NPC Heroes effect."),
                colour=config.embed_color,
            )
        elif cmd == 'Infos':
            embed = discord.Embed(
                title="Infos command(s)",
                description=f"Syntax:\n`infos <class/hero>`: Shows Hero Infos.\n`infos <number/name>`: Shows Boss information.",
                colour=config.embed_color,
            )
        elif cmd == 'Skills':
            embed = discord.Embed(
                title="Skills command(s)",
                description=f"Syntax:\n`skills <class/hero>`: Shows Hero skills.\n`skills <number/name>`: Shows Boss skills.",
                colour=config.embed_color,
            )
        elif cmd == 'Perks':
            embed = discord.Embed(
                title="Perks command(s)",
                description=f"Syntax:\n`perks <class/hero>`\n`trans <class/hero>`\nShows Hero Perks/Transcend.",
                colour=config.embed_color,
            )
        elif cmd == 'Books':
            embed = discord.Embed(
                title="Books command(s)",
                description=f"Syntax:\n`books <class/hero>`: Shows Hero Books.",
                colour=config.embed_color,
            )
        elif cmd == 'Splashart':
            embed = discord.Embed(
                title="Splashart command(s)",
                description=f"Syntax:\n`splashart <class/hero>`: Shows Hero Splashart/Loading Screen",
                colour=config.embed_color,
            )
        elif cmd == 'Visual':
            embed = discord.Embed(
                title="Visual command(s)",
                description=(f"Syntax:\n`visual <class/hero>`: Shows first Hero generation Visual Splashart.\n\n"+
                    "*First Hero generation: Kasel, Frey, Cleo, Roi, Clause, Morrah, Maria, Selene, Lorraine*"),
                colour=config.embed_color,
            )
        elif cmd == 'Costumes':
            embed = discord.Embed(
                title="Costumes command(s)",
                description=(f"Syntax:\n`costume <class/hero>`\n`cos <class/hero>`\n`skin <class/hero>`\nShows Hero's costume(s).\n\n"+
                    "Please wait till the bot reacts all of the emojis. Then you will have 30 secs to add reaction.\n"+
                    "If the image is not loaded properly, you can hit the reload emoji in 10 secs."),
                colour=config.embed_color,
            )
        elif cmd == 'UW':
            embed = discord.Embed(
                title="UWs command(s)",
                description=f"Syntax:\n`uw <class/hero/name>`\nShows Hero Unique Weapon.",
                colour=config.embed_color,
            )
        elif cmd == 'SW':
            embed = discord.Embed(
                title="SWs command(s)",
                description=f"Syntax:\n`sw <class/hero/name>`\n`us <class/hero/name>`\nShows Hero Soul Weapon/Unique Skill.",
                colour=config.embed_color,
            )
        elif cmd == 'UTs':
            embed = discord.Embed(
                title="UTs command(s)",
                description=f"Syntax:\n`ut <class/hero/name>`\n`ut<number> <class/hero/name>`\n`ut <number> <class/hero/name>`\nShows Hero Unique Treasures.",
                colour=config.embed_color,
            )
        elif cmd == 'UT1':
            embed = discord.Embed(
                title="UT1 command(s)",
                description=f"Syntax:\n`ut1 <class/hero>`\n`ut 1 <class/hero>`\nShows Hero Unique Treasure 1.",
                colour=config.embed_color,
            )
        elif cmd == 'UT2':
            embed = discord.Embed(
                title="UT2 command(s)",
                description=f"Syntax:\n`ut2 <class/hero>`\n`ut 2 <class/hero>`\nShows Hero Unique Treasure 2.",
                colour=config.embed_color,
            )
        elif cmd == 'UT3':
            embed = discord.Embed(
                title="UT3 command(s)",
                description=f"Syntax:\n`ut3 <class/hero>`\n`ut 3 <class/hero>`\nShows Hero Unique Treasure 3.",
                colour=config.embed_color,
            )
        elif cmd == 'UT4':
            embed = discord.Embed(
                title="UT4 command(s)",
                description=f"Syntax:\n`ut4 <class/hero>`\n`ut 4 <class/hero>`\nShows Hero Unique Treasure 4.",
                colour=config.embed_color,
            )
        elif cmd == 'Bosses':
            embed = discord.Embed(
                title="Boss command(s)",
                description=(f"Syntax:\n`infos <number/name>`: Shows Boss information.\n`skills <number/name>`: Shows Boss skills.\n"+
                    "Currently supported Boss content: Guild Raid / Guild Conquest / World Boss / Trial of God King / Shakmeh / Technomagic."),
                colour=config.embed_color,
            )
        elif cmd == 'Artifacts':
            embed = discord.Embed(
                title="Artifact command(s)",
                description=(f"Syntax:\n`atf <name>`\n`artifact <name>`\nShows Artifact information.\n"+
                    "\n`atf search <number:default=10> <name>`\n`artifact search <number:default=10> <name>`\nSearch Artifacts.\n"+
                    "\n`atf <all/list>`\n`artifact <all/list>`\nShows all Artifacts."),
                colour=config.embed_color,
            )
        elif cmd == 'Announcements':
            embed = discord.Embed(
                title="Announcements command(s)",
                description=("*The bot needs these permissions in Text Channel:* `Read Messages`, `Send Messages`, `Embed Links`, `Attach Files`, `Read Message History`\n"+
                    "*And you need this permission:* `Manage Channels`"),
                colour=config.embed_color,
            )
            embed.add_field(
                name="*KR __EN__ Announcements*",
                value=f"`en on` to turn KR __EN__ Announcements on this channel.\n`en off` to turn KR __EN__ Announcements off this channel.",
            )
            embed.add_field(
                name="*KR __JP__ Announcements*",
                value=f"`jp on` to turn KR __JP__ Announcements on this channel.\n`jp off` to turn KR __JP__ Announcements off this channel.",
            )
            embed.add_field(
                name="*KR __TH__ Announcements*",
                value=f"`th on` to turn KR __TH__ Announcements on this channel.\n`th off` to turn KR __TH__ Announcements off this channel.",
            )
            embed.add_field(
                name="*KR __TW__ Announcements*",
                value=f"`tw on` to turn KR __TW__ Announcements on this channel.\n`tw off` to turn KR __TW__ Announcements off this channel.",
            )
            embed.add_field(
                name="*KR __VI__ Announcements*",
                value=f"`vi on` to turn KR __VI__ Announcements on this channel.\n`vi off` to turn KR __VI__ Announcements off this channel.",
            )
            embed.set_footer(
                text="If the registered channel has unicode name (can't save with text file type (txt, log, etc)), announces may not be sent."
            )
        elif cmd == 'EN':
            embed = discord.Embed(
                title="__English__ Announcements (Require `Manage Channel`)",
                description=(f"*The bot needs these permissions in Text Channel:* `Read Messages`, `Send Messages`, `Embed Links`, `Attach Files`, `Read Message History`\n\n\
                    Syntax:\n`en <on/off>`: Send new posts from [King's Raid EN Community](https://kr-official.community/en-community/)."),
                colour=config.embed_color,
            )
        elif cmd == 'JP':
            embed = discord.Embed(
                title="__Japan__ Announcements (Require `Manage Channel`)",
                description=(f"*The bot needs these permissions in Text Channel:* `Read Messages`, `Send Messages`, `Embed Links`, `Attach Files`, `Read Message History`\n\n"+
                    "Syntax:\n`jp <on/off>`: Send new posts from [King's Raid 日本コミュニティ](https://kr-official.community/jpn-community/)."),
                colour=config.embed_color,
            )
        elif cmd == 'TW':
            embed = discord.Embed(
                title="__Taiwan__ King Raid Announcements (Require `Manage Channel`)",
                description=(f"*The bot needs these permissions in Text Channel:* `Read Messages`, `Send Messages`, `Embed Links`, `Attach Files`, `Read Message History`\n\n"+
                    "Syntax:\n`tw <on/off>`: Send new posts from [King's Raid 王之逆襲官方社群](https://kr-official.community/tw-community/)."),
                colour=config.embed_color,
            )
        elif cmd == 'KR':
            embed = discord.Embed(
                title="__Korean__ King Raid Announcements (Require `Manage Channel`)",
                description=(f"*The bot needs these permissions in Text Channel:* `Read Messages`, `Send Messages`, `Embed Links`, `Attach Files`, `Read Message History`\n\n"+
                    "Syntax:\n`kr <on/off>`: Send new posts from [킹스 레이드 공식 카페 : 네이버 카페](https://cafe.naver.com/kingsraid?iframe_url=/MyCafeIntro.nhn%3Fclubid=28873632)."),
                colour=config.embed_color,
            )
        elif cmd == 'VI':
            embed = discord.Embed(
                title="__Vietnam__ Announcements (Require `Manage Channel`)",
                description=(f"*The bot needs these permissions in Text Channel:* `Read Messages`, `Send Messages`, `Embed Links`, `Attach Files`, `Read Message History`\n\n"+
                    "Syntax:\n`vi <on/off>`: Send new posts from [King's Raid VN Community](https://kr-official.community/vn-community/)."),
                colour=config.embed_color,
            )
        elif cmd == 'TH':
            embed = discord.Embed(
                title="__Thailand__ Announcements (Require `Manage Channel`)",
                description=(f"*The bot needs these permissions in Text Channel:* `Read Messages`, `Send Messages`, `Embed Links`, `Attach Files`, `Read Message History`\n\n"+
                    "Syntax:\n`th <on/off>`: Send new posts from [King's Raid คอมมูนิตี้ไทย](https://kr-official.community/th-community/)."),
                colour=config.embed_color,
            )
        elif cmd == 'Twitter':
            embed = discord.Embed(
                title="King Raid Twitter (Require `Manage Channel`)",
                description=(f"*The bot needs these permissions in Text Channel:* `Read Messages`, `Send Messages`, `Embed Links`, `Attach Files`, `Read Message History`\n\n"+
                    "Syntax:\n`twitter <on/off>`: Send new tweets from [KING RAID OFFICIAL](https://twitter.com/Play_KINGsRAID)."),
                colour=config.embed_color,
            )
        elif cmd == 'Fanart':
            embed = discord.Embed(
                title="Fanart command(s)",
                description=f"Syntax:\n`fanart <hero/waifu/husbando>`: Shows a random King Raid fanart.",
                colour=config.embed_color,
            )
        elif cmd == 'Math':
            embed = discord.Embed(
                title="Math command(s)",
                description=f"Syntax:\n`calc <operation>`\n`math <operation>`\nCalculates an Operation.",
                colour=config.embed_color,
            )
        elif cmd == 'Softcap':
            embed = discord.Embed(
                title="Softcap command(s)",
                description=(f"Syntax:\n`softcap <value>`\n`soft <value>`\n`cap <value>`\nShows a Softcap table.\n\n"+
                    "*Thanks to [Duckness](https://github.com/duckness) for this command.*"),
                colour=config.embed_color,
            )
        elif cmd == 'Feedback':
            embed = discord.Embed(
                title='Feedback/Report command(s)',
                description=f'Syntax:\n`feedback <text>`\n`report <text>`\nFeedback or report somethings.',
                colour=config.embed_color,
            )
        return embed