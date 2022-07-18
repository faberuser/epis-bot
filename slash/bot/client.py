import discord, sys, aiohttp, asyncio
from discord.ext import commands
from datetime import datetime

from discord_slash.utils.manage_commands import create_option
from discord_slash.utils.manage_components import create_button, create_select_option, create_select, create_actionrow
from discord_slash.model import ButtonStyle
from discord_slash import cog_ext, SlashContext

from ..utils import paginator, check_permisison
from config import config

client = discord.Client()

class Info(commands.Cog):

    def __init__(self, client):
        self.client = client
        self.paginator = paginator.Paginator(self.client).paginator
        self.check = check_permisison.view_channels
        self.discord_bot_list = config.DBL_URL
        self.donate = config.donate
        self.vote_url = config.DBL_VOTE
        self.policy = config.POLICY
        with open('./data/time', 'r') as f:
            self.launch_time = datetime.strptime(f.read(), '%Y-%m-%d %H:%M:%S.%f')


    @cog_ext.cog_slash(name='help',
                    description='Give some help',
                    guild_ids=config.guild_ids) # slash help command
    async def help_(self, ctx: SlashContext):
        if self.check(ctx.guild, ctx.channel) == True:
            await ctx.send(content="This command can't be used here...", hidden=True)
            return
        moreinfo = ''
        if self.policy != '':
            moreinfo += f'See my [Policy]({self.policy})\n'
        if self.discord_bot_list != '':
            moreinfo += f'More at [Discord Bot List]({self.discord_bot_list})\n'
        if self.donate != '':
            moreinfo += f'Support me on [Donate]({self.donate})\n'
        embed1 = discord.Embed(
            title=f"__Commands start with {config.PREFIX}__",
            description=(moreinfo+
            "__**Hero**__\n"+
            "`hero` `infos` `skills` `books` `perks` `uw` `ut` `sw` `splashart` `visual` `costume` `story` `npc`\n"+
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

        buttons = []
        if self.discord_bot_list != '':
            button = create_button(style=ButtonStyle.URL, label='Discord Bot List', url=f'{self.discord_bot_list}')
            buttons.append(button)
        if self.donate != '':
            button = create_button(style=ButtonStyle.URL, label='Donate', url=f'{self.donate}')
            buttons.append(button)
        embeds = [embed1, embed2]
        if buttons != []:
            await self.paginator(ctx, embeds, buttons)
        else:
            await self.paginator(ctx, embeds)


    @cog_ext.cog_subcommand(
                    base='bot',
                    name='info',
                    description=f'Give a bit of infomations about the Bot',
                    guild_ids=config.guild_ids)
    async def bot_(self, ctx: SlashContext):
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
            useful_urls = useful_urls.replace('{self.invite_url}', f'{self.invite()}')
            useful_urls = useful_urls.replace('{self.discord_bot_list}', f'{self.discord_bot_list}')
        embed.add_field(
            name="<:grey_circle:652813264824041492> Useful URL",
            value=useful_urls
        )
        embed.set_author(name=self.client.user.name+" Bot", icon_url=self.client.user.avatar_url)
        embed.set_thumbnail(url=self.client.user.avatar_url)
        embed.set_footer(text=f"Any feedback or idea please DM me on Discord or use 'feedback'.")
 
        if self.check(ctx.guild, ctx.channel) == True:
            await ctx.send(embed=embed, hidden=True)
        else:
            await ctx.send(embed=embed)


    @cog_ext.cog_subcommand(
                    base='bot',
                    name='uptime',
                    description=f"Give the Bot's uptime",
                    guild_ids=config.guild_ids)
    async def uptime_(self, ctx: SlashContext):
        days, hours, minutes, seconds = self.time()
        embed = discord.Embed(
            title=f"Uptime: {days}d, {hours}h, {minutes}m, {seconds}s",
            colour=config.embed_color,
        )
        if self.check(ctx.guild, ctx.channel) == True:
            await ctx.send(embed=embed, hidden=True)
        else:
            await ctx.send(embed=embed)


    @cog_ext.cog_subcommand(
                    base='bot',
                    name='news',
                    description=f"Give the Bot's newest update",
                    guild_ids=config.guild_ids)
    async def update_(self, ctx: SlashContext):
        embed = discord.Embed(
            title="What's new",
            description=self.news(),
            colour=config.embed_color,
        )
        if self.check(ctx.guild, ctx.channel) == True:
            await ctx.send(embed=embed, hidden=True)
        else:
            await ctx.send(embed=embed)


    @cog_ext.cog_subcommand(
                    base='bot',
                    name='invite',
                    description=f'Invite the Bot',
                    guild_ids=config.guild_ids)
    async def invite_(self, ctx: SlashContext):
        embed = discord.Embed(
            title="Invite me!",
            url=self.invite(),
            colour=config.embed_color,
        )
        embed.set_thumbnail(url=self.client.user.avatar_url)
        if self.check(ctx.guild, ctx.channel) == True:
            await ctx.send(embed=embed, hidden=True)
        else:
            await ctx.send(embed=embed)


    @cog_ext.cog_subcommand(
                    base='bot',
                    name='ping',
                    description=f"Give the Bot's  current ping to Discord API",
                    guild_ids=config.guild_ids)
    async def ping_(self, ctx: SlashContext):
        embed = discord.Embed(
            title=f"Ping: {round(self.client.latency * 1000)}ms",
            colour=config.embed_color,
        )
        if self.check(ctx.guild, ctx.channel) == True:
            await ctx.send(embed=embed, hidden=True)
        else:
            await ctx.send(embed=embed)


    @cog_ext.cog_subcommand(
                    base='bot',
                    name='vote',
                    description=f"Vote for the Bot on Discord Bot List",
                    guild_ids=config.guild_ids)
    async def vote_(self, ctx: SlashContext):
        embed = discord.Embed(
            title=f"Vote for me on Discord Bot List!",
            url=self.vote_url,
            colour=config.embed_color,
        )
        embed.set_thumbnail(url=self.client.user.avatar_url)
        if self.check(ctx.guild, ctx.channel) == True:
            await ctx.send(embed=embed, hidden=True)
        else:
            await ctx.send(embed=embed)


    @cog_ext.cog_subcommand(
                    base='bot',
                    name='donate',
                    description=f"Donate the Bot's owner",
                    guild_ids=config.guild_ids)
    async def donate_(self, ctx: SlashContext):
        embed = discord.Embed(
            title=f"Support me!",
            url=self.donate,
            colour=config.embed_color,
        )
        embed.set_thumbnail(url=self.client.user.avatar_url)
        if self.check(ctx.guild, ctx.channel) == True:
            await ctx.send(embed=embed, hidden=True)
        else:
            await ctx.send(embed=embed)


    @cog_ext.cog_subcommand(
                    base='user',
                    name='info',
                    description=f"Give a bit of a member's infomations",
                    guild_ids=config.guild_ids,
                    options=[
                        create_option(name='member', description='Inpput a member', option_type=6, required=False)
                    ])
    async def userinfo_(self, ctx: SlashContext, *, member: discord.Member = None):
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
        if self.check(ctx.guild, ctx.channel) == True:
            await ctx.send(embed=embed, hidden=True)
        else:
            await ctx.send(embed=embed)


    @cog_ext.cog_subcommand(
                    base='user',
                    name='avatar',
                    description="Give a member's avatar",
                    guild_ids=config.guild_ids,
                    options=[
                        create_option(name='member', description='Inpput a member', option_type=6, required=False)
                    ])
    async def user_avatar(self, ctx: SlashContext, *, member: discord.Member = None):
        await self.avatar_s(ctx, member)

    @cog_ext.cog_slash(
                    name='avatar',
                    description="An aliase of user avatar",
                    guild_ids=config.guild_ids,
                    options=[
                        create_option(name='member', description='Inpput a member', option_type=6, required=False)
                    ])
    async def avatar_(self, ctx: SlashContext, *, member:discord.Member = None):
        await self.avatar_s(ctx, member)

    async def avatar_s(self, ctx, member):
        if member is not None:
            au = member
        if member is None:
            au = ctx.author
        url_ = au.avatar_url
        embed = discord.Embed(title=f"{au}", colour=config.embed_color)
        embed.set_image(url=url_)
        embed.set_footer(text=f"Requested by: {ctx.author}", icon_url=ctx.author.avatar_url)
        if self.check(ctx.guild, ctx.channel) == True:
            await ctx.send(embed=embed, hidden=True)
        else:
            await ctx.send(embed=embed)


    @cog_ext.cog_subcommand(
                    base='user',
                    name='banner',
                    description="Give a member's banner",
                    guild_ids=config.guild_ids,
                    options=[
                        create_option(name='member', description='Inpput a member', option_type=6, required=False)
                    ])
    async def user_banner(self, ctx: SlashContext, *, member: discord.Member = None):
        await self.banner_s(ctx, member)

    @cog_ext.cog_slash(
                    name='banner',
                    description=f"An aliase of user banner",
                    guild_ids=config.guild_ids,
                    options=[
                        create_option(name='member', description='Inpput a member', option_type=6, required=False)
                    ])
    async def banner_(self, ctx: SlashContext, *, member:discord.Member = None):
        await self.banner_s(ctx, member)

    async def banner_s(self, ctx, member=None):
        if member is not None:
            user_id = member.id
            au = member
        if member is None:
            user_id = ctx.author.id
            au = ctx.author

        resolution = 1024
        endpoints = (
            "https://cdn.discordapp.com/banners/",
            "https://discord.com/api/v9/users/{}".format(user_id)
        )

        headers = {
            "Authorization": f"Bot {config.DISCORD_TOKEN}"
        }

        embed = discord.Embed(title=f"{au}", colour=config.embed_color)
        embed.set_footer(text=f"Requested by: {ctx.author}", icon_url=ctx.author.avatar_url)

        async with aiohttp.ClientSession(headers=headers) as session:
            async with session.get(endpoints[1]) as response:
                data = await response.json()
                try:
                    url = endpoints[0] + str(user_id) + "/" + data["banner"] + "?size={0}".format(resolution)
                    embed.set_image(url=url)
                    if self.check(ctx.guild, ctx.channel) == True:
                        await ctx.send(embed=embed, hidden=True)
                    else:
                        await ctx.send(embed=embed)
                except:
                    await ctx.send('User has no banner', hidden=True)


    @cog_ext.cog_subcommand(
                    base='server',
                    name='info',
                    description=f"Give a bit this server's infomations",
                    guild_ids=config.guild_ids)
    async def serverinfo_(self, ctx: SlashContext):
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
        if self.check(ctx.guild, ctx.channel) == True:
            await ctx.send(embed=embed, hidden=True)
        else:
            await ctx.send(embed=embed)


    def invite(self):
        invite_ = discord.utils.oauth_url(self.client.user.id, discord.Permissions(permissions=322624))
        invite_url = invite_[:-19] + '%20applications.commands' + invite_[-19:]
        return invite_url


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
