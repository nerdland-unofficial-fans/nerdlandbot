from typing import Any

from discord.ext import commands


from nerdlandbot.translations.Translations import get_text as translate
from nerdlandbot.helpers.TranslationHelper import get_culture_from_context as culture
from nerdlandbot.helpers.TranslationHelper import get_culture_from_id as culture_id
from nerdlandbot.helpers.log import warn as log_warn
from nerdlandbot.helpers.constants import DISCORD_SERVER_ID


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
        #Notify user when using a command in DM that is not meant for DM
        if isinstance(error, commands.NoPrivateMessage):
            msg = translate("err_command_no_DM", await culture_id(int(DISCORD_SERVER_ID)))
            return await ctx.send(msg)
        # Notify user for MissingRequiredArgument errors
        elif isinstance(error, commands.MissingRequiredArgument):
            command_name = ctx.message.content.split(" ")[0]
            msg = translate("err_missing_parameter", await culture(ctx)).format(command_name, error.param.name)
            return await ctx.send(msg)

        else:
            # Log the warning
            log_warn(error)

        # Notify user with general error
        msg = translate("err_unrecognized_command", await culture(ctx))
        await ctx.send(msg)


def setup(bot):
    bot.add_cog(OnCommandError(bot))
