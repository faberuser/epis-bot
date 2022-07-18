# this Chat module use API call to get response

import discord, asyncio, random, json, requests, traceback
from discord.ext import commands

from config import config

client = discord.Client()

class Chat(commands.Cog):

    def __init__(self, client):
        self.client = client
        self.client.add_listener(self.chat_, 'on_message')

    async def chat_(self, message):
        if message.author.id == self.client.user.id or message.content.startswith('/'):
            return
        content = message.content
        if '!' in content: # sometimes mentions have '!' syntax
            content = content.replace('!', '')
        clientuser = self.client.user.mention
        if clientuser in content or isinstance(message.channel, discord.channel.DMChannel):
            msg = None
            if isinstance(message.channel, discord.channel.DMChannel):
                msg = content
            elif content.startswith(clientuser): # bot is mentioned at first
                msg = content[21:]
            elif content.endswith(clientuser): # bot is mentioned at last
                msg = content[:-21]
            elif clientuser in content: # bot is mentioned in message
                msg = content.replace(str(clientuser), 'you')
            if '<@' in msg: # replace mentioned user to him or her (library can't response to ids)
                msg_ = msg.replace(msg[msg.find('<@')+len('<@'):msg.rfind('>')], '')
                msg = msg_.replace('<@>', random.choice(['him', 'her']))
            langs = ['vi', 'en', 'jp', 'tw']
            for lang in langs: # check registered language
                try:
                    with open(f'./data/chat/chat_{lang}', 'r') as f:
                        if lang == 'vi':
                            vi = f.read()
                        elif lang == 'jp':
                            jp = f.read()
                        elif lang == 'tw':
                            tw = f.read()
                        elif lang == 'en':
                            en = f.read()
                except FileNotFoundError:
                    open(f'./data/chat/chat_{lang}', 'a').close()
            async with message.channel.typing():
                def check(obj): # simsumi api
                    if obj in vi:
                        return requests.get(f'https://simsumi.herokuapp.com/api?text=[{msg}]&lang=vi', timeout=5.0)
                    elif obj in jp:
                        return requests.get(f'https://simsumi.herokuapp.com/api?text=[{msg}]&lang=jp', timeout=5.0)
                    elif obj in tw:
                        return requests.get(f'https://simsumi.herokuapp.com/api?text=[{msg}]&lang=tw', timeout=5.0)
                    elif obj in en:
                        return requests.get(f'https://simsumi.herokuapp.com/api?text=[{msg}]&lang=en', timeout=5.0)
                    else:
                        return None
                try:
                    api = check(str(message.channel.guild.id))
                    if api is not None:
                        api = api
                    else:
                        api = requests.get(f'http://epis-programy.herokuapp.com/context/{str(message.channel.id)}/question/[{msg}]', timeout=5.0) # base api
                except:
                    api = check(str(message.channel.id))
                    if api is not None:
                        api = api
                    else:
                        api = requests.get(f'https://simsumi.herokuapp.com/api?text=[{msg}]&lang=en', timeout=5.0) # simsumi api
                try:
                    if api.status_code == 200:
                        load = api.json()
                        response = load['success']
                    else:
                        response = None
                except:
                    response = api.content
                if response == '' or response is None:
                    response = '<:borryWeird:732920361179414578>' # got no response
                if 'Y-Bot' in response:
                    response = response.replace('Y-Bot', self.client.user.name+' Bot')
                if 'your site' in msg.lower() or 'your url' in msg.lower() or 'your website' in msg.lower():
                    response = 'https://top.gg/bot/623894263846928412'
                if response == 'No.':
                    response = random.choice(['No.', 'Yes.'])
                splited = response.split()
                response = ''
                for word in splited:
                    response+=word+' '
                await asyncio.sleep(random.choice([1, 2]))
                await message.reply(response)

    @commands.command()
    @commands.has_permissions(manage_channels=True)
    async def chat(self, ctx, lang:str=None):
        await self.chatto(ctx, lang)

    @commands.command(aliases=['dm_chat'])
    @commands.dm_only()
    async def chat_dm(self, ctx, lang:str=None):
        await self.chatto(ctx, lang, True)

    async def chatto(self, ctx, lang, channel=False):
        if lang is None:
            embed = discord.Embed(title='Chat Language Set (Require `Manage Channel`)',
                                description='Syntax:\n`chat <language>`\nSet chat language (Module: [simsumi](https://simsumi.herokuapp.com/#home)) currently support [`vi`, `jp`, `th`, `tw`, `en`]. If multi langauge has been set, will follow in order of the list.\nUse this command again to unset.',
                                colour=config.embed_color)
            await ctx.reply(embed=embed)
        else:
            langs = ['vi', 'en', 'jp', 'tw']
            if lang not in langs:
                await ctx.reply(f'`{lang}` not found or currently not supported.')
                return
            try:
                with open(f'./data/chat/chat_{lang}', 'r') as f:
                    re = f.read()
                if channel == True:
                    id_ = str(ctx.channel.id)
                else:
                    id_ = str(ctx.guild.id)
                if id_ not in re:
                    with open(f'./data/chat/chat_{lang}', 'w+') as f:
                        f.write(id_+'\n')
                        await ctx.reply(f'Succesfully set chat language to `{lang}` for `{id_}`.')
                elif id_ in re:
                    with open(f'./data/chat/chat_{lang}', 'w') as f:
                        f.write(re.replace(id_+'\n', ''))
                        await ctx.reply(f'Succesfully unset chat language to `{lang}` for `{id_}`.')
            except FileNotFoundError:
                with open(f'./data/chat/chat_{lang}', 'a') as f:
                    f.write(id_+'\n')
                    await ctx.reply(f'Succesfully set chat language to `{lang}` for `{id_}`.')
            except Exception as e:
                await ctx.reply(e)

def setup(client):
	client.add_cog(Chat(client))
