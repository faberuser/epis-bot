import discord, tweepy, asyncio, json, logging, psutil, aiohttp, traceback
from discord.ext import commands, tasks
from datetime import datetime

from ..utils import info_embed, resource
from config import config

check = None
auth = None
api = None
if config.BEARER_TOKEN == "" or config.CONSUMER_KEY == "" or config.CONSUMER_SECRET == "" or config.ACCESS_TOKEN == ""  or config.ACCESS_TOKEN_SECRET == "":
	check = False
	print('Twitter API Token(s) has been passed. Tweet-checking has been disabled.')
else:
	check = True
	bearer_token = config.BEARER_TOKEN
	consumer_key = config.CONSUMER_KEY
	consumer_secret = config.CONSUMER_SECRET
	access_token = config.ACCESS_TOKEN
	access_token_secret = config.ACCESS_TOKEN_SECRET

	# auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
	# auth.set_access_token(access_token, access_token_secret)
	# api = tweepy.API(auth)
	api = tweepy.Client(bearer_token, consumer_key, consumer_secret, access_token, access_token_secret)

client = discord.Client()


class Twitter(commands.Cog):

	def __init__(self, client):
		self.client = client
		self.api = api
		if check == True:
			self.twitter_.start()
		else:
			return
		self.twitter_.add_exception_type(aiohttp.ClientConnectionError)
		self.twitter_.add_exception_type(aiohttp.client_exceptions.ClientConnectionError)
		self.info_embed_ = info_embed.Info_Embed()
		self.channel_path = "./data/twitter/channels.json"

		try:
			with open(self.channel_path) as f:
				self.channels = json.load(f)
		except FileNotFoundError:
			open(self.channel_path, "a").close()
			self.channels = {}
		except Exception as e:
			raise (e)

	@tasks.loop(minutes=1, reconnect=True) # twitter task checking
	async def twitter_(self):
		resource.states_('Tweets')
		try:
			tweets = self.api.get_users_tweets(1248518690535923712, max_results=10, exclude='replies')
		except Exception as e:
			logging.warn(e)
			return
		try:
			with open('./data/twitter/tweets', 'r+') as f:
				tws = f.readlines()
				for tweet in tweets.data:
					if f'{tweet.id}\n' not in tws:
						f.write(str(tweet.id) + '\n')
						message = 'https://twitter.com/Play_KINGsRAID/status/' + str(tweet.id)
						msg = 'New tweet found: ' + message
						logging.info(msg)
						print(msg)
						try:
							tweet = self.api.get_tweet(tweet.id, tweet_fields=['created_at'], media_fields=['url'], expansions='attachments.media_keys')
							embed = discord.Embed(
								title='Tweet', url=message,
								description=tweet.data.text,
								colour=discord.Colour.from_rgb(29, 161, 242)
								)
							embed.set_footer(text='Twitter', icon_url='https://cdn.discordapp.com/attachments/865652402706972682/978702740786151424/Twitter-logo.svg.png')
							embed.set_author(name="KING's RAID OFFICIAL (@Play_KINGsRAID)", url='https://twitter.com/Play_KINGsRAID', icon_url='https://pbs.twimg.com/profile_images/1452700303845781504/BBNcSveS.jpg')
							if tweet.includes['media'][0].url:
								embed.set_image(url=tweet.includes['media'][0].url)
							if tweet.data.created_at:
								embed.timestamp = tweet.data.created_at
						except:
							traceback.print_exc()
							pass
						for key in self.channels:
							if self.channels[key]:
								chan = self.client.get_channel(int(key))
								try:
									if isinstance(chan, discord.abc.GuildChannel):
										attemp = f" | TWITTER attempting to send to channel #{key}"
										logging.info(attemp)
										print(attemp)
										try:
											await chan.send(embed=embed)
										except:
											await chan.send(message)
										success = f" | TWITTER successfully sent to #{chan.name} on {chan.guild.name}"
										logging.info(success)
										print(success)
									else:
										invalid = f" | TWITTER channel #{key} is invalid, removing"
										logging.info(invalid)
										print(invalid)
										self.channels[key] = False
										self.write_channels()
								except discord.errors.Forbidden as r:
									forbidden = f" | FORBIDDEN: {str(r)} | Channel: #{chan.name} on {chan.guild.name}"
									logging.warn(forbidden)
									print(forbidden)
								except Exception as e:
									logging.warn(e)
		except FileNotFoundError:
			with open('./data/twitter/tweets', 'a') as r:
				for id_ in tweets_id:
					r.write(str(id_) + "\n")
		except Exception as e:
			logging.warn(e)

	@twitter_.before_loop
	async def before_twitter_(self):
		await self.client.wait_until_ready()

	@commands.group() # twitter register
	async def twitter(self, ctx):
		if ctx.invoked_subcommand is None:
			embed = self.info_embed_.info_embed('Twitter')
			await ctx.reply(embed=embed)

	@twitter.command(name="on") # twitter register on
	@commands.has_permissions(manage_channels=True)
	async def twitter_on(self, ctx):
		chan = str(ctx.channel.id)
		self.channels[chan] = True
		self.write_channels()
		await ctx.reply("This channel has followed King's Raid Twitter.")


	@twitter.command(name="off") # twitter register off
	@commands.has_permissions(manage_channels=True)
	async def twitter_off(self, ctx):
		chan = str(ctx.channel.id)
		self.channels[chan] = False
		self.write_channels()
		await ctx.reply("This channel has unfollowed King's Raid Twitter.")

	def write_channels(self):
		with open(self.channel_path, "w") as f:
			f.write(json.dumps(self.channels))

def setup(client):
	client.add_cog(Twitter(client))





