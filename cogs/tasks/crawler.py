import requests, os, discord, logging, json, bs4, datetime, time, asyncio
from discord.ext import commands, tasks
from bs4 import BeautifulSoup

from ..utils import resource, info_embed
from config import config

client = discord.Client()

lg = [
    ['EN', 'https://kr-official.community/en-community/', './data/kr-official.community/en_ids', './data/plug/channels_en.json'],
    ['JP', 'https://kr-official.community/jpn-community/', './data/kr-official.community/jp_ids', './data/plug/channels_jp.json'],
    ['TW', 'https://kr-official.community/tw-community/', './data/kr-official.community/tw_ids', './data/plug/channels_tw.json'],
    # ['VN', 'https://kr-official.community/vn-community/', './data/kr-official.community/vn_ids', './data/plug/channels_vi.json'],
    # ['TH', 'https://kr-official.community/th-community/', './data/kr-official.community/th_ids', './data/plug/channels_th.json'],
]

def check_permisison(guild, channel):
    per = guild.me.permissions_in(channel)
    if per.send_messages == False or \
        per.embed_links == False or \
            per.attach_files == False:
        return "I don't have enough permissions in this channel. Please make sure that at least `Send Messages`, `Embed Links`, `Attach Files` in my role are enabled."
    else:
        return True

class EN(commands.Cog):

    def __init__(self, client):
        self.client = client
        self.channels = {}
        self.channel_path = lg[0][3]
        try:
            with open(self.channel_path) as f:
                self.channels = json.load(f)
        except FileNotFoundError:
            open(self.channel_path, "a").close()
            self.channels = {}
        except Exception as e:
            raise (e)

    @commands.group(aliases=['en_plug']) # english register
    async def en(self, ctx):
        if ctx.invoked_subcommand is None:
            embed = info_embed.Info_Embed().info_embed('EN')
            await ctx.reply(embed=embed)

    @en.command(name="on") # english register on
    @commands.has_permissions(manage_channels=True)
    async def en_on(self, ctx):
        check = check_permisison(ctx.guild, ctx.channel)
        if check is not True:
            await ctx.reply(check)
            return
        cid = str(ctx.channel.id)
        self.channels[cid] = True
        await ctx.reply(
            "King's Raid __EN__ Announcements have been turned on for this channel."
        )
        write_channels(self.channel_path, self.channels)

    @en.command(name="off") # english register off
    @commands.has_permissions(manage_channels=True)
    async def en_off(self, ctx):
        cid = str(ctx.channel.id)
        self.channels[cid] = False
        await ctx.reply(
            "King's Raid __EN__ Announcements have been turned off for this channel."
        )
        write_channels(self.channel_path, self.channels)

class JP(commands.Cog):

    def __init__(self, client):
        self.client = client
        self.channels = {}
        self.channel_path = lg[1][3]
        try:
            with open(self.channel_path) as f:
                self.channels = json.load(f)
        except FileNotFoundError:
            open(self.channel_path, "a").close()
            self.channels = {}
        except Exception as e:
            raise (e)

    @commands.group(aliases=['jp_plug']) # japanese register
    async def jp(self, ctx):
        if ctx.invoked_subcommand is None:
            embed = info_embed.Info_Embed().info_embed('JP')
            await ctx.reply(embed=embed)

    @jp.command(name="on") # japanese register on
    @commands.has_permissions(manage_channels=True)
    async def jp_on(self, ctx):
        check = check_permisison(ctx.guild, ctx.channel)
        if check is not True:
            await ctx.reply(check)
            return
        cid = str(ctx.channel.id)
        self.channels[cid] = True
        await ctx.reply(
            "King's Raid __JP__ Announcements have been turned on for this channel."
        )
        write_channels(self.channel_path, self.channels)

    @jp.command(name="off") # japanese register off
    @commands.has_permissions(manage_channels=True)
    async def jp_off(self, ctx):
        cid = str(ctx.channel.id)
        self.channels[cid] = False
        await ctx.reply(
            "King's Raid __JP__ Announcements have been turned off for this channel."
        )
        write_channels(self.channel_path, self.channels)

class TW(commands.Cog):

    def __init__(self, client):
        self.client = client
        self.channels = {}
        self.channel_path = lg[2][3]
        try:
            with open(self.channel_path) as f:
                self.channels = json.load(f)
        except FileNotFoundError:
            open(self.channel_path, "a").close()
            self.channels = {}
        except Exception as e:
            raise (e)

    @commands.group(aliases=['tw_plug']) # taiwan register
    async def tw(self, ctx):
        if ctx.invoked_subcommand is None:
            embed = info_embed.Info_Embed().info_embed('TW')
            await ctx.reply(embed=embed)

    @tw.command(name="on") # taiwan register on
    @commands.has_permissions(manage_channels=True)
    async def tw_on(self, ctx):
        check = check_permisison(ctx.guild, ctx.channel)
        if check is not True:
            await ctx.reply(check)
            return
        cid = str(ctx.channel.id)
        self.channels[cid] = True
        await ctx.reply(
            "King's Raid __TW__ Announcements have been turned on for this channel."
        )
        write_channels(self.channel_path, self.channels)

    @tw.command(name="off") # taiwan register off
    @commands.has_permissions(manage_channels=True)
    async def tw_off(self, ctx):
        cid = str(ctx.channel.id)
        self.channels[cid] = False
        await ctx.reply(
            "King's Raid __TW__ Announcements have been turned off for this channel."
        )
        write_channels(self.channel_path, self.channels)

class VI(commands.Cog): # (old)

    def __init__(self, client):
        self.client = client
        self.channels = {}
        self.channel_path = lg[3][3]
        try:
            with open(self.channel_path) as f:
                self.channels = json.load(f)
        except FileNotFoundError:
            open(self.channel_path, "a").close()
            self.channels = {}
        except Exception as e:
            raise (e)

    @commands.group(aliases=['vi_plug']) # vietnamese register
    async def vi(self, ctx):
        if ctx.invoked_subcommand is None:
            embed = info_embed.Info_Embed().info_embed('VI')
            await ctx.reply(embed=embed)

    @vi.command(name="on") # vietnamese register on
    @commands.has_permissions(manage_channels=True)
    async def vi_on(self, ctx):
        check = check_permisison(ctx.guild, ctx.channel)
        if check is not True:
            await ctx.reply(check)
            return
        cid = str(ctx.channel.id)
        self.channels[cid] = True
        await ctx.reply(
            "King's Raid __VI__ Announcements have been turned on for this channel."
        )
        write_channels(self.channel_path, self.channels)

    @vi.command(name="off") # vietnamese register off
    @commands.has_permissions(manage_channels=True)
    async def vi_off(self, ctx):
        cid = str(ctx.channel.id)
        self.channels[cid] = False
        await ctx.reply(
            "King's Raid __VI__ Announcements have been turned off for this channel."
        )
        write_channels(self.channel_path, self.channels)

class TH(commands.Cog): # (old)

    def __init__(self, client):
        self.client = client
        self.channels = {}
        self.channel_path = lg[4][3]
        try:
            with open(self.channel_path) as f:
                self.channels = json.load(f)
        except FileNotFoundError:
            open(self.channel_path, "a").close()
            self.channels = {}
        except Exception as e:
            raise (e)

    @commands.group(aliases=['th_plug']) # thailand register
    async def th(self, ctx):
        if ctx.invoked_subcommand is None:
            embed = info_embed.Info_Embed().info_embed('TH')
            await ctx.reply(embed=embed)

    @th.command(name="on") # thailand register on
    @commands.has_permissions(manage_channels=True)
    async def th_on(self, ctx):
        check = check_permisison(ctx.guild, ctx.channel)
        if check is not True:
            await ctx.reply(check)
            return
        cid = str(ctx.channel.id)
        self.channels[cid] = True
        await ctx.reply(
            "King's Raid __TH__ Announcements have been turned on for this channel."
        )
        write_channels(self.channel_path, self.channels)

    @th.command(name="off") # thailand register off
    @commands.has_permissions(manage_channels=True)
    async def th_off(self, ctx):
        cid = str(ctx.channel.id)
        self.channels[cid] = False
        await ctx.reply(
            "King's Raid __TH__ Announcements have been turned off for this channel."
        )
        write_channels(self.channel_path, self.channels)

class Crawler(commands.Cog):
    def __init__(self, client):
        self.client = client
        self.checker_.start()
        self.channels = {}

    @commands.command(aliases=['announcement', 'announce', 'plug']) # annoucement help comamnd
    async def announcements(self, ctx):
        embed = info_embed.Info_Embed().info_embed('Announcements')
        await ctx.reply(embed=embed)

    @tasks.loop(minutes=1, reconnect=True) # loop checking task
    async def checker_(self):
        await self.checker(lg)

    async def checker(self, lg):
        resource.states_('new posts...')
        for lg_ in lg:
            lang = lg_[0]
            url = lg_[1]
            ids_path = lg_[2]
            channel_path = lg_[3]
            try:
                with open(channel_path) as f:
                    self.channels = json.load(f)
            except FileNotFoundError:
                open(channel_path, "a").close()
                self.channels = {}
                print(f'No reregistered channel found, breaking the {lang} loop...')
                break
            except Exception as e:
                raise (e)
            try:
                html_doc = requests.get(url, timeout=10.0).text
            except Exception as e:
                logging.critical(e)
                return
            soup = BeautifulSoup(html_doc, 'html.parser')
            try:
                with open(ids_path, 'r') as r:
                    ids = r.read()
            except FileNotFoundError:
                open(ids_path, 'a').close()
                with open(ids_path, 'r') as r:
                    ids = r.read()

            if lang == 'EN': # english page crawl
                soup3 = soup.find_all('ul', {'class': 'wp-block-latest-posts__list has-dates has-author wp-block-latest-posts'})
                posts = BeautifulSoup(str(soup3), 'html.parser').find_all('li')
                for post_ in posts:
                    post = BeautifulSoup(str(post_), 'html.parser')
                    a = post.find('a')
                    url_ = a.get('href')
                    if url_ is not None:
                        if url_ not in ids:
                            msg = 'New ' + lang + ' post found: ' + url_
                            logging.info(msg)
                            print(msg)
                            with open(ids_path, 'a', encoding='utf-8') as f:
                                f.write(url_+'\n')
                            title = a.get_text()
                            author_name = post.find('div').get_text()[3:]
                            time_ = post.find('time').get('datetime').replace('T', ' ')
                            time = datetime.datetime.strptime(time_, '%Y-%m-%d %H:%M:%S%z')
                            try:
                                page = requests.get(url_, timeout=10.0).text
                                page_soup = BeautifulSoup(page, 'html.parser')
                                thumbnail = page_soup.find('img').get('src')
                            except Exception as e:
                                thumbnail = None
                                logging.critical(e)
                            if config.parallel_tasks == True:
                                asyncio.create_task(self.sender(lang, title, url_, thumbnail, time, author_name, channel_path, self.channels))
                            else:
                                await self.sender(lang, title, url_, thumbnail, time, author_name, channel_path)

            elif lang == 'TH' or lang == 'TW': # thailand and taiwan crawl
                re = soup.find_all('article')
                for article in re:
                    id_ = article.get('data-post-id')
                    if id_ is not None:
                        re_ = article.find_all('h2', {'class': 'entry-title'})
                        re__ = BeautifulSoup(str(re_), 'html.parser').find_all('a')[0]
                        url_ = re__.get('href')
                        if id_ not in ids:
                            msg = 'New ' + lang + ' post found: ' + url_
                            logging.info(msg)
                            print(msg)
                            with open(ids_path, 'a', encoding='utf-8') as f:
                                f.write(id_+'\n')
                                news = str(article)
                                title = re__.get_text()
                            author = BeautifulSoup(str(article.find_all('div', {'class': 'entry-meta'})), 'html.parser')
                            author_name = author.find_all('span')[0].get_text().strip()[3:]
                            time_ = article.find_all('time')[0].get('datetime').replace('T', ' ')
                            time = datetime.datetime.strptime(time_, '%Y-%m-%d %H:%M:%S%z')
                            try:
                                page = requests.get(url_, timeout=10.0).text
                                page_soup = BeautifulSoup(page, 'html.parser')
                                thumbnail = page_soup.find('img').get('src')
                            except Exception as e:
                                thumbnail = None
                                logging.critical(e)
                            if config.parallel_tasks == True:
                                asyncio.create_task(self.sender(lang, title, url_, thumbnail, time, author_name, channel_path, self.channels))
                            else:
                                await self.sender(lang, title, url_, thumbnail, time, author_name, channel_path)

            else: # japanese and vietnamese crawl (old)
                re = soup.find_all('ul', {'class': 'wp-block-latest-posts__list has-dates has-author wp-block-latest-posts'})
                soup2 = BeautifulSoup(str(re), 'html.parser')
                re_ = soup2.find_all('li')
                for li in re_:
                    soup3 = BeautifulSoup(str(li), 'html.parser')
                    re__ = soup3.find_all('a')
                    url_ = re__[0].get('href')
                    if url_ is not None:
                        if url_ not in ids:
                            msg = 'New ' + lang + ' post found: ' + url_
                            logging.info(msg)
                            print(msg)
                            with open(ids_path, 'a', encoding='utf-8') as f:
                                f.write(url_+'\n')
                                news = soup3
                            title = news.find_all('a')[0].get_text()
                            author_name = news.find_all('div', {'class': 'wp-block-latest-posts__post-author'})[0].get_text()[3:]
                            time_ = news.find_all('time', {'class': 'wp-block-latest-posts__post-date'})
                            time__ = time_[0].get('datetime').replace('T', ' ')
                            time = datetime.datetime.strptime(time__, '%Y-%m-%d %H:%M:%S%z')
                            thumbnail = None
                            if config.parallel_tasks == True:
                                asyncio.create_task(self.sender(lang, title, url_, thumbnail, time, author_name, channel_path, self.channels))
                            else:
                                await self.sender(lang, title, url_, thumbnail, time, author_name, channel_path)

    async def sender(self, lang, title, url_, thumbnail, time, author_name, channel_path, channels): # get embed and send to channels
        try:
            chan = self.client.get_channel(config.cache_channel)
            msg = await chan.send(url_)
            await asyncio.sleep(30)
            embed = (await chan.fetch_message(msg.id)).embeds[0]
            embed.colour = discord.Colour.from_rgb(24,8,84)
            embed.timestamp = time
            if thumbnail is not None:
                embed.set_image(url=thumbnail)
            else:
                try:
                    embed.set_image(url=embed.thumbnail.url)
                except:
                    pass
            embed.thumbnail.url = None
        except:
            embed = discord.Embed(title=title, url=url_, timestamp=time, colour=discord.Colour.from_rgb(24,8,84))
            embed.set_author(name=author_name)
            if thumbnail is not None:
                embed.set_thumbnail(url=thumbnail)
        for key in channels:
            if channels[key]:
                chan = self.client.get_channel(int(key))
                try:
                    if isinstance(chan, discord.abc.GuildChannel):
                        attemp = f" | {lang} attempting to send to channel #{key}"
                        logging.info(attemp)
                        print(attemp)
                        await chan.send(embed=embed)
                        success = f" | {lang} successfully sent to #{chan.name} on {chan.guild.name}"
                        logging.info(success)
                        print(success)
                    else:
                        invalid = f" | {lang} channel #{key} is invalid, removing"
                        logging.info(invalid)
                        print(invalid)
                        channels[key] = False
                        write_channels(channel_path, channels)
                except discord.errors.Forbidden as r:
                    forbidden = f" | FORBIDDEN: {str(r)} | Channel: #{chan.name} on {chan.guild.name}"
                    logging.warn(forbidden)
                    print(forbidden)
                except Exception as e:
                    logging.warn(e)
                    print(e)

    @checker_.before_loop
    async def before_checker(self):
        await self.client.wait_until_ready()


def write_channels(channel_path, channels):
    with open(channel_path, 'w', encoding='utf-8') as json_data:
        json_data.write(json.dumps(channels))

def setup(client):
    client.add_cog(EN(client))
    client.add_cog(JP(client))
    client.add_cog(TW(client))
    # client.add_cog(TH(client))
    # client.add_cog(VI(client))
    client.add_cog(Crawler(client))