"""Offline migration checks; no real configuration or Discord connection is used."""

import asyncio
import json
from pathlib import Path
import sys
import tempfile
import types
import unittest
from types import SimpleNamespace
from unittest.mock import AsyncMock, MagicMock, patch

import discord
from discord import app_commands
from discord.ext import commands


settings = SimpleNamespace(
    PREFIX="!", DISCORD_TOKEN="", embed_color=discord.Colour.blue(),
    POLICY="", donate="",
)
config_package = types.ModuleType("config")
config_package.config = settings
previous_config = sys.modules.get("config")
sys.modules["config"] = config_package
try:
    import main
    from cogs.utils.paginator import PageView, Paginator
finally:
    if previous_config is None:
        sys.modules.pop("config", None)
    else:
        sys.modules["config"] = previous_config


USER = {"id": "456", "username": "tester", "discriminator": "0", "avatar": None}


class MigrationTests(unittest.IsolatedAsyncioTestCase):
    async def asyncSetUp(self):
        self.bot = main.create_bot()
        await self.bot.__aenter__()
        self.bot._connection.user = discord.ClientUser(
            state=self.bot._connection,
            data={**USER, "id": "123", "username": "offline-bot"},
        )
        previous = sys.modules.get("config")
        sys.modules["config"] = config_package
        try:
            await self.bot.load_extension("cogs.bot.client")
            await self.bot.load_extension("cogs.kr.stuffs")
        finally:
            if previous is None:
                sys.modules.pop("config", None)
            else:
                sys.modules["config"] = previous

    async def asyncTearDown(self):
        await self.bot.close()

    def message(self, content):
        return discord.Message(
            state=self.bot._connection,
            channel=discord.PartialMessageable(state=self.bot._connection, id=789),
            data={
                "id": str(discord.utils.time_snowflake(discord.utils.utcnow())),
                "content": content, "author": USER, "type": 0,
                "attachments": [], "embeds": [], "edited_timestamp": None,
                "mention_everyone": False, "tts": False, "pinned": False,
            },
        )

    def interaction(self, name):
        interaction = discord.Interaction(
            state=self.bot._connection,
            data={
                "id": str(discord.utils.time_snowflake(discord.utils.utcnow())),
                "application_id": "123", "type": 2, "token": "offline",
                "version": 1, "locale": "en-US", "user": USER,
                "channel": {"id": "789", "type": 1},
                "data": {"id": "999", "name": name, "type": 1},
                "attachment_size_limit": 10485760,
            },
        )
        return interaction

    async def test_prefix_and_slash_macro_use_the_same_callback(self):
        prefix = self.bot.get_command("macro")
        slash = self.bot.tree.get_command("macro")
        self.assertIsInstance(prefix, commands.HybridCommand)
        self.assertIs(slash.wrapped, prefix)
        with patch.object(discord.abc.Messageable, "send", new_callable=AsyncMock) as send:
            ctx = await self.bot.get_context(self.message("!macro"))
            await self.bot.invoke(ctx)
            prefix_embed = send.await_args.kwargs["embed"].to_dict()
        interaction = self.interaction("macro")
        response_message = MagicMock(spec=discord.InteractionMessage)
        with patch.object(discord.InteractionResponse, "send_message", new_callable=AsyncMock) as respond:
            respond.return_value = SimpleNamespace(resource=response_message)
            await slash._invoke_with_namespace(interaction, app_commands.Namespace(interaction, {}, []))
            self.assertFalse(interaction.command_failed)
            self.assertEqual(respond.await_args.kwargs["embed"].to_dict(), prefix_embed)

    async def test_slash_help_sends_a_button_menu(self):
        interaction = self.interaction("help")
        response_message = MagicMock(spec=discord.InteractionMessage)
        with patch.object(discord.InteractionResponse, "send_message", new_callable=AsyncMock) as respond:
            respond.return_value = SimpleNamespace(resource=response_message)
            await self.bot.tree.get_command("help")._invoke_with_namespace(
                interaction, app_commands.Namespace(interaction, {}, [])
            )
            self.assertFalse(interaction.command_failed)
            view = respond.await_args.kwargs["view"]
            self.assertIsInstance(view, discord.ui.View)
            self.assertEqual(view.author_id, int(USER["id"]))
            self.assertEqual(len(view.embeds), 2)
            self.assertIs(view.message, response_message)
            view.stop()

    async def test_prefix_help_alias_and_topic_still_work(self):
        with patch.object(discord.abc.Messageable, "send", new_callable=AsyncMock) as send:
            ctx = await self.bot.get_context(self.message("!h hero"))
            await self.bot.invoke(ctx)
            self.assertFalse(ctx.command_failed)
            self.assertIsInstance(send.await_args.kwargs["embed"], discord.Embed)

    async def test_reload_does_not_duplicate_commands(self):
        await self.bot.reload_extension("cogs.kr.stuffs")
        self.assertEqual([c.name for c in self.bot.tree.get_commands()].count("macro"), 1)
        self.assertIs(self.bot.get_command("choose"), self.bot.get_command("random"))

    async def test_startup_loads_once_and_does_not_publish_commands(self):
        with tempfile.TemporaryDirectory() as directory:
            with patch.object(main, "DATA", Path(directory)), \
                 patch.object(self.bot, "load_extensions", new_callable=AsyncMock) as load, \
                 patch.object(self.bot.tree, "sync", new_callable=AsyncMock) as sync:
                await self.bot.setup_hook()
                await self.bot.on_ready()
                await self.bot.on_ready()
                load.assert_awaited_once()
                sync.assert_not_awaited()
                self.assertTrue(self.bot.change_status.is_running())
                index = (Path(directory) / "commands").read_text(encoding="utf-8")
                self.assertIn("macro\n", index)
                self.assertEqual(index.count("macro\n"), 1)

    async def test_sync_defaults_to_current_guild_and_is_owner_only(self):
        ctx = SimpleNamespace(bot=self.bot, author=SimpleNamespace(id=456), guild=SimpleNamespace(id=42), send=AsyncMock())
        command = self.bot.get_command("sync")
        with patch.object(self.bot, "is_owner", new_callable=AsyncMock, return_value=False):
            with self.assertRaises(commands.NotOwner):
                await command.checks[0](ctx)
        with patch.object(self.bot.tree, "sync", new_callable=AsyncMock, return_value=[]) as sync:
            await command.callback(ctx)
            self.assertEqual(sync.await_args.kwargs["guild"].id, 42)
            self.assertEqual(
                {c.name for c in self.bot.tree.get_commands(guild=discord.Object(id=42))},
                {c.name for c in self.bot.tree.get_commands()},
            )

    async def test_default_sync_in_dm_does_not_publish(self):
        ctx = SimpleNamespace(guild=None, send=AsyncMock())
        with patch.object(self.bot.tree, "sync", new_callable=AsyncMock) as sync:
            await self.bot.get_command("sync").callback(ctx)
            sync.assert_not_awaited()

    async def test_prefix_defaults_and_guild_override(self):
        with tempfile.TemporaryDirectory() as directory:
            with patch.object(main, "DATA", Path(directory)):
                dm = SimpleNamespace(guild=None)
                guild = SimpleNamespace(guild=SimpleNamespace(id=42))
                self.assertEqual(main.determine_prefix(self.bot, dm), "!")
                self.assertEqual(main.determine_prefix(self.bot, guild), "!")
                (Path(directory) / "prefixes.json").write_text(json.dumps({"42": "?"}))
                self.assertEqual(main.determine_prefix(self.bot, guild), "?")


class PaginatorTests(unittest.IsolatedAsyncioTestCase):
    async def test_buttons_bound_navigation_to_available_pages(self):
        embeds = [discord.Embed(title="First"), discord.Embed(title="Second")]
        view = PageView(1, embeds)
        interaction = SimpleNamespace(response=SimpleNamespace(edit_message=AsyncMock()))
        self.assertTrue(view.previous.disabled)
        self.assertFalse(view.next.disabled)
        await view.next.callback(interaction)
        self.assertEqual(view.index, 1)
        self.assertTrue(view.next.disabled)
        self.assertFalse(view.previous.disabled)
        self.assertIs(interaction.response.edit_message.await_args.kwargs["embed"], embeds[1])
        await view.next.callback(interaction)
        self.assertEqual(view.index, 1)
        await view.previous.callback(interaction)
        self.assertEqual(view.index, 0)
        view.stop()

    async def test_other_users_are_rejected_privately(self):
        view = PageView(1, [discord.Embed()])
        interaction = SimpleNamespace(user=SimpleNamespace(id=2), response=SimpleNamespace(send_message=AsyncMock()))
        self.assertFalse(await view.interaction_check(interaction))
        self.assertTrue(interaction.response.send_message.await_args.kwargs["ephemeral"])
        interaction.user.id = 1
        self.assertTrue(await view.interaction_check(interaction))
        view.stop()

    async def test_timeout_disables_all_buttons(self):
        view = PageView(1, [discord.Embed(), discord.Embed()])
        view.message = SimpleNamespace(edit=AsyncMock())
        await view.on_timeout()
        self.assertTrue(all(child.disabled for child in view.children))
        view.message.edit.assert_awaited_once_with(view=view)
        view.stop()

    async def test_deleted_message_during_timeout_is_handled(self):
        view = PageView(1, [discord.Embed()])
        error = discord.NotFound(SimpleNamespace(status=404, reason="Not Found"), "Deleted")
        view.message = SimpleNamespace(edit=AsyncMock(side_effect=error))
        await view.on_timeout()
        view.stop()

    async def test_empty_results_and_legacy_message_entry_point(self):
        message = SimpleNamespace(author=SimpleNamespace(id=1), reply=AsyncMock())
        paginator = Paginator(None)
        await paginator.pag(message, [])
        message.reply.assert_awaited_once_with("There are no pages to display.")
        await paginator.pag(message, [discord.Embed()])
        view = message.reply.await_args.kwargs["view"]
        self.assertTrue(all(child.disabled for child in view.children))
        view.stop()


if __name__ == "__main__":
    unittest.main()
