import discord, random
from discord.ext import commands

from config import config

client = discord.Client()


class Stuffs(commands.Cog):
    def __init__(self, client):
        self.client = client

    @commands.command() # macro command
    async def macro(self, ctx):
        embed = discord.Embed(
            title="King's Raid Emulator LoH Macro",
            description=("Nox App Player (04.04.2020)\nhttps://www.reddit.com/r/Kings_Raid/comments/fumrn9/new_loh_macro_for_nox_app_player_04042020/\n\n"+
                        "MEmu App Player (01.04.2020)\nhttps://www.reddit.com/r/Kings_Raid/comments/ft4z91/new_loh_macro_for_memu_play_01042020/\n\n"+
                        "LDPlayer (31.03.2020)\nhttps://www.reddit.com/r/Kings_Raid/comments/fsje29/new_loh_macro_for_ldplayer_31032020/\n\n"+
                        "LDPlayer auto dailies (by me)\nhttps://github.com/faber6/kings-raid-daily"),
            colour=config.embed_color,
        )
        await ctx.reply(embed=embed)

    @commands.command() # mail command
    async def mail(self, ctx):
        embed = discord.Embed(
            title="Vespa Mail",
            description="EN: cs_en@vespainc.oqupie.com\nJP: cs_jp@vespainc.oqupie.com\nTW: cs_tw@vespainc.oqupie.com\nKR: cs_kr@vespainc.oqupie.com",
            colour=config.embed_color,
        )
        await ctx.reply(embed=embed)

    @commands.command(aliases=['choose', 'pick']) # random command
    async def random(self, ctx, *, choices: str= None):
        if choices is None:
            embed = discord.Embed(
                title='Choose Command',
                description=('Syntax:\n'+
                'Single word: `choose <first_option second_option ...>`\n'+
                'Multiple words:\n'+
                '`choose <first option | second option | ...>`\n'+
                '`choose <"first option" "second option" "...>`\n'+
                '`choose <first option or second option or ...>`\n'+
                '`choose <first option, second option, ...>`\n'+
                'Random pick from the given list.'),
                colour=config.embed_color,
            )
            await ctx.reply(embed=embed)
        else:
            try:
                if '" "' in choices:
                    choices_ = choices.replace('" "', '", "')
                    choices_ = choices_[1:][:-1]
                elif "' '" in choices:
                    choices_ = choices.replace("' '", '", "')
                    choices_ = choices_[1:][:-1]
                elif ') (' in choices:
                    choices_ = choices.replace(') (', '", "')
                    choices_ = choices_[1:][:-1]
                elif '] [' in choices:
                    choices_ = choices.replace('] [', '", "')
                    choices_ = choices_[1:][:-1]
                elif '} {' in choices:
                    choices_ = choices.replace('} {', '", "')
                    choices_ = choices_[1:][:-1]
                elif ' | ' in choices:
                    choices_ = choices.replace(' | ', '", "')
                elif ' / ' in choices:
                    choices_ = choices.replace(' / ', '", "')
                elif ' & ' in choices:
                    choices_ = choices.replace(' & ', '", "')
                elif ' - ' in choices:
                    choices_ = choices.replace(' - ', '", "')
                elif ' or ' in choices:
                    choices_ = choices.replace(' or ', '", "')
                elif ', ' in choices:
                    choices_ = choices.replace(', ', '", "')
                elif '; ' in choices:
                    choices_ = choices.replace('; ', '", "')
                else:
                    choices_ = choices.replace(' ', '", "')
                choices = f'"{choices_}"'
                emote = [':face_with_raised_eyebrow:', ':face_with_monocle:', '<:worrythink:737581585825529916>', '<:worryfingergun:737581585385390132>', '<:worry:384946988770131970>']
                re = ['I pick', 'I choose']
                await ctx.reply(random.choice(emote) + ' ' + random.choice(re) + ' `'+random.choice(eval(choices))+'`.')
            except:
                await ctx.reply("I can't pick any from them.")

    @commands.command(aliases=['timezone', 'time_zone']) # timezone command
    async def tz(self, ctx):
        embed = discord.Embed(title="Servers time zone", colour=config.embed_color,
        description=("Asia - UTC+7 (Asia/Ho_Chi_Minh)\nEurope - UTC+2 (Europe/Bucharest)\nKorea - UTC+9 (Asia/Seoul)\n"+
                    "Ameria - UTC-4 (America/Anguilla)\nJapan - UTC+9 (Asia/Tokyo)\nTaiwan, HongKong, Macao - UTC+8 (Asia/Taipei)"))
        await ctx.reply(embed=embed)

def setup(client):
    client.add_cog(Stuffs(client))
