from typing import Any

from discord.ext import commands

from nerdlandbot.translations.Translations import get_text as translate
from nerdlandbot.helpers.TranslationHelper import get_culture_from_context as culture
from nerdlandbot.helpers.log import warn as log_warn


class OnCommandError(commands.Cog, name="on_command_error"):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @commands.Cog.listener(name="on_command_error")
    async def on_command_error(self, ctx: commands.Context, error: Any):
        """
        Handles any errors thrown by the commands.
        :param ctx: The current context. (discord.ext.commands.Context)
        :param error: The current error. (Any)
        """
        
        # Notify user for MissingRequiredArgument errors
        if isinstance(error, commands.MissingRequiredArgument):
            command_name = ctx.message.content.split(" ")[0]
            msg = translate("err_missing_parameter", await culture(ctx)).format(command_name, error.param.name)
            return await ctx.send(msg)
        elif isinstance(error, commands.NoPrivateMessage):
            return
        else:
            # Log the warning
            log_warn(error)

        # Notify user with general error
        msg = translate("err_unrecognized_command", await culture(ctx))
        await ctx.send(msg)


def setup(bot):
    bot.add_cog(OnCommandError(bot))
