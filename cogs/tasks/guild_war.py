import discord, time, json, random, pytz, os, logging, psutil
from discord.ext import commands, tasks
from datetime import datetime

from ..utils import resource
from config import config

client = discord.Client()

class Guild_War(commands.Cog):

	def __init__(self, client):
		self.client = client
		self.announce.start()

	@commands.command(aliases=['gw']) # guild war notifer (kinda scuff)
	@commands.has_permissions(manage_channels=True)
	async def guild_war(self, ctx, arg: str=None, tz: str=None, time: int=None, *, message: str=None):
		if arg is None and tz is None and time is None:
			embed = discord.Embed(title='Guild War Announcement',
								description=(f'Syntax:\n`guild_war <on/off/show> <server> <time> <custom_message/leave_blank>`\n\n'+
									'- `<server>` - list of servers can be used: `Asia`, `Europe`, `Korea`, `America`, `Japan`, `Taiwan`, `HongKong`, `Macao`\n'+
									'- `<time>` - put an hour in 24h format: `0` - `23`, you can add more than 1 time to announce by using `guild_war_time <show/add/remove> time <24h_format>`\n'+
									'- `<custom_message>` - The default message is `Time to do Guild War!`, you can add or remove message to a list for random when the bot send message by using `guild_war_msg <show/add/remove> message <custom_message>`.\n\n'+
									'**Servers time zone**:\nAsia - UTC+7 (Asia/Ho_Chi_Minh)\nEurope - UTC+2 (Europe/Bucharest)\nKorea - UTC+9 (Asia/Seoul)\n'+
										'Ameria - UTC-4 (America/Anguilla)\nJapan - UTC+9 (Asia/Tokyo)\nTaiwan, HongKong, Macao - UTC+8 (Asia/Taipei)'),
								colour=config.embed_color)
			await ctx.reply(embed=embed)				
		else:
			if arg.lower() == 'show':
				try:
					embed = self.show(ctx.guild.channels)
					await ctx.reply(embed=embed)
				except:
					await ctx.reply("You hadn't registered any channel. <:broken:652813264778166278>")

			elif arg.lower() == 'on':
				if tz.lower().startswith('as'):
					sv = 'asia'
				elif tz.lower().startswith('e'):
					sv = 'europe'
				elif tz.lower().startswith('k'):
					sv = 'korea'
				elif tz.lower().startswith('am'):
					sv = 'america'
				elif tz.lower().startswith('j'):
					sv = 'japan'
				elif tz.lower().startswith('t') or tz.lower().startswith('h') or tz.lower().startswith('m'):
					sv = 'taiwan'
				else:
					await ctx.reply(f"Sorry, i can't find any {tz} server. <:broken:652813264778166278>")

				with open(f'./data/guild_war/channels/{sv}.json', 'r') as j:
					re = json.load(j)
				for chan in re:
					if int(chan) == ctx.channel.id:
						await ctx.reply("You had already registered this channel.")
						return
					else:
						pass

				if 23 >= time >= 0:
					with open(f'./data/guild_war/time/{ctx.channel.id}', 'a') as f:
						f.write(str(time)+'\n')
				else:
					await ctx.reply('Wrong time format, please try again using time in range `0` - `23`. <:broken:652813264778166278>')
					return

				with open(f'./data/guild_war/messages/{ctx.channel.id}', 'a') as r:
					r.write('Time to do Guild War!'+'\n')
					if message:
						r.write(message+'\n')

				re[str(ctx.channel.id)] = {"time": f"./data/guild_war/time/{ctx.channel.id}",
										"messages": f"./data/guild_war/messages/{ctx.channel.id}"}
				with open(f'./data/guild_war/channels/{sv}.json', 'w') as h:
					json.dump(re, h, indent=4)

				await ctx.reply('Guild War Announcement have been turned on for this channel.')

			elif arg.lower() == 'off':
				try:
					self.remove_channel(str(ctx.channel.id))
					await ctx.reply('Guild War Announcement have been turned off for this channel.')
				except:
					await ctx.reply('Channel not found. <:broken:652813264778166278>')
			else:
				pass
		
	@commands.command(aliases=['gwt', 'gw_time'])
	@commands.has_permissions(manage_channels=True)
	async def guild_war_time(self, ctx, arg: str=None, time: int=None):
		if arg is None and time is None:
			embed = discord.Embed(title="Guild War Time Add",
								description="Syntax:\n`/guild_war_time <show/add/remove> <24h_format>`",
								colour=config.embed_color)
			await ctx.reply(embed=embed)
		else:
			if arg.lower() == 'show':
				try:
					embed = self.show(ctx.guild.channels)
					await ctx.reply(embed=embed)
				except:
					await ctx.reply("You hadn't registered any channel. <:broken:652813264778166278>")

			elif arg.lower() == 'add':
				for file in os.listdir('./data/guild_war/time'):
					chan = []
					chan.append(file[:-4])
					if str(ctx.channel.id) in chan:
						with open(f'./data/guild_war/time/{file}', 'r') as y:
							re = y.read()
						if str(time) not in re:
							with open(f'./data/guild_war/time/{file}', 'a') as f:
								f.write(str(time)+'\n')
							await ctx.reply(f'Added `{time}`.')
						else:
							await ctx.reply(f'Seems like `{time}` is already in this channel.')
					else:
						await ctx.reply("Sorry, seems like this channel not exists in my list. <:broken:652813264778166278>")

			elif arg.lower() == 'remove':
				for file in os.listdir('./data/guild_war/time'):
					chan = []
					chan.append(file[:-4])
					if str(ctx.channel.id) in chan:
						with open(f'./data/guild_war/time/{file}', 'r') as r:
							lines = r.readlines()
						try:
							with open(f'./data/guild_war/time/{file}', 'w') as t:
								for line in lines:
									if line.strip("\n") != str(time):
										t.write(line)
							await ctx.reply(f'Removed `{time}`.')
						except:
							await ctx.reply(f"Seems like `{time}` is already in this channel.")
					else:
						await ctx.reply("Sorry, seems like this channel not exists in my list. <:broken:652813264778166278>")
			
			else:
				pass

	@commands.command(aliases=['gwm', 'gw_msg', 'guild_war_message', 'gw_message'])
	@commands.has_permissions(manage_channels=True)
	async def guild_war_msg(self, ctx, arg: str, *, msg: str=None):
		if arg is None and time is None:
			embed = discord.Embed(title="Guild War Message Add",
								description="Syntax:\n`/guild_war_message <show/add/remove> <custom_message>`",
								colour=config.embed_color)
			await ctx.reply(embed=embed)
		else:
			if arg.lower() == 'show':
				try:
					embed = self.show(ctx.guild.channels)
					await ctx.reply(embed=embed)
				except:
					await ctx.reply("You hadn't registered any channel. <:broken:652813264778166278>")

			elif arg.lower() == 'add':
				for file in os.listdir('./data/guild_war/messages'):
					chan = []
					chan.append(file[:-4])
					if str(ctx.channel.id) in chan:
						with open(f'./data/guild_war/messages/{file}', 'r') as y:
							re = y.read()
						if msg not in re:
							with open(f'./data/guild_war/messages/{file}', 'a') as f:
								f.write(str(msg)+'\n')
							await ctx.reply(f'Added `{msg}`.')
						else:
							await ctx.reply(f'Seems like `{msg}` is already in this channel.')
					else:
						await ctx.reply("Sorry, seems like this channel not exists in my list. <:broken:652813264778166278>")

			elif arg.lower() == 'remove':
				for file in os.listdir('./data/guild_war/messages'):
					chan = []
					chan.append(file[:-4])
					if str(ctx.channel.id) in chan:
						with open(f'./data/guild_war/messages/{file}', 'r') as r:
							lines = r.readlines()
						try:
							with open(f'./data/guild_war/messages/{file}', 'w') as t:
								for line in lines:
									if line.strip("\n") != msg:
										t.write(line)
							await ctx.reply(f'Removed `{msg}`.')
						except:
							await ctx.reply(f"Seems like `{msg}` is already in this channel.")
					else:
						await ctx.reply("Sorry, seems like this channel not exists in my list. <:broken:652813264778166278>")
			
			else:
				pass

	def all_chan(self):
		asia = []
		europe = []
		korea = []
		america = []
		japan = []
		taiwan = []
		with open(f'./data/guild_war/channels/asia.json') as a:
			rea = json.load(a)
			for chan in rea:
				asia.append(chan)
		with open(f'./data/guild_war/channels/europe.json') as e:
			ree = json.load(e)
			for chan in ree:
				europe.append(chan)
		with open(f'./data/guild_war/channels/korea.json') as k:
			rek = json.load(k)
			for chan in rek:
				korea.append(chan)
		with open(f'./data/guild_war/channels/america.json') as am:
			ream = json.load(am)
			for chan in ream:
				america.append(chan)
		with open(f'./data/guild_war/channels/japan.json') as j:
			rej = json.load(j)
			for chan in rej:
				japan.append(chan)
		with open(f'./data/guild_war/channels/taiwan.json') as t:
			ret = json.load(t)
			for chan in ret:
				taiwan.append(chan)
		return asia, europe, korea, america, japan, taiwan

	def show(self, channels):
		asia, europe, korea, america, japan, taiwan = self.all_chan()
		for channel in channels:
			if str(channel.id) in asia:
				with open(f'./data/guild_war/channels/asia.json', 'r') as a_:
					asia_ = json.load(a_)
				time = asia_[str(channel.id)]['time']
				messages = asia_[str(channel.id)]['messages']
				chan = self.client.get_channel(int(channel.id))
			elif str(channel.id) in europe:
				with open(f'./data/guild_war/channels/europe.json', 'r') as e_:
					europe_ = json.load(e_)
				time = europe_[str(channel.id)]['time']
				messages = europe_[str(channel.id)]['messages']
				chan = self.client.get_channel(int(channel.id))
			elif str(channel.id) in korea:
				with open(f'./data/guild_war/channels/korea.json', 'r') as k_:
					korea_ = json.load(k_)
				time = korea_[str(channel.id)]['time']
				messages = korea_[str(channel.id)]['messages']
				chan = self.client.get_channel(int(channel.id))
			elif str(channel.id) in america:
				with open(f'./data/guild_war/channels/ameria.json', 'r') as am_:
					america_ = json.load(am_)
				time = america_[str(channel.id)]['time']
				messages = america_[str(channel.id)]['messages']
				chan = self.client.get_channel(int(channel.id))
			elif str(channel.id) in japan:
				with open(f'./data/guild_war/channels/japan.json', 'r') as j_:
					japan_ = json.load(j_)
				time = japan_[str(channel.id)]['time']
				messages = japan_[str(channel.id)]['messages']
				chan = self.client.get_channel(int(channel.id))
			elif str(channel.id) in taiwan:
				with open(f'./data/guild_war/channels/taiwan.json', 'r') as t_:
					taiwan_ = json.load(t_)
				time = taiwan_[str(channel.id)]['time']
				messages = taiwan_[str(channel.id)]['messages']
				chan = self.client.get_channel(int(channel.id))
			else:
				pass
		with open(f'{time}') as m:
			time_ = m.read()
		with open(f'{messages}') as n:
			messages_ = n.read()
		t = time_.replace('\n', ', ')
		m = messages_.replace('\n', ', ')
		embed = discord.Embed(title=f'{chan.name}', description=f"Time: {t[:-1]}\nMessages: {m[:-1]}", colour=config.embed_color)
		return embed

	@tasks.loop(minutes=1, reconnect=True)
	async def announce(self):
		with open('./data/guild_war/status', 'r') as f:
			re = f.read()
		if re == 'on':
			pass
		else:
			return
		resource.states_('Guild War attack')

		asia = datetime.now(pytz.timezone('Asia/Ho_Chi_Minh'))
		europe = datetime.now(pytz.timezone('Europe/Bucharest'))
		korea = datetime.now(pytz.timezone('Asia/Seoul'))
		america = datetime.now(pytz.timezone('America/Anguilla'))
		japan = datetime.now(pytz.timezone('Asia/Tokyo'))
		taiwan = datetime.now(pytz.timezone('Asia/Taipei'))

		day_asia = asia.today().weekday()
		day_europe = europe.today().weekday()
		day_korea = korea.today().weekday()
		day_america = america.today().weekday()
		day_japan = japan.today().weekday()
		day_taiwan = taiwan.today().weekday()

		if day_asia == int(0) or day_asia == int(3) or day_asia == int(4) or day_asia == int(6):
			await self.send('asia', day_asia, asia.hour, asia.minute)
		if day_europe == int(0) or day_europe == int(3) or day_europe == int(4) or day_europe == int(6):
			await self.send('europe', day_europe, europe.hour, europe.minute)
		if day_korea == int(0) or day_korea == int(3) or day_korea == int(4) or day_korea == int(6):
			await self.send('korea', day_korea, korea.hour, korea.minute)
		if day_america == int(0) or day_america == int(3) or day_america == int(4) or day_america == int(6):
			await self.send('america', day_america, america.hour, america.minute)
		if day_japan == int(0) or day_japan == int(3) or day_japan == int(4) or day_japan == int(6):
			await self.send('japan', day_japan, japan.hour, japan.minute)
		if day_taiwan == int(0) or day_taiwan == int(3) or day_taiwan == int(4) or day_taiwan == int(6):
			await self.send('taiwan', day_taiwan, taiwan.hour, taiwan.minute)

	async def send(self, sv: str, day: int, hour: int, minute: int):
		with open(f'./data/guild_war/channels/{sv}.json') as a:
			re = json.load(a)
			for channel in re:
				time = re[str(channel)]['time']
				msg = re[str(channel)]['messages']
				with open(time, 'r') as f:
					time = f.readlines()
					for time_ in time:
						if hour == int(time_) and minute == int(0):
							_time_ = time_.replace('\n', '')
							attemp = f" | Guild War attemping to send to #{str(channel)} at {sv.capitalize()} server at {_time_}h"
							logging.info(attemp)
							print(attemp)
							chan = self.client.get_channel(int(channel))
							try:
								with open(msg, 'r') as r:
									custome_msg = r.readlines()
									await chan.send(random.choice(custome_msg))
									success = f" | Guild War successfully sent to #{chan.name} on {chan.guild.name}"
									logging.info(success)
									print(success)
									return
							except AttributeError:
								invalid = f" | Guild War channel {str(channel)} is invalid, removing"
								logging.warn(invalid)
								print(invalid)
								self.remove_channel(str(channel))
							except discord.errors.Forbidden as r:
								forbidden = f" | FORBIDDEN: {str(r)} | Channel: #{chan.name} on {chan.guild.name}"
								print(forbidden)
								logging.info(forbidden)
							except Exception as t:
								logging.warn(t)

	def remove_channel(self, chan: str):
		asia, europe, korea, america, japan, taiwan = self.all_chan()
		if chan in asia:
			sv = 'asia'
		elif chan in europe:
			sv = 'europe'
		elif chan in korea:
			sv = 'korea'
		elif chan in america:
			sv = 'america'
		elif chan in japan:
			sv = 'japan'
		elif chan in taiwan:
			sv = 'taiwan'
		with open(f'./data/guild_war/channels/{sv}.json', 'r') as k:
			re_ = json.load(k)
			re_.pop(chan)
		with open(f'./data/guild_war/channels/{sv}.json', 'w') as l:
			json.dump(re_, l, indent=4)
		os.remove(f'./data/guild_war/messages/{chan}')
		os.remove(f'./data/guild_war/time/{chan}')

	@announce.before_loop
	async def before_annoucne(self):
		await self.client.wait_until_ready()

def setup(client):
	client.add_cog(Guild_War(client))