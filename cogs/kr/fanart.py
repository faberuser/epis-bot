import discord, random, json, os, asyncio
from discord.ext import commands
from fuzzywuzzy import process

from PIL import Image
import imagehash, requests, io, pickle

from ..utils import dbl, info_embed
from config import config
from ..bot import sauce

client = discord.Client()

class Fanart(commands.Cog):
    def __init__(self, client):
        self.client = client
        self.vote = dbl.Vote(self.client)
        self.info_embed_ = info_embed.Info_Embed()
        self.file_type = ''
        #if config.windows == True:
            #self.file_type = '.txt'
        self.husbando = ['husbando', '_husbando']
        self.waifu = ['waifu', '_waifu']
        for file in os.listdir('./data/kr/table-data/heroes'):
            with open(f'./data/kr/table-data/heroes/{file}') as f:
                re = json.load(f)
            if re['infos']['gender'] == 'Female':
                self.waifu.append(file[:-5].lower().replace(' ', '-'))
            elif re['infos']['gender'] == 'Male':
                self.husbando.append(file[:-5].lower().replace(' ', '-'))
            else:
                if re['gender'] == "Female":
                    self.waifu.append(file[:-5].lower().replace(' ', '-'))
                elif re['gender'] == "Male":
                    self.husbando.append(file[:-5].lower().replace(' ', '-'))

    @commands.command(aliases=["fa"]) # fanart command
    @commands.cooldown(1, 5, commands.BucketType.user)
    async def fanart(self, ctx, *, input_:str=None):
        if input_ is None:
            embed = self.info_embed_.info_embed('Fanart')
            await ctx.reply(embed=embed)
        elif input_ is not None:
            check = await self.vote.vote(ctx)
            if check is False:
                return
            else:
                pass
            ls = []
            for hero in self.husbando:
                ls.append(hero)
            for hero in self.waifu:
                ls.append(hero)
            re = process.extractOne(input_.lower(), ls)
            if re[1] >= 50:
                embed = self.embed_(ctx, re[0])
                try:
                    msg = await ctx.reply(embed=embed)
                    await msg.add_reaction('🇸')
                    def check(reaction, user):
                        if msg.channel.type == discord.ChannelType.private:
                            return reaction.emoji in '🇸'
                        return user == ctx.author and str(reaction.emoji) in '🇸'
                    reaction, user = await self.client.wait_for(
                        "reaction_add", timeout=10.0, check=check
                        )
                    if str(reaction.emoji) in '🇸':
                        try:
                            await msg.clear_reactions()
                        except:
                            pass
                        search_embed = sauce.Sauce(self.client).searching_embed(embed)
                        await msg.edit(embed=search_embed)
                        sauce_embed = await sauce.Sauce(self.client).sauce_embed(search_embed)
                        await msg.edit(embed=sauce_embed)
                except asyncio.TimeoutError:
                    try:
                        await msg.clear_reactions()
                    except:
                        pass
                    timeout_embed = sauce.Sauce(self.client).timeout_embed(embed)
                    await msg.edit(embed=timeout_embed)
                except:
                    await ctx.reply(content=embed)
            else:
                await ctx.reply(f"Sorry, i can't find `{input_}`. <:broken:652813264778166278>")

    def embed_(self, ctx, input_: str): # process embed
        def get_color(cls_):
            if cls_ == 'wizard':
                clr = discord.Colour.from_rgb(123, 0, 0)
            elif cls_ == 'warrior':
                clr = discord.Colour.from_rgb(123, 60, 0)
            elif cls_ == 'knight':
                clr = discord.Colour.from_rgb(26, 63, 112)
            elif cls_ == 'assassin':
                clr = discord.Colour.from_rgb(118, 0, 102)
            elif cls_ == 'archer':
                clr = discord.Colour.from_rgb(51, 116, 0)
            elif cls_ == 'mechanic':
                clr = discord.Colour.from_rgb(0, 20, 122)
            elif cls_ == 'priest':
                clr = discord.Colour.from_rgb(0, 101, 115)
            else:
                clr = discord.Colour.darker_gray()
            return clr
        input__ = input_.replace('-', ' ')
        if input_ == 'waifu' or input_ == 'husbando':
            clr = config.embed_color
        else:
            with open(f'./data/kr/table-data/heroes/{input__.title()}.json') as f:
                re = json.load(f)
            cls_ = re['infos']['class']
            clr = get_color(cls_.lower())
        try:
            with open(f'./data/fanart/lists/{input_}{self.file_type}', 'r') as f:
                re = f.readlines()
                if re == []:
                    return f"Sorry, i can't find any `{input__.title()}`'s fanart in my data. <:broken:652813264778166278>"
                pic = str(random.choice(re))
                embed = discord.Embed(title=f"{input__.title()} Fanart", colour=clr)
                embed.set_image(url=pic)
                embed.set_footer(text=f"Total {input__.title()}'s fanarts data: {len(re)} | Click the emoji below to find source of this image")
                return embed
        except FileNotFoundError:
            open(f'./data/fanart/lists/{input_}{self.file_type}', 'a').close()
            return f"Sorry, i can't find any `{input__.title()}`'s fanart in my data. <:broken:652813264778166278>"


    @commands.Cog.listener() # add fanart from admin server
    async def on_message(self, msg):
        if msg.author.id == self.client.user.id:
            return
        try:
            if msg.guild.id == config.admin_guild:
                chan = msg.channel.name.lower()
                if chan in self.waifu: # auto add images from channel with waifu hero name
                    for hero in self.waifu:
                        if chan == hero:
                            asyncio.create_task(self.determine(hero, msg))
                if chan in self.husbando: # auto add images from channel with husbando hero name
                    for hero in self.husbando:
                        if chan == hero:
                            asyncio.create_task(self.determine(hero, msg))
                if chan.lower().startswith('fanart-check'):
                    asyncio.create_task(self.fanart_check(msg))
        except:
            pass

    async def determine(self, hero:str, msg):
        if msg.attachments:
            for img in msg.attachments:
                url = img.url
                await self.add_hero(url, hero, msg)
                await self.add_waifu_husbando(url, hero, msg)
        elif msg.content.startswith('http'):
            await self.add_hero(msg.content, hero, msg)
            await self.add_waifu_husbando(msg.content, hero, msg)

    def add(self, path, url, type_, adder, hash):
        with open(path, 'a') as f:
            f.write(url + '\n')
        with open('./data/fanart/data.json') as j:
            data = json.load(j)
        byte_files = []
        for file in os.listdir('./data/fanart/bytes'):
            byte_files.append(file)
        byte_files.sort()
        num = int(byte_files[-1])+1
        with open(f'./data/fanart/bytes/{num}', 'wb') as p:
            pickle.dump(hash, p)
        data[type_][url] = {'byte': f'./data/fanart/bytes/{num}', 'adder': adder}
        with open('./data/fanart/data.json', 'w') as j:
            json.dump(data, j, indent=4)

    def delete(self, path, url, type_):
        with open(path, 'r') as f:
            write_data = f.read().replace(url+'\n', '')
        with open(path, 'w+') as f:
            f.write(write_data)
        with open('./data/fanart/data.json') as j:
            data = json.load(j)
        byte_file = data[type_][url]['byte']
        del data[type_][url]
        with open('./data/fanart/data.json', 'w') as j:
            json.dump(data, j, indent=4)
        dup = False
        for hero in data:
            for url_ in data[hero]:
                if data[hero][url_]['byte'] == byte_file:
                    dup = True
        if dup == False:
            os.remove(byte_file)

    async def add_hero(self, url, hero, msg):
        path = f'./data/fanart/lists/{hero}{self.file_type}'
        await self.process(path, url, hero, msg, hero)

    async def add_waifu_husbando(self, url, hero, msg):
        if hero in self.waifu:
            path = f'./data/fanart/lists/waifu{self.file_type}'
            type_ = 'waifu'
        elif hero in self.husbando:
            path = f'./data/fanart/lists/husbando{self.file_type}'
            type_ = 'husbando'
        await self.process(path, url, hero, msg, type_)

    async def process(self, path, url, hero, msg, type_):
        if self.is_url_image(url) == True:
            await msg.reply('Processing in `'+type_+'` file')
        else:
            await msg.reply('Url is not an image')
            return

        try:
            original_img = Image.open(requests.get(url, stream=True).raw)
        except:
            try:
                dataBytesIO = io.BytesIO(requests.get(url).content)
                original_img = Image.open(dataBytesIO)
            except:
                await msg.reply('Failed to process, please try to convert image to `.png` using online converter.\nIf this error still occur, please contact the bot owner.')
                return
        original_hash = imagehash.average_hash(original_img)
        cutoff = 5
        similar = False
        open(path, 'a').close()
        with open(path, 'r+') as f:
            hero_w = f.readlines()
            for _url_ in hero_w:
                url_ = _url_[:-1]
                with open('./data/fanart/data.json') as j:
                    data = json.load(j)
                try:
                    data[type_]
                except KeyError:
                    data[type_] = {}
                    with open('./data/fanart/data.json', 'w') as j:
                        json.dump(data, j, indent=4)
                    break
                try:
                    with open(data[type_][url_]['byte'], 'rb') as p:
                        comparing_hash = pickle.load(p)
                except:
                    continue
                if original_hash - comparing_hash < cutoff:
                    similar = True
                    if type_ == 'husbando' or type_ == 'waifu':
                        await msg.reply('I found a similar image: '+
                        url_+' in `#'+type_+'`, do you want to add anyway or delete existing one? (Y/N/D)')
                    else:
                        await msg.reply('I found a similar image: '+
                        url_+' in <#'+str(msg.channel.id)+'>, do you want to add anyway or delete existing one? (Y/N/D)')
                    def check(m):
                        return m.author == msg.author
                    try:
                        msg_ = await self.client.wait_for('message', check=check, timeout=30.0)
                        if msg_.content.lower().startswith('y'):
                            self.add(path, url, type_, msg.author.id, original_hash)
                            await msg.reply('Added to `'+type_+'`')
                        elif msg_.content.lower().startswith('n'):
                            await msg.reply('Ok, no action was executed')
                        elif msg_.content.lower().startswith('d'):
                            self.delete(path, url_, type_)
                            await msg.reply('Deleted from `'+type_+'`')
                        else:
                            await msg.reply('Invalid answer, no action was executed')
                    except asyncio.TimeoutError:
                        await msg.reply('Timeout, no action was executed')
        if similar == False:
            self.add(path, url, type_, msg.author.id, original_hash)
            await msg.reply('Added to `'+type_+'`')

    async def fanart_check(self, msg):
        async def process(url):
            if self.is_url_image(url) == True:
                await msg.reply('Processing...')
            else:
                await msg.reply('Url is not an image')
                return

            try:
                original_img = Image.open(requests.get(url, stream=True).raw)
            except:
                try:
                    dataBytesIO = io.BytesIO(requests.get(url).content)
                    original_img = Image.open(dataBytesIO)
                except:
                    await msg.reply('Failed to process, please try to convert image to `.png` using online converter.\n\
                        If this error still occur, please contact the bot owner.')
                    return
            original_hash = imagehash.average_hash(original_img)
            cutoff = 5
            with open('./data/fanart/data.json') as j:
                data = json.load(j)
            similar = False
            for hero in data:
                print(hero)
                for url in data[hero]:
                    with open(data[hero][url]['byte'], 'rb') as p:
                        comparing_hash = pickle.load(p)
                        if original_hash - comparing_hash < cutoff:
                            similar = True
                            await msg.reply('I found similar image: '+url+' in `'+hero+'`')
            if similar == False:
                await msg.reply("I didn't find any similar image!")

        if msg.attachments:
            for img in msg.attachments:
                url = img.url
                await process(url)
        elif msg.content.startswith('http'):
            await process(msg.content)

    def is_url_image(self, url:str): # check if link is an image
        image_formats = ["image/png", "image/jpeg", "image/jpg", "image/gif"]
        r = requests.get(url, timeout=10.0)
        if r.headers["content-type"] in image_formats:
            return True
        return False


    #----------------------------------------------------------------------------
    # unused functions
    async def _add_(self, msg, hero: str):
        chan = msg.channel
    
        def hero_():
            f = open(f'./data/fanart/lists/{hero}{self.file_type}', 'r+')
            re = f.read()
            return f, re
        def waifu():
            r = open(f'./data/fanart/lists/waifu{self.file_type}', 'r+')
            waifu = r.read()
            return r, waifu
        def husbando():
            t = open(f'./data/fanart/lists/husbando{self.file_type}', 'r+')
            husbando = t.read()
            return t, husbando

        try:
            f, re = hero_()
        except FileNotFoundError:
            open(f'./data/fanart/lists/{hero}{self.file_type}', 'a').close()
            f, re = hero_()
        try:
            r, waifu = waifu()
        except FileNotFoundError:
            open(f'./data/fanart/lists/waifu{self.file_type}', 'a').close()
            r, waifu = waifu()
        try:
            t, husbando = husbando()
        except FileNotFoundError:
            open(f'./data/fanart/lists/husbando{self.file_type}', 'a').close()
            t, husbando = husbando()
        count = 0

        async def add(obj, url, type_, count=None):
            obj.write(url + '\n')
            if count is not None:
                await chan.send(f'Added {count} pic(s) to `{type_}`')
            else:
                await chan.send(f'Added to `{type_}`')

        async def delete(url, obj, list_, type_):
            await chan.send(f'{url} already in `{type_}`. Do you want to delete ? (Y/N)')
            def check(m):
                return m.author == msg.author
            msg_ = await self.client.wait_for('message', check=check, timeout=30.0)
            if msg_.content.lower() == 'yes' or msg_.content.lower() == 'y':
                obj.close()
                actual_list = list_.replace('\n', ' ').split()
                rep = None
                for url_ in actual_list:
                    if url_.split('/')[-1] == url.split('/')[-1]:
                        rep = list_.replace(url_+'\n', '')
                        break
                if rep is not None:
                    if type_ == 'hero':
                        with open(f'./data/fanart/lists/{hero}', 'w') as h:
                            h.write(rep)
                    if type_ == 'husbando':
                        with open(f'./data/fanart/lists/husbando{self.file_type}', 'w') as hus:
                            hus.write(rep)
                    if type_ == 'waifu':
                        with open(f'./data/fanart/lists/waifu{self.file_type}', 'w') as wai:
                            wai.write(rep)
                    await chan.send(f'Deleted from `{type_}`')
                else:
                    await chan.send(f"Failed to delete, can't find {url}")
            elif msg_.content.lower() == 'no' or msg_.content.lower() == 'n':
                await chan.send('Ok')
            else:
                await chan.send('Invalid answer')

        for hero_ in self.husbando:
            if hero == hero_:
                if msg.attachments:
                    attachments = msg.attachments
                    for img in attachments:
                        count += 1
                        pt = img.url
                        name = pt.split('/')[-1] + '\n'
                        if name not in re:
                            await add(f, pt, 'hero', count)
                        else:
                            await delete(pt, f, re, 'hero')
                        if name not in husbando:
                            await add(t, pt, 'husband', count)
                        else:
                            await delete(pt, t, husbando, 'husbando')
                elif msg.content.startswith('http'):
                    attachment = msg.content
                    name = attachment.split('/')[-1] + '\n'
                    if name not in re:
                        await add(f, attachment, 'hero')
                    if name in re:
                        await delete(attachment, f, re, 'hero')
                    if name not in husbando:
                        await add(t, attachment, 'husbando')
                    if name in husbando:
                        await delete(attachment, t, husbando, 'husbando')
                else:
                    pass

        for hero_ in self.waifu:
            if hero == hero_:
                if msg.attachments:
                    attachments = msg.attachments
                    for img in attachments:
                        count += 1
                        pt = img.url
                        name = pt.split('/')[-1] + '\n'
                        if name not in re:
                            await add(f, pt, 'hero', count)
                        else:
                            await delete(pt, f, re, 'hero')
                        if name not in waifu:
                            await add(r, pt, 'waifu', count)
                        else:
                            await delete(pt, r, waifu, 'waifu')
                elif msg.content.startswith('http'):
                    attachment = msg.content
                    name = attachment.split('/')[-1] + '\n'
                    if name not in re:
                        await add(f, attachment, 'hero')
                    if name in re:
                        await delete(attachment, f, re, 'hero')
                    if name not in waifu:
                        await add(r, attachment, 'waifu')
                    if name in waifu:
                        await delete(attachment, r, waifu, 'waifu')
                else:
                    pass

def setup(client):
    client.add_cog(Fanart(client))
