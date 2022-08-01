import discord, random
from discord.ext import commands

from discord_slash import cog_ext, SlashContext
from discord_slash.utils.manage_commands import create_option

from ..utils import check_permisison
from config import config

client = discord.Client()


class Stuffs(commands.Cog):
    def __init__(self, client):
        self.client = client
        self.check = check_permisison.view_channels


    @cog_ext.cog_slash(name='macro',
                    description="Give King's Raid Emulator LoH Macro",
                    guild_ids=config.guild_ids) # slash macro command
    async def macro_(self, ctx: SlashContext):
        embed = discord.Embed(
            title="King's Raid Emulator LoH Macro",
            description=("Nox App Player (04.04.2020)\nhttps://www.reddit.com/r/Kings_Raid/comments/fumrn9/new_loh_macro_for_nox_app_player_04042020/\n\n"+
                        "MEmu App Player (01.04.2020)\nhttps://www.reddit.com/r/Kings_Raid/comments/ft4z91/new_loh_macro_for_memu_play_01042020/\n\n"+
                        "LDPlayer (31.03.2020)\nhttps://www.reddit.com/r/Kings_Raid/comments/fsje29/new_loh_macro_for_ldplayer_31032020/\n\n"+
                        "LDPlayer auto dailies (by me)\nhttps://github.com/faber6/kings-raid-daily"),
            colour=config.embed_color,
        )
        if self.check(ctx.guild, ctx.channel) == True:
            await ctx.send(embed=embed, hidden=True)
        else:
            await ctx.send(embed=embed)


    @cog_ext.cog_slash(name='mail',
                    description="Give Vespa Mail",
                    guild_ids=config.guild_ids) # slash mail command
    async def mail_(self, ctx: SlashContext):
        embed = discord.Embed(
            title="Vespa Mail",
            description="EN: cs_en@vespainc.oqupie.com\nJP: cs_jp@vespainc.oqupie.com\nVI: cs_vn@vespainc.oqupie.com\nTH: cs_th@vespainc.oqupie.com\nTW: cs_tw@vespainc.oqupie.com",
            colour=config.embed_color,
        )
        if self.check(ctx.guild, ctx.channel) == True:
            await ctx.send(embed=embed, hidden=True)
        else:
            await ctx.send(embed=embed)


    @cog_ext.cog_slash(name='choose',
                    description="Random choose from the given list",
                    guild_ids=config.guild_ids,
                    options=[
                        create_option(name='option0', description='Input option 0', option_type=3, required=True),
                        create_option(name='option1', description='Input option 1', option_type=3, required=True),
                        create_option(name='option2', description='Input option 2', option_type=3, required=False),
                        create_option(name='option3', description='Input option 3', option_type=3, required=False),
                        create_option(name='option4', description='Input option 4', option_type=3, required=False),
                        create_option(name='option5', description='Input option 5', option_type=3, required=False),
                        create_option(name='option6', description='Input option 6', option_type=3, required=False),
                        create_option(name='option7', description='Input option 7', option_type=3, required=False),
                        create_option(name='option8', description='Input option 8', option_type=3, required=False),
                        create_option(name='option9', description='Input option 9', option_type=3, required=False),
                        create_option(name='option10', description='Input option 10', option_type=3, required=False),
                        create_option(name='option11', description='Input option 11', option_type=3, required=False),
                        create_option(name='option12', description='Input option 12', option_type=3, required=False),
                        create_option(name='option13', description='Input option 13', option_type=3, required=False),
                        create_option(name='option14', description='Input option 14', option_type=3, required=False),
                        create_option(name='option15', description='Input option 15', option_type=3, required=False),
                        create_option(name='option16', description='Input option 16', option_type=3, required=False),
                        create_option(name='option17', description='Input option 17', option_type=3, required=False),
                        create_option(name='option18', description='Input option 18', option_type=3, required=False),
                        create_option(name='option19', description='Input option 19', option_type=3, required=False),
                        create_option(name='option20', description='Input option 20', option_type=3, required=False),
                        create_option(name='option21', description='Input option 21', option_type=3, required=False),
                        create_option(name='option22', description='Input option 22', option_type=3, required=False),
                        create_option(name='option23', description='Input option 23', option_type=3, required=False),
                        create_option(name='option24', description='Input option 24', option_type=3, required=False),
                    ]
                    ) # slash choose command
    async def random_(self, ctx: SlashContext, option0:str, option1:str, option2:str=None, option3:str=None, option4:str=None, option5:str=None, option6:str=None, option7:str=None,\
                    option8:str=None, option9:str=None, option10:str=None, option11:str=None, option12:str=None, option13:str=None, option14:str=None, option15:str=None, option16:str=None,\
                    option17:str=None, option18:str=None, option19:str=None, option20:str=None, option21:str=None, option22:str=None, option23:str=None, option24:str=None):
        try:
            choices_ = [option0, option1, option2, option3, option4, option5, option6, option7,
                    option8, option9, option10, option11, option12, option13, option14, option15, option16,
                    option17, option18, option19, option20, option21, option22, option23, option24]
            choices = []
            for choice in choices_:
                if choice is not None:
                    choices.append(choice)
            emote = [':face_with_raised_eyebrow:', ':face_with_monocle:', '<:worrythink:737581585825529916>', '<:worryfingergun:737581585385390132>', '<:worry:384946988770131970>']
            re = ['I pick', 'I choose']
            if self.check(ctx.guild, ctx.channel) == True:
                await ctx.send(content=random.choice(emote) + ' ' + random.choice(re) + ' `' + random.choice(choices) + '`.', hidden=True)
            else:
                await ctx.send(random.choice(emote) + ' ' + random.choice(re) + ' `'+ random.choice(choices) + '`.')
        except:
            await ctx.send("I can't pick any from them", hidden=True)


    @cog_ext.cog_slash(name='timezone',
                    description="Give Servers time zone",
                    guild_ids=config.guild_ids)
    async def tz_(self, ctx):
        embed = discord.Embed(title="Servers time zone", colour=config.embed_color,
        description=("Asia - UTC+7 (Asia/Ho_Chi_Minh)\nEurope - UTC+2 (Europe/Bucharest)\nKorea - UTC+9 (Asia/Seoul)\n"+
                    "Ameria - UTC-4 (America/Anguilla)\nJapan - UTC+9 (Asia/Tokyo)\nTaiwan, HongKong, Macao - UTC+8 (Asia/Taipei)"))
        if self.check(ctx.guild, ctx.channel) == True:
            await ctx.send(embed=embed, hidden=True)
        else:
            await ctx.send(embed=embed)


def setup(client):
    client.add_cog(Stuffs(client))
