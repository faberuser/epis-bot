import asyncio
import json
from pathlib import Path
from types import SimpleNamespace
import sys
import unittest
from unittest.mock import AsyncMock, MagicMock, patch

import discord

import test_migration as base


class FullMigrationTests(unittest.IsolatedAsyncioTestCase):
    async def asyncSetUp(self):
        self.settings = SimpleNamespace(
            **vars(base.settings), BEARER_TOKEN="", CONSUMER_KEY="",
            CONSUMER_SECRET="", ACCESS_TOKEN="", ACCESS_TOKEN_SECRET="",
            kre_guild_id=0, kre_categories=[], kre_invite="",
            cache_channel=0, parallel_tasks=False, windows=True,
        )
        self.config = patch.object(base.config_package, "config", self.settings)
        self.config.start()
        self.previous_config = sys.modules.get("config")
        sys.modules["config"] = base.config_package
        self.bot = base.main.create_bot()
        await self.bot.__aenter__()
        self.bot._connection.user = discord.ClientUser(
            state=self.bot._connection,
            data={**base.USER, "id": "123", "username": "offline-bot"},
        )
        self.failures = await self.bot.load_extensions()

    async def asyncTearDown(self):
        await self.bot.close()
        if self.previous_config is None:
            sys.modules.pop("config", None)
        else:
            sys.modules["config"] = self.previous_config
        self.config.stop()

    async def invoke_slash(self, path, **options):
        parts = path.split()
        interaction = base.MigrationTests.interaction(self, parts[0])
        values = [{"name": name, "value": value, "type": 4 if isinstance(value, int) else 3} for name, value in options.items()]
        interaction.data["options"] = [{"type": 1, "name": parts[1], "options": values}] if len(parts) > 1 else values
        response = MagicMock(spec=discord.InteractionMessage)
        with patch.object(discord.InteractionResponse, "send_message", new_callable=AsyncMock, return_value=SimpleNamespace(resource=response)) as send, \
             patch.object(discord.InteractionResponse, "defer", new_callable=AsyncMock):
            await self.bot.tree._call(interaction)
            await asyncio.sleep(0)
            self.assertFalse(interaction.command_failed, path)
            self.assertTrue(send.await_count, path)
            return send.await_args.kwargs

    async def test_all_extensions_load_and_every_legacy_slash_path_is_present(self):
        self.assertEqual(self.failures, [])
        for name in ("feedback", "report", "reply", "response", "cases", "case", "fanart", "fa", "fanart_pick", "tic_tac_toe", "ttt", "vote"):
            self.assertIsNone(self.bot.get_command(name), name)
            self.assertIsNone(self.bot.tree.get_command(name), name)
        self.assertIsNone(self.bot.tree.get_command("bot").get_command("vote"))
        expected = set(json.loads(Path("tests/fixtures/slash_commands.json").read_text()))
        actual = {command.qualified_name for command in self.bot.tree.walk_commands() if not isinstance(command, discord.app_commands.Group)}
        self.assertFalse(expected - actual, expected - actual)
        for command in self.bot.tree.get_commands():
            payload = command.to_dict(self.bot.tree)
            self.assertLessEqual(len(payload.get("options", [])), 25)

    async def test_grouped_alias_invokes_the_shared_hybrid_callback(self):
        source = self.bot.get_command("info")
        alias = self.bot.tree.get_command("infos").get_command("hero")
        self.assertIs(alias.wrapped, source)
        with patch("cogs.utils.hero_rendering.asset", return_value=None):
            result = await self.invoke_slash("infos hero", hero="Epis")
        self.assertIn("Epis", result["embed"].title)
        self.assertIsNone(result["embed"].thumbnail.url)

    async def test_grouped_bot_command_invokes_shared_callback(self):
        result = await self.invoke_slash("bot uptime")
        self.assertIn("uptime", (str(result.get("content")) + str(result["embed"].to_dict())).lower())

    async def test_hybrid_math_and_choices_are_usable(self):
        result = await self.invoke_slash("calc", operation="7 + 3")
        self.assertIn("10", result["embed"].title)
        result = await self.invoke_slash("choose", choices="first option | second option")
        self.assertIn(result["content"], ("I pick `first option`.", "I pick `second option`."))
        self.assertIs(self.bot.get_command("calculator"), self.bot.get_cog("Calculator").calculator)
        self.assertIs(self.bot.get_command("calculate"), self.bot.get_command("calc"))
        result = await self.invoke_slash("softcap", value=1000)
        self.assertIn("1000", result["embed"].title)

    async def test_equipment_story_and_perk_menus(self):
        for name in ("story", "perks", "uts"):
            result = await self.invoke_slash(name, hero="Epis")
            self.assertIsInstance(result["view"], discord.ui.View)
            self.assertGreater(len(result["view"].choices), 1)
            result["view"].stop()

    async def test_sync_refuses_an_incomplete_command_tree(self):
        self.bot.extension_failures = ["cogs.kr.infos"]
        ctx = SimpleNamespace(send=AsyncMock(), guild=SimpleNamespace(id=42))
        with patch.object(self.bot.tree, "sync", new_callable=AsyncMock) as sync:
            await self.bot.get_command("sync").callback(ctx)
            sync.assert_not_awaited()
        self.assertIn("cogs.kr.infos", ctx.send.await_args.args[0])

    async def test_starred_equipment_and_multiword_prefix_name(self):
        result = await self.invoke_slash("uw", hero="Epis", stars=5)
        self.assertIn("Epis", result["embed"].title)
        if isinstance(result.get("file"), discord.File):
            result["file"].close()
        with patch.object(discord.abc.Messageable, "send", new_callable=AsyncMock) as send:
            message = base.MigrationTests.message(self, '!uw "Fallen Frey" 3')
            ctx = await self.bot.get_context(message)
            await self.bot.invoke(ctx)
            self.assertFalse(ctx.command_failed)
            self.assertIn("Frey", send.await_args.kwargs["embed"].title)
            if isinstance(send.await_args.kwargs.get("file"), discord.File):
                send.await_args.kwargs["file"].close()

    async def test_artifact_search_and_guide_missing_server(self):
        result = await self.invoke_slash("artifact search", name="sword")
        self.assertIsInstance(result["view"], discord.ui.View)
        result["view"].stop()
        from discord.ext import commands
        with self.assertRaises(commands.BadArgument):
            self.bot.get_cog("Guide").channels()

    async def test_unload_and_reload_removes_group_routes(self):
        for extension, root in (("cogs.kr.infos", "infos"), ("cogs.kr.artifacts", "artifact"), ("cogs.kr.guide", "guide"), ("cogs.bot.client", "bot")):
            await self.bot.unload_extension(extension)
            self.assertIsNone(self.bot.tree.get_command(root))
            await self.bot.load_extension(extension)
            self.assertIsNotNone(self.bot.tree.get_command(root))
            await self.bot.reload_extension(extension)
        names = [command.qualified_name for command in self.bot.tree.walk_commands()]
        self.assertEqual(len(names), len(set(names)))


class NativeViewTests(unittest.IsolatedAsyncioTestCase):
    def interaction(self, user_id=456):
        return SimpleNamespace(
            user=SimpleNamespace(id=user_id),
            response=SimpleNamespace(defer=AsyncMock(), edit_message=AsyncMock(), send_message=AsyncMock()),
            edit_original_response=AsyncMock(), followup=SimpleNamespace(send=AsyncMock()),
        )

    async def test_choice_menu_pages_more_than_25_items_and_renders_selection(self):
        from cogs.utils.menus import ChoiceView
        render = MagicMock(return_value=discord.Embed(title="Selected"))
        view = ChoiceView(456, [(f"Item {i}", i) for i in range(60)], render)
        self.assertEqual(len(view.selector.options), 25)
        self.assertFalse(await view.interaction_check(self.interaction(999)))
        await view.next.callback(self.interaction())
        self.assertEqual(view.page, 1)
        self.assertEqual(view.selector.options[0].label, "Item 25")
        view.selector._values = ["27"]
        interaction = self.interaction()
        await view.selector.callback(interaction)
        render.assert_called_once_with(27)
        self.assertEqual(interaction.edit_original_response.await_args.kwargs["embed"].title, "Selected")
        view.message = SimpleNamespace(edit=AsyncMock())
        await view.on_timeout()
        self.assertTrue(all(item.disabled for item in view.children))
        view.stop()

    async def test_selected_guide_can_open_all_content_pages(self):
        from cogs.utils.menus import ChoiceView
        pages = [discord.Embed(title="One"), discord.Embed(title="Two")]
        view = ChoiceView(456, [("Guide", "guide")], lambda value: pages)
        view.selector._values = ["0"]
        interaction = self.interaction()
        await view.selector.callback(interaction)
        new_view = interaction.followup.send.await_args.kwargs["view"]
        self.assertEqual(len(new_view.embeds), 2)
        self.assertEqual(new_view.author_id, 456)
        new_view.stop()
        view.stop()

    async def test_calculator_buttons_share_expression_evaluation(self):
        from cogs.bot.calculator import CalculatorView
        author = SimpleNamespace(id=456, display_name="Tester", colour=discord.Colour.blue())
        view = CalculatorView(author)
        for label in ("7", "+", "3", "="):
            await view.press(self.interaction(), label)
        self.assertEqual(float(view.expression), 10)
        await view.press(self.interaction(), "Clear")
        await view.press(self.interaction(), ":")
        self.assertEqual(view.expression, "")
        for label in ("1", ":", "0", "="):
            await view.press(self.interaction(), label)
        self.assertEqual(view.display, "Invalid calculation")
        await view.press(self.interaction(), "Exit")
        self.assertTrue(view.is_finished())
        self.assertTrue(all(item.disabled for item in view.children))


    async def test_long_text_is_paginated_without_losing_content(self):
        from cogs.utils.menus import text_pages
        text = "story " * 1500
        pages = text_pages("Story", text, discord.Colour.blue())
        self.assertTrue(all(len(page.description) <= 4000 for page in pages))
        self.assertEqual("".join(page.description for page in pages), text)

