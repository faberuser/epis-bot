import asyncio
import logging

import discord
from discord.ext import commands


class PageView(discord.ui.View):
    """A bounded embed paginator controlled by the command's author."""

    def __init__(self, author_id, embeds, *, timeout=60.0):
        if not embeds:
            raise ValueError("The paginator needs at least one embed.")
        super().__init__(timeout=timeout)
        self.author_id = author_id
        self.embeds = list(embeds)
        self.index = 0
        self.message: discord.Message | None = None
        self.lock = asyncio.Lock()
        self.update_buttons()

    def update_buttons(self):
        self.previous.disabled = self.index == 0
        self.next.disabled = self.index == len(self.embeds) - 1

    async def interaction_check(self, interaction):
        if interaction.user.id != self.author_id:
            await interaction.response.send_message(
                "Only the person who opened this menu can use it.", ephemeral=True
            )
            return False
        return True

    async def turn_page(self, interaction, step):
        async with self.lock:
            if self.is_finished():
                await interaction.response.send_message(
                    "This menu has expired.", ephemeral=True
                )
                return
            self.index = max(0, min(self.index + step, len(self.embeds) - 1))
            self.update_buttons()
            await interaction.response.edit_message(
                embed=self.embeds[self.index], view=self
            )

    @discord.ui.button(emoji="\u25c0", style=discord.ButtonStyle.primary)
    async def previous(
        self, interaction: discord.Interaction, button: discord.ui.Button
    ):
        await self.turn_page(interaction, -1)

    @discord.ui.button(emoji="\u25b6", style=discord.ButtonStyle.primary)
    async def next(self, interaction: discord.Interaction, button: discord.ui.Button):
        await self.turn_page(interaction, 1)

    async def on_timeout(self):
        async with self.lock:
            for item in self.children:
                if isinstance(item, (discord.ui.Button, discord.ui.Select)):
                    item.disabled = True
            if self.message is not None:
                try:
                    await self.message.edit(view=self)
                except discord.HTTPException:
                    logging.getLogger(__name__).debug(
                        "Could not disable expired paginator", exc_info=True
                    )


class Paginator:
    def __init__(self, client):
        self.client = client

    async def pag(self, message, embeds):
        """Accept either a prefix Message or a prefix/hybrid Context."""
        send = message.send if isinstance(message, commands.Context) else message.reply
        if not embeds:
            return await send("There are no pages to display.")
        view = PageView(message.author.id, embeds)
        try:
            view.message = await send(embed=view.embeds[0], view=view)
        except Exception:
            view.stop()
            raise
        return view.message
