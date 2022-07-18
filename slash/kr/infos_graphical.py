import discord, json, asyncio, os, traceback, asyncio, re
import re as research
from fuzzywuzzy import process
from discord.ext import commands
from PIL import Image
from PIL import ImageDraw

from discord_slash.utils.manage_components import create_actionrow, spread_to_rows, create_button, wait_for_component, create_select, create_select_option
from discord_slash.utils.manage_commands import create_choice, create_option
from discord_slash.model import ButtonStyle
from discord_slash import cog_ext, SlashContext

from ..utils import check_permisison, embed_file, find_obj
from config import config

client = discord.Client()


class Heroes_Graphical(commands.Cog):
    def __init__(self, client):
        self.client = client
        self.check = check_permisison.view_channels
        self.embed_file = embed_file.embed_file
        self.embed_file = embed_file.embed_file
        self.find = find_obj.find
        self.find_boss = find_obj.find_boss
        self.find_ = find_obj.find_
        self.get_color = find_obj.get_color


    @cog_ext.cog_slash(
                    name='profile',
                    description="Give Hero's Profile",
                    guild_ids=config.guild_ids,
                    options=[
                        create_option(
                            name="hero",
                            description="Input a hero",
                            option_type=3,
                            required=True
                        ),
                    ]) # slash hero's info command
    async def profile_hero(self, ctx: SlashContext, *, hero: str):
        obj, data = self.find(hero)
        clr = self.get_color(data['infos']['class'].lower())

    def get_infos(self, obj, data, clr):
        return

    def get_splashart(self, obj, data, clr):
        return

    def get_costumes(self, obj, data, clr):
        return

    def get_skills(self, obj, data, clr):
        return

    def get_perks(self, obj, data, clr):
        return

    def get_uw(self, obj, data, clr):
        return

    def get_sw(self, obj, data, clr):
        return

    def get_ut1(self, obj, data, clr):
        return

    def get_ut2(self, obj, data, clr):
        return

    def get_ut3(self, obj, data, clr):
        return

    def get_ut4(self, obj, data, clr):
        return

    def generate_image(self):
        img = Image.new('RGB', (200, 100))
        d = ImageDraw.Draw(img)
        d.text((20, 20), 'Hello', fill=(255, 0, 0))
        text_width, text_height = d.textsize('Hello')
        img.show()

def setup(client):
    client.add_cog(Heroes_Graphical(client))


# # send pillow image object
# from io import BytesIO

# # if you have an image or anything that saves to a stream
# buffer = BytesIO()
# im.save(buffer, "png")  # 'save' function for PIL, adapt as necessary
# buffer.seek(0)

# # if you have some bytes
# buffer = BytesIO(my_bytes)

# # if you have some text
# my_text = "Don't do drugs kids"
# buffer = BytesIO(my_text.encode("utf8"))  # change encoding as necessary

# await ctx.send(file=discord.File(fp=buffer, filename="whatever.png"))