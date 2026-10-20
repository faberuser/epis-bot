"""Publish additional slash paths while sharing hybrid command implementations."""

from copy import copy

from discord import app_commands
from discord.ext import commands


class RouteCog(commands.Cog):
    def cog_unload(self):
        for name in getattr(self, "application_routes", []):
            self.client.tree.remove_command(name)


def add_routes(bot, cog, routes):
    roots = {}
    cog.application_routes = []
    for path, source_name in routes.items():
        source = bot.get_command(source_name)
        if not isinstance(source, commands.HybridCommand):
            raise TypeError(f"{source_name} must be a hybrid command")
        command = copy(source.app_command)
        parts = path.split()
        command.name = parts[-1]
        if len(parts) == 1:
            bot.tree.add_command(command)
            roots[parts[0]] = command
            cog.application_routes.append(parts[0])
        else:
            group = roots.get(parts[0])
            if group is None:
                group = app_commands.Group(name=parts[0], description=f"{parts[0].title()} commands")
                bot.tree.add_command(group)
                roots[parts[0]] = group
                cog.application_routes.append(parts[0])
            group.add_command(command)
