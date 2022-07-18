import asyncio

from discord_slash.utils.manage_components import create_button, create_actionrow, spread_to_rows, wait_for_component
from discord_slash.model import ButtonStyle

from . import check_permisison

class Paginator: # paginator for slash & interactions command
    def __init__(self, client):
        self.client = client
        self.check = check_permisison.view_channels
        self.left = "\u25c0" # "\u2B05"
        self.right = "\u25b6" # "\u27A1"

    async def paginator(self, context, embeds, additional_buttons:list=None):
        if self.check(context.guild, context.channel) == True:
            await context.send(content="This command can't be used here...", hidden=True)
            return
        index = 0
        buttons = [create_button(style=ButtonStyle.blue, label=self.left),
                create_button(style=ButtonStyle.blue, label=self.right)]
        if additional_buttons is not None:
            for add_button in additional_buttons:
                buttons.append(add_button)
        if len(buttons) > 5:
            action_row = spread_to_rows(*buttons, max_in_row=5)
            await context.defer()
            try:
                msg = await context.edit_origin(embed=embeds[index], components=action_row)
            except:
                msg = await context.send(embed=embeds[index], components=action_row)
        else:
            action_row = create_actionrow(*buttons)
            try:
                msg = await context.edit_origin(embed=embeds[index], components=[action_row])
            except:
                msg = await context.send(embed=embeds[index], components=[action_row])
        while True:
            try:
                button_ctx: ComponentContext = await wait_for_component(self.client, components=action_row, timeout=60.0, check=lambda x: x.author_id == context.author.id)
                if button_ctx.component['label'] == self.left:
                    index -= 1
                    if index < 0:
                        index = len(embeds) - 1
                elif button_ctx.component['label'] == self.right:
                    index += 1
                    if index == len(embeds):
                        index = 0
                await button_ctx.edit_origin(embed=embeds[index])
            except asyncio.TimeoutError:
                buttons = []
                for row in msg.components:
                    for button in row['components']:
                        button['disabled'] = True
                        buttons.append(button)
                if len(buttons) > 5:
                    action_row = spread_to_rows(*buttons, max_in_row=5)
                    await msg.edit(content='Timeout! Please try again.', components=action_row)
                else:
                    action_row = create_actionrow(*buttons)
                    await msg.edit(content='Timeout! Please try again.', components=[action_row])
                break
