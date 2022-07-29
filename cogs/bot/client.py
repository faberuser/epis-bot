import discord, sys, json, asyncio
from datetime import datetime
from discord.ext import commands

from ..utils import paginator, info_embed
from config import config

client = discord.Client()


class Info(commands.Cog):
    def __init__(self, client):
        self.client = client
        self.menus = paginator.Paginator(self.client)
        invite_ = discord.utils.oauth_url(self.client.user.id, discord.Permissions(permissions=322624))
        self.invite_url = invite_[:-19] + '%20applications.commands' + invite_[-19:]
        with open('./data/time', 'r') as f:
            self.launch_time = datetime.strptime(f.read(), '%Y-%m-%d %H:%M:%S.%f')
        self.info_embed_ = info_embed.Info_Embed()
        self.discord_bot_list = config.DBL_URL
        self.donate = config.donate
        self.vote_url = config.DBL_VOTE
        self.policy = config.POLICY


    @commands.command(aliases=["h", "command", "commands", "cmd"]) # help command
    async def help(self, ctx, morehelp=None):
        moreinfo = ''
        if self.policy != '':
            moreinfo += f'See my [Policy]({self.policy})\n'
        if self.discord_bot_list != '':
            moreinfo += f'More at [Discord Bot List]({self.discord_bot_list})\n'
        if self.donate != '':
            moreinfo += f'Support me on [Donate]({self.donate})\n'
        if morehelp is None:
            embed1 = discord.Embed(
                title=f"__Commands start with {config.PREFIX}__",
                description=(moreinfo+
                "__**Hero**__\n"+
                "`hero` `infos` `skills` `books` `perks` `uw` `ut` `sw` `splashart` `visual` `costume` `npc`\n"+
                "__**Artifact**__\n"+
                "`artifact` `atf` `arti`\n"+
                "__**Boss**__\n"+
                "`infos` `skills`\n"+
                "__**Announcements**__ (Require `Manage Channel`)\n"+
                "*The bot needs these permissions in Text Channel:* `Read Messages`, `Send Messages`, `Embed Links`, `Attach Files`, `Read Message History`\n*If the registered channel has unicode name (can't save with text file type (txt, log, etc)), announces may not be sent.*\n"+
                "`en <on/off>` `jp <on/off>` `tw <on/off>`\nSend new posts from [King's Raid Community](https://kr-official.community/) up to 5 languages.\n"+
                "`twitter <on/off>`: Send new tweets from [KING RAID OFFICIAL](https://twitter.com/Play_KINGsRAID).\n"+
                "`guild_war <on/off/show> <server> <24h_format> <custom_message/leave_blank>`: Guild War attack announcements."),
                colour=config.embed_color,
            )
            embed1.set_author(name=self.client.user.name+" Bot Help",
                            icon_url=self.client.user.avatar_url)
            embed1.set_footer(
                text="Page 1/2 | For more aliases/syntax type command only.")

            embed2 = discord.Embed(
                title=f"__Commands start with {config.PREFIX}__",
                description=(moreinfo+
                "__**Info**__\n"+
                "`userinfo` `avatar` `serverinfo` `invite` `vote` `bot` `news` `ping` `uptime` `donate` `feedback` `help`\n"+
                "__**Other**__\n"+
                "`calc <operation>`: Calculates something.\n`softcap <value>`: Shows a Softcap table.\n`tm <boss/gear> <hero_class/leave_blank>`: Shows 4 pieces of Technomagic Gear effect.\n"+
                "`guide <content>/list/'search <content>'`: Shows Guide(s) from [KR Encyclopedia](https://discord.gg/Y6fynAy).\n`fanart <waifu/husbando>`: Random King Raid fanart.\n"+
                "`sauce <url(image/message)/attachments>`: Find source of an image (Use command without arguments to find from a newest message has image in 50 newest messages).\n"+
                "`macro`: King Raid Emulator LoH Macro.\n`mail`: Vespa Mails.\n`timezone`: Shows servers time zone.\n`choose <first option | second option | ...>`: Random pick from the given list.\n"+
                f"`@{self.client.user.name} <message>`: Chat with {self.client.user.name} (works good with full sentence and no acronym or weird words)."),
                colour=config.embed_color,
            )
            embed2.set_author(name=self.client.user.name+" Bot Help",
                            icon_url=self.client.user.avatar_url)
            embed2.set_footer(
                text="Page 2/2 | For more aliases/syntax type command only.")

            embeds = [embed1, embed2]
            await self.menus.pag(message=ctx.message, embeds=embeds)

        elif morehelp is not None: # args after help command

            if morehelp.lower().startswith("anim"):
                embed = self.info_embed_.info_embed('Anime')
                await ctx.reply(embed=embed)

            elif morehelp.lower().startswith("boss") or morehelp.lower().startswith("gr") or morehelp.lower().startswith("gc") or morehelp.lower().startswith("wb") or morehelp.lower().startswith("trial") or "shak" in morehelp.lower():
                embed = self.info_embed_.info_embed('Bosses')
                await ctx.reply(embed=embed)

            elif (morehelp.lower().startswith("artifact")
                  or morehelp.lower().startswith("atf")
                  or morehelp.lower().startswith("arti")):
                embed = self.info_embed_.info_embed('Artifacts')
                await ctx.reply(embed=embed)

            elif morehelp.lower().startswith("fanart"):
                embed = self.info_embed_.info_embed('Fanart')
                await ctx.reply(embed=embed)

            elif morehelp.lower().startswith("math") or morehelp.lower().startswith("calc"):
                embed = self.info_embed_.info_embed('Math')
                await ctx.reply(embed=embed)

            elif morehelp.lower().startswith("soft") or morehelp.lower().startswith("cap"):
                embed = self.info_embed_.info_embed('Softcap')
                await ctx.reply(embed=embed)

            elif morehelp.lower().startswith("hero"):
                embed = self.info_embed_.info_embed('Heroes')
                await ctx.reply(embed=embed)

            elif morehelp.lower().startswith("book"):
                embed = self.info_embed_.info_embed('Books')
                await ctx.reply(embed=embed)

            elif morehelp.lower().startswith("cos") or morehelp.lower().startswith("skin"):
                embed = self.info_embed_.info_embed('Costumes')
                await ctx.reply(embed=embed)

            elif morehelp.lower().startswith("info"):
                embed = self.info_embed_.info_embed('Infos')
                await ctx.reply(embed=embed)

            elif morehelp.lower().startswith("perk"):
                embed = self.info_embed_.info_embed('Perks')
                await ctx.reply(embed=embed)

            elif morehelp.lower().startswith("skill"):
                embed = self.info_embed_.info_embed('Skills')
                await ctx.reply(embed=embed)

            elif morehelp.lower().startswith("splash"):
                embed = self.info_embed_.info_embed('Splashart')
                await ctx.reply(embed=embed)

            elif morehelp.lower().startswith("sw") or morehelp.lower().startswith("soul"):
                embed = self.info_embed_.info_embed('SW')
                await ctx.reply(embed=embed)

            elif morehelp.lower().startswith("ut") or morehelp.lower().startswith("treasure"):
                embed = self.info_embed_.info_embed('UTs')
                await ctx.reply(embed=embed)

            elif morehelp.lower().startswith("uw") or morehelp.lower().startswith("weapon"):
                embed = self.info_embed_.info_embed('UW')
                await ctx.reply(embed=embed)

            elif morehelp.lower().startswith("visual"):
                embed = self.info_embed_.info_embed('Visual')
                await ctx.reply(embed=embed)

            elif morehelp.lower().startswith("plug") or morehelp.lower().startswith("announce"):
                embed = self.info_embed_.info_embed('Announcements')
                await ctx.reply(embed=embed)

            elif morehelp.lower().startswith("en"):
                embed = self.info_embed_.info_embed('EN')
                await ctx.reply(embed=embed)

            elif morehelp.lower().startswith("jp"):
                embed = self.info_embed_.info_embed('JP')
                await ctx.reply(embed=embed)

            elif morehelp.lower().startswith("th"):
                embed = self.info_embed_.info_embed('TH')
                await ctx.reply(embed=embed)

            elif morehelp.lower().startswith("tw"):
                embed = self.info_embed_.info_embed('TW')
                await ctx.reply(embed=embed)

            elif morehelp.lower().startswith("vi"):
                embed = self.info_embed_.info_embed('VI')
                await ctx.reply(embed=embed)

            elif morehelp.lower().startswith("twitter"):
                embed = self.info_embed_.info_embed('Twitter')
                await ctx.reply(embed=embed)

            elif morehelp.lower().startswith("disable"):
                embed = self.info_embed_.info_embed('Disable', self.client.user.name)
                await ctx.reply(embed=embed)

            elif morehelp.lower().startswith("enable"):
                embed = self.info_embed_.info_embed('Enable', self.client.user.name)
                await ctx.reply(embed=embed)

            elif morehelp.lower().startswith("choose") or morehelp.lower().startswith("pick") or morehelp.lower().startswith("random"):
                embed = discord.Embed(
                    title='Choose Command',
                    description=f'Syntax:\n\
                    Single word: `choose <first_option second_option ...>`\n\
                    Multiple words:\n\
                    `choose <first option | second option | ...>`\n\
                    `choose <"first option" "second option" "...>`\n\
                    `choose <first option or second option or ...>`\n\
                    `choose <first option, second option, ...>`\n\
                    Random pick from the given list.',
                    colour=config.embed_color,
                )
                await ctx.reply(embed=embed)

            elif morehelp.lower().startswith("feedback") or morehelp.lower().startswith("report"):
                embed = self.info_embed_.info_embed('Feedback')
                await ctx.reply(embed=embed)

            elif morehelp.startswith(f"{self.client.user.mention}"):
                embed = discord.Embed(
                    title='Chat Module',
                    description=f'Syntax:\n`{self.client.user.mention} <message>`: Chat with Epis (works good with full sentence and no acronym or weird words).',
                    colour=config.embed_color,
                )
                await ctx.reply(embed=embed)

            else:
                await ctx.reply(
                    f":x: No help **{morehelp}** found. <:broken:652813264778166278>"
                )

    @commands.command(aliases=["bot", "client", "about"])
    async def in4(self, ctx): # bot info command
        days, hours, minutes, seconds = self.time()
        embed = discord.Embed(
            title=f"<:red_circle:652813264664657932> About {self.client.user.name} <:bot_tag:652813264497016834>",
            description=f"A Discord Bot for mobile game King Raid",
            colour=config.embed_color,
        )
        try:
            members = (await self.client.application_info()).team.members
            owner = ''
            for member in members:
                owner += ('*'+member.name+'#'+member.discriminator+'*'+'\n')
        except:
            owner = f"*{(await self.client.application_info()).owner}*"
        embed.add_field(name="<:green_circle:652813264841080862> Owned by",
                        value=owner)
        embed.add_field(name="<:py:652813265155653674> Python",
                        value=f"*{sys.version}*")
        embed.add_field(
            name="<:dpy:652813265910628372> discord.py",
            value=f"*{discord.__version__}*",
        )
        embed.add_field(
            name="<:yellow_circle:673961096008433674> Ping",
            value=f"*{round(self.client.latency * 1000)}ms*",
        )
        embed.add_field(name=":up: Uptime",
                        value=f"*{days}d, {hours}h, {minutes}m, {seconds}s*")
        embed.add_field(
            name="<:purple_circle:652813264992075776> Server count",
            value=f"*{len(self.client.guilds)}*",
        )
        embed.add_field(
            name="<:grey_circle:652813264824041492> What's new",
            value=f'{self.news()}'
        )
        with open('./data/useful_urls', 'r') as f:
            useful_urls = f.read()
            useful_urls = useful_urls.replace('{self.client.user.name}', f'{self.client.user.name}')
            useful_urls = useful_urls.replace('{self.invite_url}', f'{self.invite_url}')
            useful_urls = useful_urls.replace('{self.discord_bot_list}', f'{self.discord_bot_list}')
        embed.add_field(
            name="<:grey_circle:652813264824041492> Useful URL",
            value=useful_urls
        )
        embed.set_author(name=self.client.user.name+" Bot", icon_url=self.client.user.avatar_url)
        embed.set_thumbnail(url=self.client.user.avatar_url)
        embed.set_footer(text=f"Any feedback or idea please DM me on Discord or use 'feedback'.")
        await ctx.reply(embed=embed)

    @commands.command(aliases=["owner", "botowner"])
    @commands.is_owner()
    async def admin(self, ctx): # admin command
        embed = discord.Embed(
            title='Bot owner Commands',
            description=(f"List of commands:\n`fetch <command/extension/file>`: Fetch commands/extensions/files.\n`load <extension/file>`: Load a(n) extension/file.\n"+
                "`unload <extension/file>`: Unload a(n) extension/file.\n`reload <extension/file>`: Reload a(n) extension/file.\n`remove <command>`: Remove a command.\n"+
                "`reply <user_id/case> <send:True/False> <message>`: Reply to a feedback/report.\n`cases <all/not>`: Shows a table of all/not reply cases.\n"+
                "`news update <content>`: Update What's new board.\n"+
                "`slash-load <extension/file>`: Load a Slash extension/file.\n`slash-unload <extension/file>`: Unload a Slash extension/file.\n`slash-reload <extension/file>`: Reload a Slash extension/file."),
            colour=config.embed_color,
        )
        await ctx.reply(embed=embed)

    @commands.command()
    async def uptime(self, ctx): # uptime command
        days, hours, minutes, seconds = self.time()
        embed = discord.Embed(
            title=f"Uptime: {days}d, {hours}h, {minutes}m, {seconds}s",
            colour=config.embed_color,
        )
        await ctx.reply(embed=embed)

    @commands.command(aliases=['new', 'news']) # news command (can update with 'news update')
    async def update(self, ctx, update:str=None, *, text:str=None):
        embed = discord.Embed(
            title="What's new",
            description=self.news(),
            colour=config.embed_color,
        )
        await ctx.reply(embed=embed)
        if update == 'update' or update == 'updates':
            if await self.client.is_owner(ctx.author) == False:
                return
            with open('./data/news', 'w') as f:
                f.write(f'{text}\nLast update: {datetime.utcnow().strftime("%b %d %Y")}')

    @commands.command(aliases=["in", "inv"]) # invite command
    async def invite(self, ctx): 
        embed = discord.Embed(
            title="Invite me!",
            url=self.invite_url,
            colour=config.embed_color,
        )
        embed.set_thumbnail(url=self.client.user.avatar_url)
        await ctx.reply(embed=embed)

    @commands.command(aliases=["pong"]) # ping from server to API
    async def ping(self, ctx):
        embed = discord.Embed(
            title=f"Ping: {round(self.client.latency * 1000)}ms",
            colour=config.embed_color,
        )
        await ctx.reply(embed=embed)

    @commands.command() # vote command
    async def vote(self, ctx):
        embed = discord.Embed(
            title=f"Vote for me on Discord Bot List!",
            url=self.vote_url,
            colour=config.embed_color,
        )
        embed.set_thumbnail(url=self.client.user.avatar_url)
        await ctx.reply(embed=embed)

    @commands.command(aliases=['support', 'donator', 'supporter', 'donor']) # donate command
    async def donate(self, ctx):
        embed = discord.Embed(
            title=f"Support me!",
            url=self.donate,
            colour=config.embed_color,
        )
        embed.set_thumbnail(url=self.client.user.avatar_url)
        await ctx.reply(embed=embed)

    @commands.command(aliases=["ui", "user"], pass_context=True) # get userinfo from self or a server member
    async def userinfo(self, ctx, member: discord.Member = None):
        if member is not None:
            au = member
        if member is None:
            au = ctx.author
        roles = [role for role in au.roles]

        embed = discord.Embed(color=au.color)
        embed.set_author(name=f"{au}", icon_url=au.avatar_url)
        embed.set_image(url=au.avatar_url)
        embed.add_field(
            name="Joined at:",
            value=au.joined_at.strftime("%A, %d. %B %Y at %H:%M:%S"))
        embed.add_field(
            name="Created at:",
            value=au.created_at.strftime("%A, %d. %B %Y at %H:%M:%S"),
        )
        embed.add_field(
            name=f"Roles ({len(roles)-1}):",
            value=" ".join([role.mention for role in roles])[22:],
        )
        publicFlags = []
        if au.public_flags.hypesquad_balance:
            publicFlags.append("<:balance:806772217554665484> Hypesquad Balance")
        elif au.public_flags.hypesquad_bravery:
            publicFlags.append("<:bravery:806772217873956885> Hypesquad Bravery")
        elif au.public_flags.hypesquad_brilliance:
            publicFlags.append("<:brilliance:806772217928744960> Hypesquad Brilliance")
        if au.public_flags.staff:
            publicFlags.append("<:staff:806772218100580372> Discord Staff")
        if au.public_flags.partner:
            publicFlags.append("<:partner:806772218024820777> Discord Partner")
        if au.public_flags.hypesquad:
            publicFlags.append("<:hypesquad:806772218021019669> Hypesquad Events")
        if au.public_flags.bug_hunter:
            publicFlags.append("<:bughunter:806772217710379050> Bug Hunger")
        if au.public_flags.verified_bot:
            publicFlags.append("<:verifiedBot:806772744674869258> Verified Bot")
        if au.public_flags.verified_bot_developer:
            publicFlags.append("<:verifiedDev:806772217710379050> Verified Bot Developer")
        if publicFlags != []:
            embed.add_field(name="Badges", value="\n".join(publicFlags))
        embed.add_field(name="Top role:", value=au.top_role.mention)
        embed.add_field(name="Bot ?", value=au.bot)
        embed.set_footer(text=f"Requested by: {ctx.author}",
                         icon_url=ctx.author.avatar_url)
        await ctx.reply(embed=embed)

    @commands.command(aliases=["avt", "ava"], pass_context=True) # get avatar from self or a server member
    async def avatar(self, ctx, member:discord.Member = None):
        if member is not None:
            au = member
        if member is None:
            au = ctx.author
        url_ = au.avatar_url
        embed = discord.Embed(title=f"{au}", colour=config.embed_color)
        embed.set_image(url=url_)
        embed.set_footer(text=f"Requested by: {ctx.author}", icon_url=ctx.author.avatar_url)
        msg = await ctx.reply(embed=embed)

    @commands.command(aliases=["si", "server"], pass_context=True) # get server info
    async def serverinfo(self, ctx):
        roles = [role for role in ctx.guild.roles]
        role_length = len(roles)

        if role_length > 50:
            roles = roles[:50]
            roles.append(">>>> [50/%s]Roles" % len(roles))

        roles = ", ".join(role.mention for role in roles)
        textchannel = len(ctx.guild.text_channels)
        voicechannel = len(ctx.guild.voice_channels)
        boostguys = len(ctx.guild.premium_subscribers)
        regional = str(ctx.guild.region)

        embed = discord.Embed()
        embed.set_author(name=f"{ctx.guild.name}",
                         icon_url=ctx.guild.icon_url)
        embed.set_thumbnail(url=ctx.guild.icon_url)
        embed.set_image(url=ctx.guild.banner_url)
        embed.add_field(name="Member count:", value=ctx.guild.member_count)
        embed.add_field(name="Member boost:", value=boostguys)
        embed.add_field(name="Nitro Boost level", value=str(ctx.guild.premium_tier))
        embed.add_field(name="Text/Voice Channels:",
                        value=f"{textchannel}/{voicechannel}")
        embed.add_field(name="Do moderators require 2FA?", value="Yes" if ctx.guild.mfa_level == 1 else "No")
        embed.add_field(name="Owner:", value=ctx.guild.owner)
        embed.add_field(
            name="Created at:",
            value=ctx.guild.created_at.strftime("%A, %d. %B %Y at %H:%M:%S"),
        )
        embed.add_field(name="Region:", value=regional)
        embed.add_field(name="Roles:", value=roles[23:])
        await ctx.reply(embed=embed)

    @commands.command(aliases=['prefixes', 'change_prefix', 'change_prefixes']) # change prefix command
    @commands.has_permissions(manage_guild=True)
    async def prefix(self, ctx, prefix: str=None):
        if prefix is None:
            pref = ''
            remove_pref = ''
            for pre in config.PREFIX:
                pref += f'`{pre}`, '
                remove_pref += f'`prefix {pre}`, '
            pref = pref[:-2]
            remove_pref = remove_pref[:-2]
            embed = discord.Embed(title='Change Prefix Command (Require `Manage Server` permission)', 
                                description=(f"Syntax:\n`prefix <prefix>`\n\nEdit prefix for this server. Default prefixes is {pref}. "+
                                f"You can use {remove_pref} to remove {pref} prefixes. Also can add more by replace your prefix to `<prefix>`. "+
                                "Use this command with that prefix again to remove it. Use `prefix all` to show all prefixes of this server."),
                                colour=config.embed_color)
            await ctx.reply(embed=embed)
        elif prefix == 'all' or prefix == 'show': # show all prefixes in a server
            with open('./data/prefixes.json', 'r') as f:
                prefixes = json.load(f)
            try:
                guild_prefixes = prefixes[str(ctx.guild.id)]
            except:
                guild_prefixes = config.PREFIX
            desc = ''
            for pref in guild_prefixes:
                desc += f'`{pref}`, '
            desc = desc[:-2]
            embed = discord.Embed(title=f"{ctx.guild.name}'s Prefixes:",
                                description=desc)
            await ctx.reply(embed=embed)
        else: # change prefix for a server
            with open('./data/prefixes.json', 'r') as f:
                prefixes = json.load(f)
            try:
                if prefix not in prefixes[str(ctx.guild.id)]:
                    prefixes[str(ctx.guild.id)].append(prefix)
                    with open('./data/prefixes.json', 'w') as f:
                        json.dump(prefixes, f, indent=4)
                    await ctx.send(f'Added `{prefix}` prefix.')
                elif prefix in prefixes[str(ctx.guild.id)]:
                    if len(prefixes[str(ctx.guild.id)]) == 1:
                        await ctx.send(f'This is the last prefix for this server. Do you want to continue remove this ? (Y/N)')
                        def check(msg):
                            return msg.content and msg.author == ctx.author
                        try:
                            msg = await self.client.wait_for('message', check=check, timeout=30.0)
                            if msg.content.lower() == 'y' or msg.content.lower() == 'yes':
                                prefixes[str(ctx.guild.id)].remove(prefix)
                                with open('./data/prefixes.json', 'w') as f:
                                    json.dump(prefixes, f, indent=4)
                                await ctx.send(f'Removed `{prefix}` prefix. You can reset the prefix by kick the bot out and add it again.')
                            elif msg.content.lower() == 'n' or msg.content.lower() == 'no':
                                await ctx.send('Ok')
                            else:
                                await ctx.send('Invalid answer, please use the command to try again.')
                        except asyncio.TimeoutError:
                            await ctx.send('Timeout! Please use the command to try again.')
                    else:
                        prefixes[str(ctx.guild.id)].remove(prefix)
                        with open('./data/prefixes.json', 'w') as f:
                            json.dump(prefixes, f, indent=4)
                        await ctx.send(f'Removed `{prefix}` prefix.')
            except:
                self_prefixes = []
                for pre in config.PREFIX:
                    self_prefixes.append(pre)
                self_prefixes.append(prefix)
                prefixes[str(ctx.guild.id)] = self_prefixes
                with open('./data/prefixes.json', 'w') as f:
                    json.dump(prefixes, f, indent=4)
                await ctx.send(f'Added `{prefix}` prefix.')

    @commands.Cog.listener() # remove prefix if bot being kicked
    async def on_guild_remove(guild):
        with open('./data/prefixes.json', 'r') as f:
            prefixes = json.load(f)
        prefixes.pop(str(guild.id))
        with open('./data/prefixes.json', 'w') as f:
            json.dump(prefixes, f, indent=4)

    def time(self):
        delta_uptime = datetime.utcnow() - self.launch_time
        hours, remainder = divmod(int(delta_uptime.total_seconds()), 3600)
        minutes, seconds = divmod(remainder, 60)
        days, hours = divmod(hours, 24)
        return days, hours, minutes, seconds
    
    def news(self):
        try:
            with open('./data/news', 'r') as f:
                news = f.read()
            return news
        except FileNotFoundError:
            re = open('./data/news', 'a')
            news = re.read()
            re.close()
            return news

def setup(client):
    client.add_cog(Info(client))
