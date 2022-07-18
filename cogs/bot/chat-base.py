# this Chat module use the local AIML engine called programy (program-y)

import discord, programy, asyncio, random, json
from discord.ext import commands
from programy.clients.embed.datafile import EmbeddedDataFileBot

from config import config

client = discord.Client()

class Chat(commands.Cog):

    def __init__(self, client):
        self.client = client
        file = {
            'aiml': ['./storage/categories'],
            'denormals': './storage/lookups/denormal.txt',
            'normals': './storage/lookups/normal.txt',
            'genders': './storage/lookups/gender.txt',
            'persons': './storage/lookups/person.txt',
            'person2s': './storage/lookups/person2.txt',
            'regexes': './storage/regex/regex-templates.txt',
            'dynamics': ['./storage/dynamics'],
            'conversations': ['./storage/conversations'],
            'properties': './config/properties.txt',
            }
        logging = './config/logging.yaml'
        self.aiml = EmbeddedDataFileBot(file, defaults=True, logging_filename=logging) # add files
        self.error_message = [ # error message when got no response
            'I have no idea what that means.',
            'What does that mean?',
            'Is that even English?',
            'Idk what that means, leave me alone.',
            'Speak clearly',
            'Idk what to tell you chief.',
            'I hate you sometimes.',
            'Why are you like this?',
            'Uhhh try again please.',
            'What do you mean?',
            ''
            ]
        self.client.add_listener(self.chat_, 'on_message')

    async def chat_(self, message):
        if message.author.id == self.client.user.id or message.content.startswith('/'):
            return
        try:
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
                def ask_question_(self, context, question):
                    client_context = self.create_client_context(context)
                    ques = self.process_question(client_context, question)
                    resp = self.renderer.render(client_context, ques)
                    return resp
                try:
                    self.aiml.ask_question = ask_question_.__get__(self.aiml, EmbeddedDataFileBot)
                    response = self.aiml.ask_question(str(message.channel.id), msg)
                except:
                    response = self.aiml.ask_question(msg)
                if response is None: # no response from library
                    if self.client.user.name.lower() in msg.lower():
                        response = '<:borryWeird:732920361179414578>'
                    else:
                        response = random.choice(self.error_message) + ' <:borryWeird:732920361179414578>'
                if 'Y-Bot' in response:
                    response = response.replace('Y-Bot', self.client.user.name+' Bot')
                if 'your site' in msg.lower() or 'your url' in msg.lower() or 'your website' in msg.lower():
                    response = 'https://top.gg/bot/623894263846928412'
                if response == 'No.':
                    response = random.choice(['No.', 'Yes.'])
                async with message.channel.typing():
                    splited = response.split()
                    response = ''
                    for word in splited:
                        response+=word+' '
                    await asyncio.sleep(random.choice([1, 2, 3]))
                    await message.reply(response)
        except Exception as e:
            await ctx.reply(e)

def setup(client):
	client.add_cog(Chat(client))
