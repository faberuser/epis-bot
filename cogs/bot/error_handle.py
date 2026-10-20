import logging
from discord.ext import commands


class Error(commands.Cog):
    @commands.Cog.listener()
    async def on_command_error(self, ctx, error):
        if isinstance(error, commands.CommandNotFound):
            return
        if isinstance(error, commands.CommandOnCooldown):
            message = f"Try again in {error.retry_after:.1f} seconds."
        elif isinstance(error, commands.UserInputError):
            message = str(error)
        elif isinstance(error, commands.CheckFailure):
            message = "You don't have permission to use this command here."
        else:
            logging.getLogger(__name__).error("Command failed", exc_info=(type(error), error, error.__traceback__))
            message = "This command failed. Please try again later."
        await ctx.send(message, ephemeral=True)


async def setup(client):
    await client.add_cog(Error())
