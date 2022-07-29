import discord, re, asyncio, json
from discord.ext import commands
from fuzzywuzzy import process

from discord_slash.utils.manage_components import create_actionrow, spread_to_rows, create_button, wait_for_component, create_select, create_select_option
from discord_slash.utils.manage_commands import create_option
from discord_slash.model import ButtonStyle
from discord_slash import cog_ext, SlashContext

from ..utils import paginator, check_permisison
from config import config

client = discord.Client()

class Guide(commands.Cog):
    def __init__(self, client):
        self.client = client
        self.menus = paginator.Paginator(self.client)
        self.check = check_permisison.view_channels

        self.hash = "#"
        self.left = "\u25c0"
        self.right = "\u25b6"
        self.guild_id = config.kre_guild_id
        self.categories = config.kre_categories
        self.invite = config.kre_invite
        self.taken = f'\n*Taken from [KR Encyclopedia]({self.kre_invite})*'
        with open('./data/emojis.json', 'r') as f:
            emojis = json.load(f)
        self.numbers = []
        for number in emojis['numbers_']:
            self.numbers.append(str(number))
        with open('./data/emojis.json') as f:
            self.hero_emojis = json.load(f)['heroes']

    @cog_ext.cog_subcommand(
                    base='guide',
                    name='content',
                    description='Give guide from KR Encyclopedia',
                    guild_ids=config.guild_ids,
                    options=[
                        create_option(
                            name='content',
                            description='Input a game content',
                            option_type=3,
                            required=True
                        )
                    ]) # guide command
    async def guide_content(self, ctx: SlashContext, *, content=None):
        if self.check(ctx.guild, ctx.channel) == True:
            await ctx.send("This command can't be used here...", hidden=True)
            return
        guild = self.client.get_guild(self.guild_id)
        contents, embeds, categories_ = self.get_contents(guild, self.categories)

        re_ = process.extractOne(content, contents)
        re_c = process.extractOne(content, categories_)
        if re_[1] >= re_c[1]:
            if re_[1] >= 70:
                channel = discord.utils.get(guild.channels, name=re_[0])
                try:
                    hero = ((channel.name).replace('-', ' ')).title()
                    splited = re.split('(\d+)', self.hero_emojis[hero])
                    thumbnail = self.client.get_emoji(int(splited[1])).url
                except:
                    thumbnail = None
                embeds = await self.get_embed(channel, thumbnail)
                await self.menus.paginator(context=ctx, embeds=embeds)
            else:
                await ctx.send(f"I can't find `{content}` or `{content}` is currently not available.", hidden=True)
        else:
            await self.preview_embed(ctx, guild, re_c[0])

    @cog_ext.cog_subcommand(
                    base='guide',
                    name='list',
                    description='Give a list of guide from KR Encyclopedia',
                    guild_ids=config.guild_ids) # list guides slash command
    async def guide_list(self, ctx):
        if self.check(ctx.guild, ctx.channel) == True:
            await ctx.send("This command can't be used here...", hidden=True)
            return
        guild = self.client.get_guild(self.guild_id)
        contents, embeds, categories_ = self.get_contents(guild, self.categories)

        msg = await self.pag(ctx, embeds)


    @cog_ext.cog_subcommand(
                    base='guide',
                    name='search',
                    description='Search guide from KR Encyclopedia',
                    guild_ids=config.guild_ids,
                    options=[
                        create_option(
                            name='content',
                            description='Input a game content',
                            option_type=3,
                            required=True
                        )
                    ]) # search guide slash command
    async def guide_search(self, ctx, *, content=None):
        if self.check(ctx.guild, ctx.channel) == True:
            await ctx.send("This command can't be used here...", hidden=True)
            return
        guild = self.client.get_guild(self.guild_id)
        contents, embeds, categories_ = self.get_contents(guild, self.categories)

        des = ''
        count = 0
        channels = process.extract(content, contents, limit=5)
        categories = process.extract(content, categories_, limit=5)
        for channel in channels:
            if channel[1] > 70:
                if count >= 5:
                    break
                channel = discord.utils.get(guild.channels, name=channel[0])
                des+=self.numbers[count]+f'. <#{channel.id}>\n'
                count+=1
        for category in categories:
            if category[1] > 70:
                if count >= 10:
                    break
                des+=self.numbers[count]+'. '+category[0]+f'\n'
                count+=1
        if des == '':
            des = f'No matched result for `{content}`.'
        embed = discord.Embed(
            title=f"Search result for: '{content}'",
            description=des+self.taken,
            color=discord.Colour.dark_purple()
        )
        if des == f'No matched result for `{content}`.':
            return
        range_ = len(des.splitlines())
        buttons = []
        for i in range(range_):
            buttons.append(create_button(style=ButtonStyle.blue, label=self.numbers[i]))
        button_row = create_actionrow(*buttons)
        msg = await ctx.send(embed=embed, components=[button_row])

        button_ctx: ComponentContext = await wait_for_component(self.client, components=[button_row], timeout=120.0, check=lambda x: x.author_id == ctx.author.id)
        if button_ctx.component['label'] in self.numbers:
            reacted = button_ctx.component['label']
            for line in des.splitlines():
                if line.startswith(reacted):
                    try:
                        channel_id = re.search(f"{'<#'}(.*?){'>'}", line).group(1)
                        channel = self.client.get_channel(int(channel_id))
                        try:
                            hero = ((channel.name).replace('-', ' ')).title()
                            splited = re.split('(\d+)', self.hero_emojis[hero])
                            thumbnail = self.client.get_emoji(int(splited[1])).url
                        except:
                            thumbnail = None
                        embeds = await self.get_embed(channel, thumbnail)
                        await self.menus.paginator(context=button_ctx, embeds=embeds)
                    except:
                        cate_ = line[3:]
                        await self.preview_embed(ctx, guild, cate_, msg)

    async def preview_embed(self, ctx, guild, input_, msg=None): # list guide
        count = 0
        des = ''
        category = discord.utils.get(guild.categories, name=input_)
        for channel in category.channels:
            if (guild.me.permissions_in(channel)).read_message_history == True:
                des+=f'- <#{channel.id}>\n'
                count+=1
        embed = discord.Embed(
            title=category.name,
            description=des+self.taken,
            color= discord.Colour.dark_purple()
        )
        await self.hash_(ctx, embed, msg)

    async def get_embed(self, channel, thumbnail=None): # get embed
        messages_ = await channel.history(limit=20, oldest_first=True).flatten()
        embeds = []
        count = 1
        messages = []
        title = ''
        for message in messages_:
            if message.attachments:
                messages.append(message.attachments[0].url)
            if len(message.content) >= 1900:
                for content in message.content.splitlines():
                    if content == '':
                        continue
                    elif content.startswith('*') or content.startswith('_') and content.endswith('*') or content.endswith('_'):
                        title += content + '\n\n'
                    else:
                        message_ = title + content
                        messages.append(message_)
                        title = ''
            else:
                if title != '':
                    messages.append(title+message.content)
                else:
                    messages.append(message.content)
                title = ''
        for message in messages:
            embed = discord.Embed(
                title=(channel.name+' guide').title(),
                description=message+f'\n{self.taken} *<#{channel.id}>*',
                color=discord.Colour.dark_purple()
            )
            if thumbnail is not None:
                embed.set_thumbnail(url=thumbnail)
            embed.set_footer(text=f'Page {count}/{len(messages)}')
            urls_start = ['https://cdn.discordapp.com/attachments/', 'https://media.discordapp.net/attachments/']
            for url_start in urls_start:
                if url_start in message:
                    pic = ['.png', '.jpg', '.jpeg']
                    for fm in pic:
                        if fm in message:
                            msgc = message
                            url = re.search(f"{url_start}(.*?){fm}", msgc).group(1)
                            embed.set_image(url=url_start+url+fm)
                            break
            if 'https://imgur.com/' in message:
                for line in (message).splitlines():
                    if 'https://imgur.com/' in line:
                        embed.set_image(url=line)
                        break
            embeds.append(embed)
            count+=1
        return embeds

    def get_contents(self, guild, categories): # get guide's content
        contents = [] # channels
        contents_ = [] # category: [channels]
        categories_ = []
        for category_ in categories:
            category = guild.get_channel(category_)
            categories_.append(category.name)
            format_ = {
                category.name: []
            }
            for channel in category.channels:
                if (guild.me.permissions_in(channel)).read_message_history == True: 
                    contents.append(channel.name)
                    format_[category.name].append(channel)
            contents_.append(format_)
        embeds = []
        count = 1
        for category in contents_:
            category_ = next(iter(category))
            des = ''
            for channel in category[category_]:
                des+=f'- <#{channel.id}>\n'
            embed = discord.Embed(
                title=category_,
                description=des+self.taken,
                colour=discord.Colour.dark_purple()
            )
            embed.set_footer(text=f'Page {count}/{len(contents_)}')
            embeds.append(embed)
            count+=1
        return contents, embeds, categories_

    async def pag(self, context, embeds, additional_buttons:list=None):
        index = 0
        buttons = [create_button(style=ButtonStyle.blue, label=self.left),
                create_button(style=ButtonStyle.red, label=self.hash),
                create_button(style=ButtonStyle.blue, label=self.right)]
        if additional_buttons is not None:
            for add_button in additional_buttons:
                buttons.append(add_button)
        if len(buttons) > 5:
            action_row = spread_to_rows(*buttons, max_in_row=5)
            await context.defer()
            msg = await context.send(embed=embeds[index], components=action_row)
        else:
            action_row = create_actionrow(*buttons)
            msg = await context.send(embed=embeds[index], components=[action_row])
        while True:
            try:
                button_ctx: ComponentContext = await wait_for_component(self.client, components=action_row, timeout=60.0, check=lambda x: x.author_id == context.author.id)
                if button_ctx.component['label'] == self.left:
                    index -= 1
                    if index < 0:
                        index = len(embeds) - 1
                elif button_ctx.component['label'] == self.right:
                    index += 1
                    if index == len(embeds):
                        index = 0
                elif button_ctx.component['label'] == self.hash:
                    await button_ctx.edit_origin(embed=embeds[index], components=[])
                    embed = embeds[index]
                    await self.hash_(context, embed, msg)
                    return
                await button_ctx.edit_origin(embed=embeds[index])
            except asyncio.TimeoutError:
                buttons = []
                for row in msg.components:
                    for button in row['components']:
                        button['disabled'] = True
                        buttons.append(button)
                if len(buttons) > 5:
                    action_row = spread_to_rows(*buttons, max_in_row=5)
                    await msg.edit(content='Timeout! Please try again.', components=action_row)
                else:
                    action_row = create_actionrow(*buttons)
                    await msg.edit(content='Timeout! Please try again.', components=[action_row])
                break

    async def hash_(self, ctx, embed_, msg=None): # hash emoji for break choosing loop
        des = ''
        count = 0
        contents = []

        for line in embed_.description.splitlines():
            if line.startswith('-'):
                channel = self.client.get_channel(int(line[4:][:-1]))
                contents.append((channel.name, str(channel.id)))
                try:
                    hero = ((channel.name).replace('-', ' ')).title()
                    des+= self.hero_emojis[hero]+' '+line[1:]+'\n'
                except:
                    des+= '- '+line[1:]+'\n'
                count+=1
        embed = discord.Embed(
            title=embed_.title,
            description=des+self.taken,
            color=discord.Colour.dark_purple()
        )

        def chunks(lst, n):
            for i in range(0, len(lst), n):
                yield lst[i:i + n]

        menus = []
        for content in contents:
            try:
                hero = (content[0].replace('-', ' ')).title()
                emoji = self.hero_emojis[hero]
                splited = re.split('(\d+)', emoji)
                emoji_ = self.client.get_emoji(int(splited[1]))
                menus.append(create_select_option(label=embed_.title, emoji=emoji_, description=hero, value=content[1]))
            except:
                menus.append(create_select_option(label=embed_.title, description=content[0], value=content[1]))
        menus_s = list(chunks(menus, 25))

        count = 1
        menus_rows = []
        for menus_ in menus_s:
            menus_rows.append(create_actionrow(create_select(menus_, placeholder=f'Choose your guide (Page {count}/{len(menus_s)})', max_values=1)))
            count+=1
        max_ = len(menus_rows)

        index = 0
        if max_ >= 2:
            buttons = [create_button(style=ButtonStyle.blue, label=self.left),
                    create_button(style=ButtonStyle.blue, label=self.right)]
            button_row = create_actionrow(*buttons)
            action_rows = [menus_rows[index], button_row]
        else:
            action_rows = [menus_rows[index]]

        try:
            await msg.edit(embed=embed, components=action_rows)
        except:
            msg = await ctx.send(embed=embed, components=action_rows)

        while True:
            try:
                interactions: ComponentContext = await wait_for_component(self.client, components=action_rows, timeout=120.0, check=lambda x: x.author_id == ctx.author.id)
                try:
                    selected_guide = interactions.selected_options[0]
                    channel = self.client.get_channel(int(selected_guide))
                    try:
                        hero = ((channel.name).replace('-', ' ')).title()
                        splited = re.split('(\d+)', self.hero_emojis[hero])
                        thumbnail = self.client.get_emoji(int(splited[1])).url
                    except:
                        thumbnail = None
                    embeds = await self.get_embed(channel, thumbnail)
                    await self.menus.paginator(context=interactions, embeds=embeds)
                except:
                    if interactions.component['label'] == self.left:
                        index -= 1
                        if index < 0:
                            index = max_ - 1
                    elif interactions.component['label'] == self.right:
                        index += 1
                        if index == max_:
                            index = 0
                    await interactions.edit_origin(embed=embed, components=[menus_rows[index], button_row])
            except asyncio.TimeoutError:
                await msg.edit(content='Timeout! Please try again.', components=None)
                break

def setup(client):
    client.add_cog(Guide(client))