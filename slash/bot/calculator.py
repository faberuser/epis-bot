import discord, asyncio, concurrent.futures, re, traceback
from discord.ext import commands
from py_expression_eval import Parser

from discord_slash.utils.manage_components import create_button, spread_to_rows, wait_for_component
from discord_slash.model import ButtonStyle
from discord_slash import cog_ext, SlashContext

from ..utils import check_permisison
from config import config

client = discord.Client()

class Calculator(commands.Cog):
    
    def __init__(self, client):
        self.client = client
        self.check = check_permisison.view_channels
        self.parser = Parser()


    @cog_ext.cog_slash(name='calculator',
                    description='Give a graphical calculator',
                    guild_ids=config.guild_ids) # slash command calculator
    async def calculator_(self, ctx: SlashContext):
        if self.check(ctx.guild, ctx.channel) == True:
            await ctx.send(content="This command can't be used here...", hidden=True)
            return
        def get_embed(calc):
            index = 31-len(str(calc))
            emty = (' ')*index
            em=discord.Embed(title=f"{ctx.author.display_name}'s Calculator",description=f"```{emty}{calc}```",color=ctx.author.color)
            return em

        exit=False
        buttons = [
                create_button(label="Exit", style=ButtonStyle.red), create_button(label="Clear", style=ButtonStyle.green), create_button(label="\u2B05", style=ButtonStyle.grey), create_button(label=":", style=ButtonStyle.grey),
                create_button(label="7", style=ButtonStyle.blue), create_button(label="8", style=ButtonStyle.blue), create_button(label="9", style=ButtonStyle.blue), create_button(label="x", style=ButtonStyle.grey),
                create_button(label="4", style=ButtonStyle.blue),create_button(label="5", style=ButtonStyle.blue), create_button(label="6", style=ButtonStyle.blue), create_button(label="-", style=ButtonStyle.grey),
                create_button(label="1", style=ButtonStyle.blue), create_button(label="2", style=ButtonStyle.blue), create_button(label="3", style=ButtonStyle.blue), create_button(label="+", style=ButtonStyle.grey),
                create_button(label= "000", style=ButtonStyle.blue), create_button(label= "0", style=ButtonStyle.blue), create_button(label=".", style=ButtonStyle.grey), create_button(label="=", style=ButtonStyle.grey),
            ]
        action_row = spread_to_rows(*buttons, max_in_row=4)
        calculation = ""
        msg = await ctx.send(embed=get_embed("0"), components=action_row)

        try:
            while not exit:
                button_ctx: ComponentContext = await wait_for_component(self.client, components=action_row, timeout=300.0, check=lambda x: x.author_id == ctx.author.id)
                label = button_ctx.component['label']
                if label == "=":
                    try:
                        exp = ((((calculation.replace("`", "")).replace(":", "/")).replace("x", "*"))).replace(",", "")#.replace("%", "/100")
                        #listed = self.split_numbers(exp)
                        #pct_filter = await self.percentage(listed)
                        result = await asyncio.wait_for(self.a_parse(exp), timeout=1)
                        if len(str(round(result))) > 3:
                            result = f'{result:,}'
                        calculation = str(result)
                        await button_ctx.edit_origin(embed=get_embed(calculation))
                    except:
                        await button_ctx.edit_origin(embed=get_embed("Invalid calculation"))
                elif label == "Exit":
                    exit = True
                elif label == "Clear":
                    calculation = ""
                    await button_ctx.edit_origin(embed=get_embed("0"))
                elif label == "\u2B05":
                    calculation = calculation[:-1]
                    if len(calculation) == 0:
                        await button_ctx.edit_origin(embed=get_embed("0"))
                    else:
                        split = self.split_numbers(calculation.replace(',', ''))
                        text = self.thousands_separator(split)
                        await button_ctx.edit_origin(embed=get_embed(text))
                else:
                    if label == '/' or label == ':' or label == '*' or label == 'x' or label == '-' or label == '+' or \
                        label == '.' or label == '(' or label == ')':
                        if calculation[-1] in '/:*x-+.(':
                            pass
                        else:
                            calculation+=button_ctx.component['label']
                            split = self.split_numbers(calculation.replace(',', ''))
                            text = self.thousands_separator(split)
                            await button_ctx.edit_origin(embed=get_embed(text), type=6)
                    elif label == '%' or label == ')':
                        if calculation[-1] == '%':
                            pass
                        elif calculation[-1] == ')':
                            pass
                        else:
                            calculation+=button_ctx.component['label']
                            split = self.split_numbers(calculation.replace(',', ''))
                            text = self.thousands_separator(split)
                            await button_ctx.edit_origin(embed=get_embed(text))
                    else:
                        calculation+=button_ctx.component['label']
                        split = self.split_numbers(calculation.replace(',', ''))
                        text = self.thousands_separator(split)
                        await button_ctx.edit_origin(embed=get_embed(text), type=6)
            buttons = []
            for row in msg.components:
                for button in row['components']:
                    button['disabled'] = True
                    buttons.append(button)
            action_row = spread_to_rows(*buttons, max_in_row=4)
            await button_ctx.edit_origin(content='Exited', components=action_row)
        except asyncio.TimeoutError:
            buttons = []
            for row in msg.components:
                for button in row['components']:
                    button['disabled'] = True
                    buttons.append(button)
            action_row = spread_to_rows(*buttons, max_in_row=4)
            await button_ctx.edit_origin(content='Timeout! Please try again.', components=action_row)

    def split_numbers(self, text:str):
        def split(word):
            return [char for char in word]
        splited = re.split('(\d+)',text)
        lst = []
        for i, s in enumerate(splited):
            if s.isnumeric() == False:
                splited[i] = split(s)
        flat_list = []
        for sublist in splited:
            if isinstance(sublist, list):
                for item in sublist:
                    flat_list.append(item)
            else:
                flat_list.append(sublist)
        return flat_list

    def thousands_separator(self, listed:list):
        text = ''
        for each in listed:
            if each.isnumeric():
                if len(str(round(int(each)))) > 3:
                    each=f'{int(each):,}'
                text+=each
            else:
                text+=each
        return text
 
    async def percentage(self, listed:list): # i had no idea what i did here
        try:
            count = 0
            while True:
                count_ = 0
                if str('%') not in listed:
                    break
                for each in listed:
                    if each == '%':
                        percentage_location = count
                        # none of these 2 working as expected

                        # method 1: put bracket 2 side of expression but not done yet
                        # try:
                        #     if plus_minus == listed[percentage_location - 2] not in '+-':
                        #         continue
                        # except:
                        #     continue
                        # right_bracket = percentage_location + 1
                        # left_bracket = percentage_location - 4
                        # right, left == False, False
                        # try:
                        #     listed[right_bracket]
                        # except IndexError:
                        #     listed.append(')')
                        #     right = True
                        # try:
                        #     listed[left_bracket]
                        # except IndexError:
                        #     listed_ = listed
                        #     listed = ['(']
                        #     for each in listed_:
                        #         listed.append(each)
                        #     left = True
                        # ct = 0
                        # listed_ = listed
                        # listed = []
                        # for each in listed_:
                        #     if ct == right_bracket and right == False:
                        #         listed.append(')')
                        #     elif ct == left_bracket and left == False:
                        #         listed.append('(')
                        #     else:
                        #         listed.append(each)
                        #     ct += 1
                        # print(listed)

                        # method 2: calculate multiply/division first then plus/minus
                        try:
                            multiply_division = listed[percentage_location + 1]
                        except:
                            multiply_division = '='
                        try:
                            number_after = listed[percentage_location + 2]
                        except:
                            number_after = '='
                        try:
                            plus_minus = listed[percentage_location - 2]
                        except:
                            plus_minus = '='
                        try:
                            number_pct = listed[percentage_location - 1]
                        except:
                            number_pct = '='
                        try:
                            number_before = listed[percentage_location - 3]
                        except:
                            number_before = '='
                        if multiply_division in '*/':
                            listed_ = listed
                            listed = []
                            pct_ = f"{number_pct}/100{multiply_division}{number_after}"
                            pct = await asyncio.wait_for(self.a_parse(pct_), timeout=1)
                            for each in listed_:
                                if each in [number_pct, '%', multiply_division, number_after]:
                                    if count_ == 1:
                                        pass
                                    else:
                                        count_ += 1
                                        listed.append(str(pct))
                                        continue
                                listed.append(str(each))
                        elif plus_minus in '+-':
                            listed_ = listed
                            listed = []
                            pct_ = f"{number_before}{plus_minus}{number_before}*{number_pct}/100"
                            pct = await asyncio.wait_for(self.a_parse(pct_), timeout=1)
                            for each in listed_:
                                if each in [number_before, plus_minus, number_pct, '%']:
                                    if count_ == 1:
                                        pass
                                    else:
                                        count_ += 1
                                        listed.append(str(pct))
                                        continue
                                listed.append(str(each))
                        else:
                            listed_ = listed
                            listed = []
                            for each in listed_:
                                if each in ['%']:
                                    each = '/100'
                                listed.append(str(each))
                    count+=1
            text = ''
            for i in listed:
                text+=i
            print(text)
            return text
        except:
            traceback.print_exc()

    async def a_parse(self, expression):
        loop = asyncio.get_running_loop()
        with concurrent.futures.ThreadPoolExecutor() as pool:
            result = await loop.run_in_executor(pool, self.parse, expression)
        return result

    def parse(self, expression):
        return self.parser.parse(expression).evaluate({})

def setup(client):
    client.add_cog(Calculator(client))
