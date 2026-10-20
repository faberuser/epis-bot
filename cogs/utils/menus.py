"""Native views shared by prefix and application commands."""

import inspect
import logging
from dataclasses import dataclass
from pathlib import Path

import discord


@dataclass
class MenuResult:
    result: object
    view: "OwnedView"


def text_pages(title, text, colour):
    return [
        discord.Embed(title=title, description=text[i : i + 4000], colour=colour)
        for i in range(0, max(1, len(text)), 4000)
    ]


def asset(path, *, filename):
    return discord.File(path, filename=filename) if Path(path).is_file() else None


def result_kwargs(result, *, editing=False):
    if isinstance(result, str):
        return {
            "content": result,
            "embed": None,
            **({"attachments": []} if editing else {}),
        }
    embed, file = result if isinstance(result, tuple) else (result, None)
    if file is None:
        for name in ("thumbnail", "image"):
            if str(getattr(embed, name).url).startswith("attachment://"):
                getattr(embed, "set_" + name)(url=None)
    kwargs = {"content": None, "embed": embed}
    if editing:
        kwargs["attachments"] = [file] if file else []
    elif file:
        kwargs["file"] = file
    return kwargs


async def send_result(ctx, result, *, view=None):
    message = await ctx.send(**result_kwargs(result), view=view)
    if view is not None:
        view.message = message
    return message


class OwnedView(discord.ui.View):
    def __init__(self, author_id, *, timeout=120):
        super().__init__(timeout=timeout)
        self.author_id = author_id
        self.message: discord.Message | None = None

    async def interaction_check(self, interaction):
        if interaction.user.id != self.author_id:
            await interaction.response.send_message(
                "Only the person who opened this menu can use it.", ephemeral=True
            )
            return False
        return True

    async def on_timeout(self):
        for child in self.children:
            if isinstance(child, (discord.ui.Button, discord.ui.Select)):
                child.disabled = True
        if self.message is not None:
            try:
                await self.message.edit(view=self)
            except discord.HTTPException:
                pass

    async def on_error(self, interaction, error, item):
        logging.getLogger(__name__).error(
            "Menu failed", exc_info=(type(error), error, error.__traceback__)
        )
        message = "This action failed. Please try again later."
        if interaction.response.is_done():
            await interaction.followup.send(message, ephemeral=True)
        else:
            await interaction.response.send_message(message, ephemeral=True)


class ChoiceView(OwnedView):
    """Paginate any number of choices without exceeding Discord's 25-option limit."""

    def __init__(
        self, author_id, choices, render, *, timeout=120, placeholder="Choose an item"
    ):
        super().__init__(author_id, timeout=timeout)
        if not choices:
            raise ValueError("A choice menu needs at least one option.")
        self.choices = list(choices)
        self.render = render
        self.page = 0
        self.placeholder = placeholder
        self.selector = discord.ui.Select(row=0)
        self.selector.callback = self.select
        self.add_item(self.selector)
        self.refresh()

    def refresh(self):
        start = self.page * 25
        self.selector.options = [
            discord.SelectOption(label=str(label)[:100], value=str(index))
            for index, (label, value) in enumerate(
                self.choices[start : start + 25], start
            )
        ]
        total = (len(self.choices) + 24) // 25
        self.selector.placeholder = f"{self.placeholder} ({self.page + 1}/{total})"[
            :150
        ]
        self.previous.disabled = self.page == 0
        self.next.disabled = self.page + 1 >= total

    async def select(self, interaction):
        await interaction.response.defer()
        index = int(self.selector.values[0])
        result = self.render(self.choices[index][1])
        if inspect.isawaitable(result):
            result = await result
        if isinstance(result, MenuResult):
            await interaction.edit_original_response(
                **result_kwargs(result.result, editing=True), view=result.view
            )
            result.view.message = self.message
            self.stop()
            return
        if isinstance(result, list):
            if not result:
                await interaction.followup.send(
                    "There are no pages to display.", ephemeral=True
                )
                return
            from .paginator import PageView

            pages = PageView(self.author_id, result)
            pages.message = await interaction.followup.send(
                embed=result[0], view=pages, wait=True
            )
            return
        await interaction.edit_original_response(
            **result_kwargs(result, editing=True), view=self
        )

    @discord.ui.button(label="Previous", row=1)
    async def previous(self, interaction, button):
        self.page = max(0, self.page - 1)
        self.refresh()
        await interaction.response.edit_message(view=self)

    @discord.ui.button(label="Next", row=1)
    async def next(self, interaction, button):
        self.page = min((len(self.choices) - 1) // 25, self.page + 1)
        self.refresh()
        await interaction.response.edit_message(view=self)
