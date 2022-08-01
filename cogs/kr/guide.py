import discord, re, asyncio, json
from discord.ext import commands
from fuzzywuzzy import process

from ..utils import paginator
from config import config

client = discord.Client()

class Guide(commands.Cog):
    def __init__(self, client):
        self.client = client
        self.menus = paginator.Paginator(self.client)

        self.hash = "\u0023\u20e3"
        self.left = "\u25c0"
        self.right = "\u25b6"
        self.guild_id = config.kre_guild_id
        self.categories = config.kre_categories
        self.kre_invite = config.kre_invite
        self.taken = f'\n*Taken from [KR Encyclopedia]({self.kre_invite})*'
        with open('./data/emojis.json', 'r') as f:
            emojis = json.load(f)
        self.alphabets = []
        for alphabet in emojis['alphabets']:
            self.alphabets.append(emojis['alphabets'][alphabet])
        for number in emojis['numbers']:
            self.alphabets.append(emojis['numbers'][number])
        self.alphabets.append(self.left)
        self.alphabets.append(self.right)

    @commands.command() # guide command
    async def guide(self, ctx, *, content=None):
        guild = self.client.get_guild(self.guild_id)
        contents, embeds, categories_ = self.get_contents(guild, self.categories)

        if content is None:
            embed = discord.Embed(
                title="Guide command",
                description=(f"This command takes Guide(s) from [KR Encyclopedia]({self.kre_invite}).\n\n"+
                    "Syntax:\n`guide <content>`: Shows a Guide.\n"+
                    "`guide list`: Shows a list of available Guide(s).\n"+
                    "`guide search <content>`: Search a Guide.\n\n"+
                    "**Note:** If you are knowledgeable about the game or have strong writing skills, please consider visiting the server to help contribute towards a more comprehensive collection of King's Raid information.\n\n"+
                    f"*This command won't work if the bot isn't in the [KR Encyclopedia]({self.kre_invite}) server.*"),
                color=config.embed_color
            )
            await ctx.reply(embed=embed)

        elif content.lower() == 'list' or content.lower() == 'all': # list all guide
            msg = await self.pag(ctx, ctx.message, embeds)

        elif content.lower().startswith('search'): # search for guide
            content = content[7:]
            des = ''
            count = 0
            channels = process.extract(content, contents, limit=5)
            categories = process.extract(content, categories_, limit=5)
            for channel in channels:
                if channel[1] > 70:
                    if count >= 5:
                        break
                    channel = discord.utils.get(guild.channels, name=channel[0])
                    des+=self.alphabets[count]+f'. <#{channel.id}>\n'
                    count+=1
            for category in categories:
                if category[1] > 70:
                    if count >= 10:
                        break
                    des+=self.alphabets[count]+'. '+category[0]+f'\n'
                    count+=1
            if des == '':
                des = f'No matched result for `{content}`.'
            embed = discord.Embed(
                title=f"Search result for: '{content}'",
                description=des+self.taken,
                color=discord.Colour.dark_purple()
            )
            msg = await ctx.reply(embed=embed)
            if des == f'No matched result for `{content}`.':
                return
            range_ = len(des.splitlines())
            await self.add_react(ctx, range_, msg)
            re_ = await self.wait_for_react(ctx, msg)
            try:
                channel_id = re.search(f"{'<#'}(.*?){'>'}", re_).group(1)
            except:
                cate_ = re_[3:]
                embed, count = self.preview_embed(guild, cate_, False)
                await msg.clear_reactions()
                await msg.edit(content=None, embed=embed)
                if count >= 19:
                    re_ = await self.add_react(ctx, count, msg)
                else:
                    await self.add_react(ctx, count, msg)
                    re_ = await self.wait_for_react(ctx, msg)
                channel_id = re.search(f"{'<#'}(.*?){'>'}", re_).group(1)
            channel = self.client.get_channel(int(channel_id))
            embeds = await self.get_embed(channel)
            await msg.delete()
            await self.menus.pag(message=ctx.message, embeds=embeds)

        else: # get & send guide
            re_ = process.extractOne(content, contents)
            re_c = process.extractOne(content, categories_)
            if re_[1] >= re_c[1]:
                if re_[1] >= 70:
                    channel = discord.utils.get(guild.channels, name=re_[0])
                    embeds = await self.get_embed(channel)
                    await self.menus.pag(message=ctx.message, embeds=embeds)
                else:
                    await ctx.reply(f"I can't find `{content}` or `{content}` is currently not available.")
            else:
                embed, count = self.preview_embed(guild, re_c[0], True)
                msg = await ctx.reply(embed=embed)
                await self.hash_(msg, ctx, embed)

    def preview_embed(self, guild, input_, switch:bool): # list guide
        count = 0
        des = ''
        category = discord.utils.get(guild.categories, name=input_)
        for channel in category.channels:
            if (guild.me.permissions_in(channel)).read_message_history == True:
                if switch is True:
                    des+=f'- <#{channel.id}>\n'
                else:
                    des+=self.alphabets[count]+f'. <#{channel.id}>\n'
                count+=1
        embed = discord.Embed(
            title=category.name,
            description=des+self.taken,
            color= discord.Colour.dark_purple()
        )
        return embed, count

    async def get_embed(self, channel): # get embed
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

    async def pag(self, ctx, message, embeds): # paginator designed for guide command
        index = 0
        msg = None
        action = message.channel.send
        while True:
            res = await action(embed=embeds[index])
            if res is not None:
                msg = res
            l = index != 0
            r = index != len(embeds) - 1
            h = 99
            if l:
                await msg.add_reaction(self.left)
            if r:
                await msg.add_reaction(self.right)
            await msg.add_reaction(self.hash)
            try:
                react, user = await self.client.wait_for("reaction_add", check=self.predicate(msg, message, l, r, h), timeout=60.0)
            except asyncio.TimeoutError:
                await self.timeout(msg)
                break

            if str(react.emoji) in self.left:
                index -= 1
                try:
                    await msg.remove_reaction(self.left, message.author)
                except:
                    pass
            elif str(react.emoji) in self.right:
                index += 1
                try:
                    await msg.remove_reaction(self.right, message.author)
                except:
                    pass
            action = msg.edit
            if str(react.emoji) in self.hash:
                await msg.clear_reactions()
                try:
                    await self.hash_(msg, ctx)
                except asyncio.TimeoutError:
                    break

    async def hash_(self, msg, ctx, embed_i=None): # hash emoji for break choosing loop
        if embed_i is not None:
            embed_ = embed_i
        else:
            embed_ = msg.embeds[0]
        des = ''
        count = 0
        for line in embed_.description.splitlines():
            if line.startswith('-'):
                des+=self.alphabets[count]+'.'+line[1:]+'\n'
                count+=1
        embed = discord.Embed(
            title=msg.embeds[0].title,
            description=des+self.taken,
            color=discord.Colour.dark_purple()
        )
        await msg.edit(content=None, embed=embed)
        out_i = False
        for i in range(count):
            if i >= 19:
                out_i = True
                await msg.add_reaction(self.right)
                break
            await msg.add_reaction(self.alphabets[i])
        if out_i is True:
            re_ = await self.next_alphabets(msg, ctx, count)
            if re_ is True:
                await self.hash_(msg, ctx, embed_)
            else:
                pass
        if out_i is False:
            re_ = await self.wait_for_react(ctx, msg)
        channel_id = re.search(f"{'<#'}(.*?){'>'}", re_).group(1)
        channel = self.client.get_channel(int(channel_id))
        embeds = await self.get_embed(channel)
        await msg.delete()
        await self.menus.pag(message=ctx.message, embeds=embeds)

    def predicate(self, message, msg, l, r, h): # for paginator
        def check(reaction, user):
            if (
                reaction.message.id != message.id
                or user != msg.author
                or user == self.client.user
            ):
                return False
            if l and str(reaction.emoji) in self.left:
                return True
            if r and str(reaction.emoji) in self.right:
                return True
            if h and str(reaction.emoji) in self.hash:
                return True
            return False
        return check

    async def add_react(self, ctx, range_, msg): # add reactions
        out_i = False
        for i in range(range_):
            if i >= 19:
                out_i = True
                await msg.add_reaction(self.right)
                break
            await msg.add_reaction(self.alphabets[i])
        if out_i is True:
            re_ = await self.next_alphabets(msg, ctx, range_)
            if re_ == True:
                re_ = await self.add_react(ctx, range_, msg)
            return re_

    async def next_alphabets(self, msg, ctx, range_): # check for next page alphabets
        def check(reaction, user):
            return user == ctx.author and reaction.emoji in self.alphabets
        async def reaction_in_alphabets(msg):
            for alphabet in self.alphabets:
                if str(reaction.emoji) in alphabet:
                    re_ = self.get(alphabet, msg)
                    await msg.clear_reactions()
                    return re_
        try:
            reaction, user = await self.client.wait_for("reaction_add", timeout=30.0, check=check)
            if str(reaction.emoji) in self.right:
                await msg.clear_reactions()
            else:
                re_ = await reaction_in_alphabets(msg)
                return re_

            for i in range(19, range_):
                await msg.add_reaction(self.alphabets[i])
            await msg.add_reaction(self.left)

            reaction, user = await self.client.wait_for("reaction_add", timeout=30.0, check=check)
            if str(reaction.emoji) in self.left:
                await msg.clear_reactions()
                return True
            else:
                re_ = await reaction_in_alphabets(msg)
                return re_
        except asyncio.TimeoutError:
            await self.timeout(msg)

    async def wait_for_react(self, ctx, msg): # wait for reactions
        def check(reaction, user):
            return user == ctx.author and reaction.emoji in self.alphabets
        try:
            reaction, user = await self.client.wait_for("reaction_add", timeout=30.0, check=check)
            for alphabet in self.alphabets:
                if str(reaction.emoji) in alphabet:
                    re_ = self.get(alphabet, msg)
                    return re_
        except asyncio.TimeoutError:
            await self.timeout(msg)

    def get(self, num, msg):
        for item in msg.embeds[0].description.split("\n"):
            if num in item:
                re_ = item.strip()
                return re_
    
    async def timeout(self, msg):
        await msg.edit(content="Timeout! Please try again.")
        try:
            await msg.clear_reactions()
        except:
            pass

def setup(client):
    client.add_cog(Guide(client))